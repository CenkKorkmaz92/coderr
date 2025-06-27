"""Django app configuration for users application."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration for the users application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
