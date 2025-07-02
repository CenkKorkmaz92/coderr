"""Serializers for offers and offer details."""
from django.contrib.auth.models import User
from rest_framework import serializers
from ..models import Offer, OfferDetail
from users.models import UserProfile


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for offer detail data.
    
    Represents specific pricing tiers (basic, standard, premium) for offers.
    """
    url = serializers.HyperlinkedIdentityField(
        view_name='offerdetail-detail',
        lookup_field='pk'
    )
    
    class Meta:
        model = OfferDetail
        fields = [
            'id', 'url', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type'
        ]
        extra_kwargs = {
            'id': {'required': False, 'allow_null': True}
        }
    
    def to_representation(self, instance):
        """Convert the price field to float for output."""
        data = super().to_representation(instance)
        if 'price' in data:
            data['price'] = float(data['price'])
        return data
    
    def to_internal_value(self, data):
        """Process incoming data and preserve id for updates."""
        if 'id' in data:
            validated_data = super().to_internal_value(data)
            validated_data['id'] = data['id']
            return validated_data
        return super().to_internal_value(data)

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
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.IntegerField(read_only=True)
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time', 'user_details'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'min_price', 'min_delivery_time', 'user_details', 'user']
    
    def get_min_price(self, obj):
        """Get minimum price as a float number."""
        min_price = obj.min_price
        return float(min_price) if min_price else None

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
        """
        Validate offer details for creation or partial updates.
        For creation, exactly 3 details are required.
        For updates, can be partial.
        """
        if not self.instance:
            if len(value) != 3:
                raise serializers.ValidationError("Exactly 3 offer details (basic, standard, premium) are required.")
            
            offer_types = [detail.get('offer_type') for detail in value]
            required_types = ['basic', 'standard', 'premium']
            
            for required_type in required_types:
                if required_type not in offer_types:
                    raise serializers.ValidationError(f"Missing required offer type: {required_type}")
        
        return value

    def to_internal_value(self, data):
        """Handle multipart form data with JSON strings for nested fields."""
        import json
        
        if hasattr(data, 'getlist'):
            data_dict = {}
            for key in data.keys():
                values = data.getlist(key)
                data_dict[key] = values[0] if len(values) == 1 else values
            data = data_dict
        
        if isinstance(data.get('details'), str):
            try:
                data['details'] = json.loads(data['details'])
            except (json.JSONDecodeError, ValueError) as e:
                raise serializers.ValidationError({'details': f'Invalid JSON format: {str(e)}'})
        
        return super().to_internal_value(data)

    def update(self, instance, validated_data):
        """Update an offer and its associated offer details (allows partial updates)."""
        details_data = validated_data.pop('details', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if details_data is not None:
            for detail_data in details_data:
                detail_id = detail_data.get('id', None)
                offer_type = detail_data.get('offer_type', None)
                
                if detail_id:
                    try:
                        detail = OfferDetail.objects.get(id=detail_id, offer=instance)
                        for attr, value in detail_data.items():
                            if attr != 'id':
                                setattr(detail, attr, value)
                        detail.save()
                    except OfferDetail.DoesNotExist:
                        raise serializers.ValidationError(f"OfferDetail with id {detail_id} not found")
                elif offer_type:
                    try:
                        detail = OfferDetail.objects.get(offer=instance, offer_type=offer_type)
                        for attr, value in detail_data.items():
                            setattr(detail, attr, value)
                        detail.save()
                    except OfferDetail.DoesNotExist:
                        raise serializers.ValidationError(f"OfferDetail with offer_type '{offer_type}' not found")
                else:
                    raise serializers.ValidationError("Detail updates require either an 'id' or 'offer_type' field to identify the detail to update")
        
        instance.refresh_from_db()
        return instance
