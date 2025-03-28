import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.db import models
from asgiref.sync import sync_to_async
from .tasks import save_chat_message_task
from .models import Chat

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Check if user is authenticated
        if isinstance(self.scope['user'], AnonymousUser):
            await self.close(code=4003)
            return

        # Get the other user's ID from the URL
        self.user_id = self.scope['user'].id
        self.other_user_id = int(self.scope['url_route']['kwargs']['user_id'])
        
        # Create a unique room name (sorted by ID to ensure consistency)
        user_ids = sorted([self.user_id, self.other_user_id])
        self.room_name = f"chat_{user_ids[0]}_{user_ids[1]}"
        
        # Join the room
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send chat history on connect
        chat_history = await self.get_chat_history()
        if chat_history:
            await self.send(text_data=json.dumps({
                'type': 'chat_history',
                'messages': chat_history
            }))
            
            # Mark messages as read (in background)
            await self.mark_messages_as_read()

    async def disconnect(self, close_code):
        # Leave the room group
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(
                self.room_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        # Queue message saving in Celery (runs in background)
        # Note: We don't await this since it uses a normal function not an async one
        await sync_to_async(save_chat_message_task.delay)(
            self.user_id, 
            self.other_user_id, 
            message
        )
        
        # We don't need to broadcast the message here as the Celery task will do it
        # This makes the UI feel more responsive while still ensuring data consistency

    async def chat_message(self, event):
        # This method is called when a message is received from the group
        # Send message to WebSocket with all needed metadata
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp'],
            'username': event['username']
        }))
    
    @database_sync_to_async
    def get_chat_history(self):
        # Get last 50 messages between these users
        messages = Chat.objects.filter(
            (models.Q(sender_id=self.user_id, receiver_id=self.other_user_id) | 
             models.Q(sender_id=self.other_user_id, receiver_id=self.user_id))
        ).order_by('-created_at')[:50]
        
        # Reverse to get oldest message first
        messages = reversed(list(messages))
        
        history = []
        for msg in messages:
            history.append({
                'message': msg.message,
                'sender_id': msg.sender_id,
                'message_id': msg.id,
                'timestamp': msg.created_at.isoformat(),
                'username': msg.sender.username,
                'read': msg.read
            })
        return history
    
    @database_sync_to_async
    def mark_messages_as_read(self):
        # Mark all messages from the other user to the current user as read
        Chat.objects.filter(
            sender_id=self.other_user_id,
            receiver_id=self.user_id,
            read=False
        ).update(read=True)