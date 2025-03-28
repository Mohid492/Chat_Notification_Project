import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

class NotificationConsumer(AsyncWebsocketConsumer):
    # Initialize group_name to None in __init__
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = None
    
    async def connect(self):
        # Check if user is authenticated
        if isinstance(self.scope['user'], AnonymousUser):
            # Reject the connection if user is not authenticated
            await self.close(code=4003)
            return
            
        self.group_name = f"user_{self.scope['user'].id}"

        # Join user notification group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        
        # Send a welcome message (optional, for testing)
        await self.send(text_data=json.dumps({
            'notification': {'message': 'Connected to notification service!'}
        }))

    async def disconnect(self, close_code):
        # Only try to leave group if we joined one
        if self.group_name:
            # Leave user notification group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        notification = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'notification': notification
        }))