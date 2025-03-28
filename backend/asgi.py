"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()  # Important: Set up Django before importing other modules

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from notification.routing import websocket_urlpatterns as notification_websocket_urlpatterns  # Move this import here, after django.setup()
from chatapp.routing import websocket_urlpatterns as chatapp_websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            notification_websocket_urlpatterns + chatapp_websocket_urlpatterns
        )
    ),
})