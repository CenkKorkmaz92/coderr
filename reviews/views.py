from django.shortcuts import render
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Review
from .serializers import ReviewSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

# Create your views here.

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated_at', 'rating']

    def get_queryset(self):
        queryset = Review.objects.all()
        business_user_id = self.request.query_params.get('business_user_id')
        reviewer_id = self.request.query_params.get('reviewer_id')
        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)
        return queryset

    def perform_create(self, serializer):
        reviewer = self.request.user
        business_user = serializer.validated_data['business_user']
        if reviewer.profile.type != 'customer':
            raise PermissionDenied('Only customers can create reviews.')
        if Review.objects.filter(business_user=business_user, reviewer=reviewer).exists():
            raise PermissionDenied('You have already reviewed this business user.')
        serializer.save(reviewer=reviewer)

class ReviewRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        review = self.get_object()
        if request.user != review.reviewer:
            return Response({'detail': 'Only the reviewer can update this review.'}, status=status.HTTP_403_FORBIDDEN)
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        review = self.get_object()
        if request.user != review.reviewer:
            return Response({'detail': 'Only the reviewer can delete this review.'}, status=status.HTTP_403_FORBIDDEN)
        return self.destroy(request, *args, **kwargs)
