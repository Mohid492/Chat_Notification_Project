from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

class ConnectionRequest(models.Model):
    from_user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="from_user")
    to_user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="to_user")
    status=models.BooleanField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

class Connections(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    connected_user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="connected_user")

class Likes(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    liked_user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="liked_user")