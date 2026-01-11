from django.contrib import admin
from .models import ChatRoom, Message, MessageAttachment

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('team', 'created_at')
    search_fields = ('team__name',)
    readonly_fields = ('created_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('author', 'chat_room', 'content_preview', 'created_at', 'is_edited')
    list_filter = ('created_at', 'is_edited')
    search_fields = ('content', 'author__username', 'chat_room__team__name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Сообщение'

@admin.register(MessageAttachment)
class MessageAttachmentAdmin(admin.ModelAdmin):
    list_display = ('message', 'filename', 'uploaded_at')
    search_fields = ('filename', 'message__content')
    readonly_fields = ('uploaded_at',)
