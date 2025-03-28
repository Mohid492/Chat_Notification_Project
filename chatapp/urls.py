from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('messages', views.ChatViewSet, basename='chat')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.chat_view, name='chat'),
]