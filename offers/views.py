"""Views for offer management including CRUD operations and filtering."""

# Standard library
# (none in this file)

# Third-party
from django.shortcuts import render
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
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
    permission_classes = [permissions.AllowAny]  # Public access for browsing offers
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    filterset_fields = ['user', 'details__price', 'details__delivery_time_in_days']

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
        # Check if user has a profile
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
    permission_classes = [IsAuthenticated]  # Require auth for all operations

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
        
        # Allow read access for all users
        if self.request.method == 'GET':
            return offer
            
        # For updates/deletes, only allow offer owner
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
    permission_classes = [permissions.IsAuthenticated]  # Require authentication

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
