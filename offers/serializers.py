"""Serializers for offers and offer details."""

# Standard library
# (none in this file)

# Third-party
from django.contrib.auth.models import User
from rest_framework import serializers

# Local imports
from .models import Offer, OfferDetail
from users.models import UserProfile


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for offer detail data.
    
    Represents specific pricing tiers (basic, standard, premium) for offers.
    """
    
    class Meta:
        model = OfferDetail
        fields = [
            'id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type'
        ]
        read_only_fields = ['id']
    
    def validate_delivery_time_in_days(self, value):
        """Validate delivery time is a positive integer."""
        if not isinstance(value, int) or value <= 0:
            raise serializers.ValidationError("Delivery time must be a positive integer.")
        return value
    
    def validate_price(self, value):
        """Validate price is a positive number."""
        if value <= 0:
            raise serializers.ValidationError("Price must be positive.")
        return value
    
    def validate_revisions(self, value):
        """Validate revisions is a non-negative integer."""
        if not isinstance(value, int) or value < 0:
            raise serializers.ValidationError("Revisions must be a non-negative integer.")
        return value


class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer for offer data with nested offer details.
    
    Includes computed fields for minimum price and delivery time,
    as well as user details for display purposes.
    """
    
    details = OfferDetailSerializer(many=True)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time', 'user_details'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'min_price', 'min_delivery_time', 'user_details', 'user']

    def get_user_details(self, obj):
        """Get user profile details for display purposes."""
        try:
            profile = UserProfile.objects.get(user=obj.user)
            return {
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'username': obj.user.username
            }
        except UserProfile.DoesNotExist:
            return None

    def create(self, validated_data):
        """Create an offer with its associated offer details."""
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def validate_details(self, value):
        """Validate that exactly 3 offer details are provided."""
        if len(value) != 3:
            raise serializers.ValidationError("Exactly 3 offer details (basic, standard, premium) are required.")
        
        # Check for required offer types
        offer_types = [detail.get('offer_type') for detail in value]
        required_types = ['basic', 'standard', 'premium']
        
        for required_type in required_types:
            if required_type not in offer_types:
                raise serializers.ValidationError(f"Missing required offer type: {required_type}")
        
        return value

    def to_internal_value(self, data):
        """Handle multipart form data with JSON strings for nested fields."""
        import json
        
        # Handle QueryDict from multipart form data
        if hasattr(data, 'getlist'):
            # Convert QueryDict to regular dict
            data_dict = {}
            for key in data.keys():
                values = data.getlist(key)
                data_dict[key] = values[0] if len(values) == 1 else values
            data = data_dict
        
        # If details is a string (from multipart form data), parse it as JSON
        if isinstance(data.get('details'), str):
            try:
                data['details'] = json.loads(data['details'])
            except (json.JSONDecodeError, ValueError) as e:
                raise serializers.ValidationError({'details': f'Invalid JSON format: {str(e)}'})
        
        return super().to_internal_value(data)

    def update(self, instance, validated_data):
        """Update an offer and its associated offer details."""
        details_data = validated_data.pop('details', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if details_data is not None:
            for detail_data in details_data:
                detail_id = detail_data.get('id', None)
                if detail_id:
                    detail = OfferDetail.objects.get(id=detail_id, offer=instance)
                    for attr, value in detail_data.items():
                        if attr != 'id':
                            setattr(detail, attr, value)
                    detail.save()
                else:
                    OfferDetail.objects.create(offer=instance, **detail_data)
        return instance
