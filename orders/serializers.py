# Serializers for orders app

from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    offer_detail = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'offer_detail', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'offer_detail']
