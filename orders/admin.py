"""Admin configuration for orders app."""

from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order model."""
    
    list_display = ['id', 'customer_user', 'business_user', 'offer_detail', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_user__username', 'business_user__username', 'offer_detail__offer__title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('customer_user', 'business_user', 'offer_detail', 'status')
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
