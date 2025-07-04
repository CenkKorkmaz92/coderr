"""Django app configuration for core application."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for the core application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
