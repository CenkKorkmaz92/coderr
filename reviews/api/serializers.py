"""Serializers for reviews app"""

from rest_framework import serializers
from ..models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for review data.
    
    The reviewer field is automatically set from the authenticated user,
    so it's marked as read-only in the serializer.
    """
    
    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'reviewer']
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if not isinstance(value, int) or value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be an integer between 1 and 5.")
        return value
