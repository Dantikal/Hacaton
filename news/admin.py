from django.contrib import admin
from .models import News, Schedule, Task

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published', 'created_at', 'author')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'location', 'is_important')
    list_filter = ('is_important', 'start_time')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'start_time'

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'team', 'status', 'priority', 'deadline', 'created_at')
    list_filter = ('status', 'priority', 'created_at', 'deadline')
    search_fields = ('title', 'description', 'assigned_to__username', 'team__name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
