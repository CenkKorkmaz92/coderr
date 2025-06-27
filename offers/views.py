"""Views for offer management including CRUD operations and filtering."""

# Standard library
# (none in this file)

# Third-party
from django.shortcuts import render
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

# Local imports
from .models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailSerializer

class OfferListCreateView(generics.ListCreateAPIView):
    """
    Handle listing and creating offers with search and filtering capabilities.
    """
    queryset = Offer.objects.all().prefetch_related('details')
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    filterset_fields = ['user', 'details__price', 'details__delivery_time_in_days']

    def perform_create(self, serializer):
        """
        Save the offer with the current user as the owner.
        
        Args:
            serializer: The validated offer serializer
            
        Raises:
            PermissionDenied: If user is not a business user
        """
        if self.request.user.profile.type != 'business':
            raise permissions.PermissionDenied('Only business users can create offers.')
        serializer.save(user=self.request.user)

class OfferRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handle retrieving, updating, and deleting individual offers.
    """
    queryset = Offer.objects.all().prefetch_related('details')
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

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
