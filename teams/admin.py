from django.contrib import admin
from .models import Team, TeamInvitation

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'leader', 'member_count', 'max_members', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'leader__username', 'leader__email')
    readonly_fields = ('created_at', 'member_count')
    
    def member_count(self, obj):
        return obj.member_count()
    member_count.short_description = 'Количество участников'

@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ('team', 'invited_user', 'invited_by', 'is_accepted', 'created_at')
    list_filter = ('is_accepted', 'created_at')
    search_fields = ('team__name', 'invited_user__username', 'invited_by__username')
    readonly_fields = ('created_at',)
