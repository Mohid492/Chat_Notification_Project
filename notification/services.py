from .tasks import create_notification_task

def create_notification(user, message):
    """Queue notification creation in Celery"""
    # Queue the task to run in the background
    create_notification_task.delay(user.id, message)