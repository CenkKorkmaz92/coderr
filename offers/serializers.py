"""Serializers for offers app"""

from rest_framework import serializers
from .models import Offer, OfferDetail
from users.models import UserProfile
from django.contrib.auth.models import User


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for offer detail data.
    
    Represents specific pricing tiers (basic, standard, premium) for offers.
    """
    
    class Meta:
        model = OfferDetail
        fields = [
            'id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'offer'
        ]
        read_only_fields = ['id']


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
        read_only_fields = ['id', 'created_at', 'updated_at', 'min_price', 'min_delivery_time', 'user_details']

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
