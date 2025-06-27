"""Django app configuration for reviews application."""

from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """Configuration for the reviews application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'
