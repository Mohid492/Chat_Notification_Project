from .tasks import create_notification_task

def create_notification(user, message):
    """Queue notification creation in Celery"""
    # Queue the task to run in the background
    create_notification_task.delay(user.id, message)


# services.py:

# Handles backend logic for creating notifications.
# It queues tasks (using Celery) to create notifications in the background.
# It is not real-time; it focuses on processing notifications asynchronously.


# consumers.py:

# Handles real-time communication using WebSockets.
# It sends notifications to connected users instantly via WebSocket connections.
# It is real-time and interacts with the WebSocket protocol.