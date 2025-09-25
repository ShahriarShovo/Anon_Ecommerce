from django.contrib import admin
from .models import Conversation, Message, Participant

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'assigned_to', 'status', 'created_at', 'last_message_at']
    list_filter = ['status', 'created_at', 'assigned_to']
    search_fields = ['customer__email', 'customer__full_name', 'assigned_to__email']
    readonly_fields = ['created_at', 'updated_at', 'last_message_at']
    raw_id_fields = ['customer', 'assigned_to']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'message_type', 'created_at', 'delivery_status']
    list_filter = ['message_type', 'delivery_status', 'created_at']
    search_fields = ['content', 'sender__email', 'conversation__id']
    readonly_fields = ['created_at', 'updated_at', 'read_at']
    raw_id_fields = ['conversation', 'sender']

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'user', 'is_online', 'is_active', 'last_seen_at']
    list_filter = ['is_online', 'is_active', 'last_seen_at']
    search_fields = ['user__email', 'conversation__id']
    readonly_fields = ['joined_at', 'last_seen_at']
    raw_id_fields = ['conversation', 'user']
