"""Views for order management."""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from offers.models import OfferDetail
from ..models import Order
from .serializers import OrderSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    """
    Handle listing and creating orders.
    
    GET: Returns an array of orders for the authenticated user (filtered by customer_user).
    POST: Creates a new order for the authenticated user.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return orders for the authenticated user as customer.
        """
        return Order.objects.filter(customer_user=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        """
        Return a simple array of orders, not a paginated response.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Create a new order by copying data from the selected offer detail.
        Only customer users can create orders.
        """
        try:
            user_profile = self.request.user.profile
        except AttributeError:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('User profile not found.')
            
        if user_profile.type != 'customer':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only customer users can create orders.')
            
        offer_detail_id = self.request.data.get('offer_detail_id')
        offer_detail = get_object_or_404(OfferDetail, id=offer_detail_id)
        
        serializer.save(
            customer_user=self.request.user,
            business_user=offer_detail.offer.user,
            offer_detail=offer_detail,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type
        )


class OrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handle retrieving, updating, and deleting individual orders.
    Only allows customers to access their own orders.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return orders for the authenticated user as customer.
        """
        return Order.objects.filter(customer_user=self.request.user)


class OrderCountView(APIView):
    """
    Return the total count of orders for a specific business user.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, business_user_id):
        """Get order count for business user."""
        count = Order.objects.filter(business_user_id=business_user_id).count()
        return Response({'count': count})


class CompletedOrderCountView(APIView):
    """
    Return the count of completed orders for a specific business user.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, business_user_id):
        """Get completed order count for business user."""
        count = Order.objects.filter(
            business_user_id=business_user_id, 
            status='completed'
        ).count()
        return Response({'count': count})
