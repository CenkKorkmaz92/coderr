"""Django app configuration for offers application."""

from django.apps import AppConfig


class OffersConfig(AppConfig):
    """Configuration for the offers application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'offers'
