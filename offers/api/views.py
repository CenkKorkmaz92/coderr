"""Views for offer management including CRUD operations and filtering."""
from rest_framework import generics, permissions, filters
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
    permission_classes = [permissions.IsAuthenticated]  # Require auth for all operations
    
    def get_object(self):
        """
        Get offer for GET requests with proper error order: 401 -> 404
        For PATCH/DELETE, we handle in the methods directly.
        
        Returns:
            Offer instance
            
        Raises:
            Http404: If offer doesn't exist
        """
        if self.request.method == 'GET':
            # Authentication is handled by DRF permission_classes
            # If we get here, user is authenticated
            try:
                offer = Offer.objects.prefetch_related('details').get(pk=self.kwargs['pk'])
            except Offer.DoesNotExist:
                from django.http import Http404
                raise Http404("Offer not found")
            return offer
        
        # For PATCH/PUT/DELETE, return a dummy object to prevent DRF from automatically
        # checking existence. Our custom update/destroy methods handle the logic properly.
        from django.contrib.auth.models import User
        dummy_user = User(id=999999, username='dummy')
        return Offer(id=999999, user=dummy_user, title='dummy', description='dummy')

    def update(self, request, *args, **kwargs):
        """
        Handle PATCH/PUT with proper status code order: 400 -> 401 -> 403 -> 404
        """
        from rest_framework import status
        
        # First do basic validation that doesn't require the offer instance
        details = request.data.get('details', [])
        for detail in details:
            if 'offer_type' in detail and not detail.get('offer_type'):
                return Response(
                    {'details': 'offer_type is required for each detail'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Check authentication
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication credentials were not provided.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get the offer and handle 403/404 properly
        try:
            offer = Offer.objects.get(pk=self.kwargs['pk'])
        except Offer.DoesNotExist:
            # Standard REST: if resource doesn't exist, return 404
            return Response(
                {'detail': 'Offer not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permission (only if offer exists)
        if offer.user != request.user:
            return Response(
                {'detail': 'You can only modify your own offers'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Now do full validation with serializer (this will catch other validation errors)
        serializer = self.get_serializer(offer, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)
        
        offer.refresh_from_db()
        response_serializer = self.get_serializer(offer)
        return Response(response_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Handle DELETE with proper status code order: 401 -> 403 -> 404
        """
        from rest_framework import status
        
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication credentials were not provided.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            offer = Offer.objects.get(pk=self.kwargs['pk'])
        except Offer.DoesNotExist:
            # Standard REST: if resource doesn't exist, return 404
            return Response(
                {'detail': 'Offer not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permission (only if offer exists)
        if offer.user != request.user:
            return Response(
                {'detail': 'You can only modify your own offers'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        offer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """
        Get offer detail with proper authentication check first, then 404.
        
        Returns:
            OfferDetail instance
            
        Raises:
            Http404: If offer detail doesn't exist
        """
        try:
            offer_detail = OfferDetail.objects.get(pk=self.kwargs['pk'])
        except OfferDetail.DoesNotExist:
            from django.http import Http404
            raise Http404("Offer detail not found")
        
        return offer_detail

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
