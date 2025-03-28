from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']

class ChatSerialzier(serializers.ModelSerializer):
    class Meta:
        model=Chat
        fields=['id','receiver','message','created_at','read']
        read_only_fields=['id','created_at','read']

    def create(self, validated_data):
        sender = self.context['user']
        receiver_id = validated_data.pop('receiver')
        return Chat.objects.create(sender=sender,receiver_id=receiver_id,**validated_data)