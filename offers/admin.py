"""Admin configuration for offers app."""

from django.contrib import admin
from .models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    """Inline admin for offer details."""
    model = OfferDetail
    extra = 1
    fields = ['title', 'offer_type', 'price', 'delivery_time_in_days', 'revisions']


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Admin interface for Offer model."""
    
    list_display = ['title', 'user', 'min_price', 'min_delivery_time', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'min_price', 'min_delivery_time']
    inlines = [OfferDetailInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'image')
        }),
        ('Computed Fields', {
            'fields': ('min_price', 'min_delivery_time'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """Admin interface for OfferDetail model."""
    
    list_display = ['offer', 'title', 'offer_type', 'price', 'delivery_time_in_days']
    list_filter = ['offer_type', 'delivery_time_in_days']
    search_fields = ['offer__title', 'title']
