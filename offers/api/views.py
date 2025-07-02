"""Views for offer management including CRUD operations and filtering."""
from django.shortcuts import render
from django.db.models import Min
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailSerializer

class OfferListCreateView(generics.ListCreateAPIView):
    """
    Handle listing and creating offers with search and filtering capabilities.
    """
    queryset = Offer.objects.all().prefetch_related('details')
    serializer_class = OfferSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'created_at']
    filterset_fields = ['user']

    def get_queryset(self):
        """
        Filter offers based on min_price and max_delivery_time query parameters.
        """
        queryset = super().get_queryset()
        
        min_price = self.request.query_params.get('min_price')
        if min_price:
            try:
                min_price = float(min_price)
                queryset = queryset.filter(details__price__gte=min_price).distinct()
            except (ValueError, TypeError):
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'min_price': 'Must be a valid number'})
        
        max_delivery_time = self.request.query_params.get('max_delivery_time')
        if max_delivery_time:
            try:
                max_delivery_time = int(max_delivery_time)
                queryset = queryset.filter(details__delivery_time_in_days__lte=max_delivery_time).distinct()
            except (ValueError, TypeError):
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'max_delivery_time': 'Must be a valid integer'})
        
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Handle listing offers with custom page_size support.
        """
        page_size = request.query_params.get('page_size')
        
        if page_size:
            try:
                page_size = int(page_size)
                
                from rest_framework.pagination import PageNumberPagination
                paginator = PageNumberPagination()
                paginator.page_size = page_size
                
                queryset = self.filter_queryset(self.get_queryset())
                page = paginator.paginate_queryset(queryset, request, view=self)
                
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return paginator.get_paginated_response(serializer.data)
            except (ValueError, TypeError):
                pass
        
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        """
        Allow public access for GET requests, require authentication for POST.
        """
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_authenticators(self):
        """
        Skip authentication for GET requests to allow public access.
        """
        if self.request.method == 'GET':
            return []
        return super().get_authenticators()

    def perform_create(self, serializer):
        """
        Save the offer with the current user as the owner.
        
        Args:
            serializer: The validated offer serializer
            
        Raises:
            PermissionDenied: If user is not a business user
        """
        try:
            user_profile = self.request.user.profile
        except AttributeError:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('User profile not found.')
            
        if user_profile.type != 'business':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only business users can create offers.')
        serializer.save(user=self.request.user)

class OfferRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handle retrieving, updating, and deleting individual offers.
    """
    queryset = Offer.objects.all().prefetch_related('details')
    serializer_class = OfferSerializer
    
    def get_permissions(self):
        """
        Allow public access for GET requests, require authentication for POST/PATCH/DELETE.
        """
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        """
        Get offer with proper permission checks for updates/deletes.
        
        Returns:
            Offer instance
            
        Raises:
            Http404: If offer doesn't exist
            PermissionDenied: If user doesn't own the offer (for updates/deletes)
        """
        try:
            offer = Offer.objects.prefetch_related('details').get(pk=self.kwargs['pk'])
        except Offer.DoesNotExist:
            from django.http import Http404
            raise Http404("Offer not found")
        
        if self.request.method == 'GET':
            return offer
            
        if offer.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only modify your own offers")
            
        return offer

    def perform_update(self, serializer):
        """
        Save the updated offer with the current user as the owner.
        
        Args:
            serializer: The validated offer serializer
        """
        serializer.save(user=self.request.user)

class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """
    Handle retrieving individual offer details.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [permissions.AllowAny]

class OfferDetailListCreateView(generics.ListCreateAPIView):
    """
    Handle listing and creating offer details with ownership validation.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """
        Create offer detail after validating user ownership of the parent offer.
        
        Args:
            serializer: The validated offer detail serializer
            
        Raises:
            PermissionDenied: If user doesn't own the parent offer
        """
        offer = serializer.validated_data['offer']
        if offer.user != self.request.user:
            raise permissions.PermissionDenied('You can only create details for your own offers.')
        serializer.save()
