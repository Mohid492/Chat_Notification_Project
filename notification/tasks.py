from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def create_notification_task(user_id, message):
    """Celery task to create notification in the background"""
    
    try:
        user = User.objects.get(id=user_id)
        
        # Save notification to database
        notification = Notification.objects.create(
            user=user,
            message=message
        )
        
        # Send real-time notification
        channel_layer = get_channel_layer()
        group_name = f"user_{user.id}"
        
        # Send notification to the user's group
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
                'message': {
                    'id': notification.id,
                    'message': notification.message,
                    'created_at': notification.created_at.isoformat(),
                }
            }
        )
        
        return f"Notification {notification.id} created for user {user.username}"
    
    except User.DoesNotExist:
        return f"User with ID {user_id} does not exist"