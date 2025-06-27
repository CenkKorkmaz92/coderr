"""Admin configuration for users app."""

from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model."""
    
    list_display = ['user', 'type', 'first_name', 'last_name', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['user__username', 'user__email', 'first_name', 'last_name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'type')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'description', 'file')
        }),
        ('Contact Information', {
            'fields': ('tel', 'location')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
