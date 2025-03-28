from django.shortcuts import render
from .serializers import *
from .models import *
from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
# Create your views here.
class ConnectionRequestViewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    http_method_names=['get','post','put']

    def get_queryset(self):
        return ConnectionRequest.objects.filter(to_user=self.request.user)

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method=='GET':
            return ViewConnectionRequestSerialzier
        elif self.request.method=='POST':
            return SendConnectionRequestSerializer
        elif self.request.method=='PUT':
            return UpdateConnectionRequestSerializers

    def get_serializer_context(self):
        return {
            "user":self.request.user,
        }    
    
class ConnectionsViewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    http_method_names=['get','delete']
    serializer_class=ConnectionsSerializer
    def get_queryset(self):
        return Connections.objects.filter(user=self.request.user)
        
    def destroy(self, request, *args, **kwargs):
        connection = self.get_object()
        with transaction.atomic():
            # Delete the reciprocal connection (if exists)
            reciprocal = Connections.objects.filter(user=connection.connected_user,
                                                    connected_user=connection.user).first()
            if reciprocal:
                reciprocal.delete()
            # Delete any connection requests between these two users
            ConnectionRequest.objects.filter(
                Q(from_user=connection.user, to_user=connection.connected_user) |
                Q(from_user=connection.connected_user, to_user=connection.user)
            ).delete()
            connection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class LikesViewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    http_method_names=['get','post','delete']
    serializer_class=LikesSerializer
    def get_queryset(self):
        return Likes.objects.filter(liked_user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        like_count = self.get_queryset().count()
        user_id=self.request.user.id
        return Response({"like_count": like_count,"user_id":user_id}, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        return {
            "user":self.request.user
        }
    