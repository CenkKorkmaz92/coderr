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
    """
    Handle listing and creating orders with user-specific filtering.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return orders where the user is either customer or business user.
        
        Returns:
            QuerySet of orders involving the authenticated user
        """
        user = self.request.user
        return Order.objects.filter(
            models.Q(customer_user=user) | models.Q(business_user=user)
        )

    def perform_create(self, serializer):
        """
        Create an order from an offer detail with validation.
        
        Args:
            serializer: The validated order serializer
            
        Raises:
            ValidationError: If offer_detail_id is missing or invalid
            PermissionDenied: If user is not a customer
        """
        try:
            user_profile = self.request.user.profile
        except AttributeError:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('User profile not found.')
            
        if user_profile.type != 'customer':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only customers can create orders.')
        
        offer_detail_id = self.request.data.get('offer_detail_id')
        if not offer_detail_id:
            raise serializers.ValidationError({'offer_detail_id': 'This field is required.'})
        try:
            offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        except OfferDetail.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('OfferDetail not found.')
            
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
    """
    Handle retrieving, updating, and deleting individual orders with permission checks.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        """
        Update order status. Only business users can update orders.
        
        Args:
            request: HTTP request containing update data
            
        Returns:
            Response with updated order data or 403 if unauthorized
        """
        order = self.get_object()
        if request.user != order.business_user:
            return Response({'detail': 'Only the business user can update the order status.'}, status=status.HTTP_403_FORBIDDEN)
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Delete order. Allowed for customers, business users, or admin.
        
        Args:
            request: HTTP request for deletion
            
        Returns:
            Response with 204 status on success or 403 if unauthorized
        """
        order = self.get_object()
        if request.user == order.customer_user or request.user == order.business_user or request.user.is_staff:
            return self.destroy(request, *args, **kwargs)
        return Response({'detail': 'You can only delete orders you are involved in.'}, status=status.HTTP_403_FORBIDDEN)

    def get_object(self):
        """
        Get order with proper error handling.
        
        Returns:
            Order instance
            
        Raises:
            Http404: If order doesn't exist
        """
        try:
            return Order.objects.get(pk=self.kwargs['pk'])
        except Order.DoesNotExist:
            from django.http import Http404
            raise Http404("Order not found")

class OrderCountView(APIView):
    """
    Get count of in-progress orders for a business user.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, business_user_id):
        """
        Return count of in-progress orders for specified business user.
        
        Args:
            request: HTTP request
            business_user_id: ID of the business user
            
        Returns:
            Response containing order count
            
        Raises:
            Http404: If business user doesn't exist
        """
        try:
            User.objects.get(id=business_user_id)
        except User.DoesNotExist:
            from django.http import Http404
            raise Http404("Business user not found")
            
        count = Order.objects.filter(business_user_id=business_user_id, status='in_progress').count()
        return Response({'order_count': count})

class CompletedOrderCountView(APIView):
    """
    Get count of completed orders for a business user.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, business_user_id):
        """
        Return count of completed orders for specified business user.
        
        Args:
            request: HTTP request
            business_user_id: ID of the business user
            
        Returns:
            Response containing completed order count
            
        Raises:
            Http404: If business user doesn't exist
        """
        try:
            User.objects.get(id=business_user_id)
        except User.DoesNotExist:
            from django.http import Http404
            raise Http404("Business user not found")
            
        count = Order.objects.filter(business_user_id=business_user_id, status='completed').count()
        return Response({'completed_order_count': count})
