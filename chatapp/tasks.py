from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Chat
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def save_chat_message_task(sender_id, receiver_id, message):
    """Save chat message in the background and notify receiver"""
    try:
        # Get user objects
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        
        # Save message to database
        chat_message = Chat.objects.create(
            sender=sender,
            receiver=receiver,
            message=message
        )
        
        # Send real-time message to appropriate group
        channel_layer = get_channel_layer()
        
        # Create unique group name for this chat (same logic as in consumer)
        user_ids = sorted([sender_id, receiver_id])
        room_name = f"chat_{user_ids[0]}_{user_ids[1]}"
        
        # Send message to the room group
        async_to_sync(channel_layer.group_send)(
            room_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'message_id': chat_message.id,
                'timestamp': chat_message.created_at.isoformat(),
                'username': sender.username
            }
        )
        
        # Also send a notification to the receiver if they're not in the chat
        # Create unique notification group name for receiver
        receiver_group = f"user_{receiver_id}"
        
        from notification.tasks import create_notification_task
        create_notification_task.delay(
            receiver_id, 
            f"New message from {sender.username}: {message[:30]}{'...' if len(message) > 30 else ''}"
        )
        
        return f"Chat message {chat_message.id} saved successfully"
        
    except User.DoesNotExist:
        return "User does not exist"
    except Exception as e:
        return f"Error: {str(e)}"