from django.contrib import admin
from .models import Likes

# Register the Likes model
@admin.register(Likes)
class LikesAdmin(admin.ModelAdmin):
    list_display = ('user', 'liked_user')  # Fields to display in the admin list view
    search_fields = ('user__username', 'liked_user__username')  # Enable search by user and liked_user