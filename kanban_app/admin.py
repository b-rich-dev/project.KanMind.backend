from django.contrib import admin
from .models import KanbanBoard, Task, Comment


class KanbanBoardAdmin(admin.ModelAdmin):
    """Admin interface for Kanban boards."""
    list_display = ['id', 'title', 'owner', 'created_at']
    list_filter = ['created_at', 'owner']
    search_fields = ['title', 'owner__username', 'owner__email']
    filter_horizontal = ['members']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Board Information', {
            'fields': ('title', 'owner')
        }),
        ('Members', {
            'fields': ('members',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class TaskAdmin(admin.ModelAdmin):
    """Admin interface for tasks."""
    list_display = ['id', 'title', 'board', 'status', 'priority', 'assignee', 'created_by', 'due_date']
    list_filter = ['status', 'priority', 'board', 'created_at']
    search_fields = ['title', 'description', 'board__title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Task Information', {
            'fields': ('board', 'title', 'description')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'due_date')
        }),
        ('Assignment', {
            'fields': ('assignee', 'reviewer_id', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class CommentAdmin(admin.ModelAdmin):
    """Admin interface for comments."""
    list_display = ['id', 'task', 'author', 'created_at', 'content_preview']
    list_filter = ['created_at', 'author']
    search_fields = ['content', 'task__title', 'author__username']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('task', 'author', 'content')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        """Show first 50 characters of content."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


admin.site.register(KanbanBoard, KanbanBoardAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Comment, CommentAdmin)
