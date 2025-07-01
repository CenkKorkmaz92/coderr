from django.shortcuts import render
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from ..models import Review
from .serializers import ReviewSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q


class ReviewListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating reviews.
    
    Supports filtering by business_user_id and reviewer_id query parameters.
    Only customers can create reviews, and each customer can only review
    a business user once.
    """
    
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated_at', 'rating']

    def get_queryset(self):
        """Get reviews with optional filtering by business user or reviewer."""
        queryset = Review.objects.all()
        business_user_id = self.request.query_params.get('business_user_id')
        reviewer_id = self.request.query_params.get('reviewer_id')
        
        if business_user_id:
            try:
                business_user_id = int(business_user_id)
                queryset = queryset.filter(business_user_id=business_user_id)
            except (ValueError, TypeError):
                pass
                
        if reviewer_id:
            try:
                reviewer_id = int(reviewer_id)
                queryset = queryset.filter(reviewer_id=reviewer_id)
            except (ValueError, TypeError):
                pass
                
        return queryset.order_by('-created_at')

    def get_permissions(self):
        """
        Require authentication for all operations.
        """
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        """
        Return a simple array of reviews, not a paginated response.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Create a review with validation for customer type and uniqueness."""
        reviewer = self.request.user
        business_user = serializer.validated_data['business_user']
        
        try:
            reviewer_profile = reviewer.profile
        except AttributeError:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('User profile not found.')
            
        if reviewer_profile.type != 'customer':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only customers can create reviews.')
        if Review.objects.filter(business_user=business_user, reviewer=reviewer).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You have already reviewed this business user.')
        serializer.save(reviewer=reviewer)


class ReviewRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting reviews.
    
    Only the original reviewer can update or delete their review.
    """
    
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Get review with proper error handling.
        
        Returns:
            Review instance
            
        Raises:
            Review.DoesNotExist: If review doesn't exist
        """
        return Review.objects.get(pk=self.kwargs['pk'])

    def patch(self, request, *args, **kwargs):
        """Update review - only allowed for the original reviewer."""
        review = self.get_object()
        if request.user != review.reviewer:
            return Response({'detail': 'Only the reviewer can update this review.'}, status=status.HTTP_403_FORBIDDEN)
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Delete review - only allowed for the original reviewer."""
        try:
            review = self.get_object()
        except Review.DoesNotExist:
            return Response({'detail': 'Review with given id does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != review.reviewer:
            return Response({'detail': 'Only the reviewer can delete this review.'}, status=status.HTTP_403_FORBIDDEN)
        
        review.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
