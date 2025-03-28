from rest_framework import serializers
from .models import *
from django.db import transaction
from django.contrib.auth import get_user_model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']

# Update the import
from notification.services import create_notification

class SendConnectionRequestSerializer(serializers.ModelSerializer):
    to_user_id=serializers.IntegerField(write_only=True)
    class Meta:
        model=ConnectionRequest
        fields = ['id','to_user_id']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        from_user = self.context['user']
        to_user_id = validated_data.pop('to_user_id')  # Get the ID first
        
        # Get the User object
        
        try:
            to_user = User.objects.get(id=to_user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"to_user_id": "User does not exist"})
        
        # Create the connection request with both user objects
        connection_request = ConnectionRequest.objects.create(
            from_user=from_user,
            to_user=to_user
        )
        
        # Queue notification in the background
        message = f"{from_user.username} sent you a connection request"
        create_notification(to_user, message)
        
        return connection_request

class ViewConnectionRequestSerialzier(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    class Meta:
        model = ConnectionRequest  # This should be the model class, not a list
        fields = ['id', 'from_user', 'status']  # This should be a list, not string

class UpdateConnectionRequestSerializers(serializers.ModelSerializer):
    class Meta:
        model=ConnectionRequest
        fields=['id','status']
        read_only_fields=['id']
    
    def update(self, instance, validated_data):
        if validated_data.get('status') is False:
            instance.status = False
            instance.save()
        elif validated_data.get('status') is True:
            with transaction.atomic():
                instance.status = True
                instance.save()
                Connections.objects.create(user=instance.from_user, connected_user=instance.to_user)
                Connections.objects.create(user=instance.to_user, connected_user=instance.from_user)
                message = f"{instance.to_user.username} has accepted your connection request"
                create_notification(instance.from_user, message)
        return instance

class ConnectionsSerializer(serializers.ModelSerializer):
    connected_user=UserSerializer(read_only=True)
    class Meta:
        model=Connections
        fields=['id','connected_user']


class LikesSerializer(serializers.ModelSerializer):
    liked_user_id=serializers.IntegerField(write_only=True)
    class Meta:
        model=Likes
        fields=['id','liked_user_id']

    def create(self, validated_data):
        user=self.context['user']
        liked_user_id=validated_data.pop('liked_user_id')
        liked_user=User.objects.get(id=liked_user_id)
        message=f"{user.username} gave you a like"
        create_notification(liked_user,message)
        return Likes.objects.create(user=user,liked_user=liked_user,**validated_data)