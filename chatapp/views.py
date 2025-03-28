from django.shortcuts import render
from .serializers import *
from .models import *
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatViewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    http_method_names=['get','post','delete']
    serializer_class=ChatSerialzier
    
    def get_queryset(self):
        return Chat.objects.filter(Q(sender=self.request.user)|Q(receiver=self.request.user))
    
    def get_serializer_context(self):
        return {"user": self.request.user}

@login_required
def chat_view(request):
    """View for the chat interface"""
    # Get all users except the current user
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat.html', {
        'users': users
    })