from django.contrib import admin
from .models import Chat
# Register your models here.
@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('sender','receiver','message','created_at','read')  # Fields to display in the admin list view
