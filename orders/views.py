from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
from offers.models import OfferDetail
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import models
from rest_framework import serializers

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            models.Q(customer_user=user) | models.Q(business_user=user)
        )

    def perform_create(self, serializer):
        offer_detail_id = self.request.data.get('offer_detail_id')
        if not offer_detail_id:
            raise serializers.ValidationError({'offer_detail_id': 'This field is required.'})
        try:
            offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError({'offer_detail_id': 'Invalid offer_detail_id.'})
        if self.request.user.profile.type != 'customer':
            raise permissions.PermissionDenied('Only customers can create orders.')
        business_user = offer_detail.offer.user
        order = serializer.save(
            customer_user=self.request.user,
            business_user=business_user,
            offer_detail=offer_detail,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type
        )
        return order

class OrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        if request.user != order.business_user:
            return Response({'detail': 'Only the business user can update the order status.'}, status=status.HTTP_403_FORBIDDEN)
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Only admin/staff can delete
        if not request.user.is_staff:
            return Response({'detail': 'Only admin can delete orders.'}, status=status.HTTP_403_FORBIDDEN)
        return self.destroy(request, *args, **kwargs)

class OrderCountView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, business_user_id):
        count = Order.objects.filter(business_user_id=business_user_id, status='in_progress').count()
        return Response({'order_count': count})

class CompletedOrderCountView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, business_user_id):
        count = Order.objects.filter(business_user_id=business_user_id, status='completed').count()
        return Response({'completed_order_count': count})
