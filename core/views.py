from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from offers.models import Offer
from reviews.models import Review
from users.models import UserProfile
from django.db.models import Avg


class BaseInfoView(APIView):
    """
    API view for retrieving platform statistics.
    
    Provides aggregate information about the platform including
    review counts, average ratings, business profiles, and offers.
    """
    permission_classes = [permissions.AllowAny]  # No permissions required
    
    def get(self, request):
        """Get platform statistics for dashboard display."""
        review_count = Review.objects.count()
        average_rating = Review.objects.all().aggregate(Avg('rating'))['rating__avg'] or 0
        average_rating = round(average_rating, 1)
        business_profile_count = UserProfile.objects.filter(type='business').count()
        offer_count = Offer.objects.count()
        return Response({
            'review_count': review_count,
            'average_rating': average_rating,
            'business_profile_count': business_profile_count,
            'offer_count': offer_count
        }, status=status.HTTP_200_OK)
