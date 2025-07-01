"""Views for user management including registration, login, and profile management."""

# Standard library
# (none in this file)

# Third-party
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from rest_framework.authtoken.models import Token
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

# Local imports
from ..models import UserProfile
from .serializers import RegistrationSerializer, LoginSerializer, UserProfileSerializer

class RegistrationView(APIView):
    """
    Handle user registration and return authentication token.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Create a new user account.
        
        Args:
            request: HTTP request containing user registration data
            
        Returns:
            Response containing token and user details on success,
            validation errors on failure
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    Handle user login and return authentication token.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Authenticate user and return token.
        
        Args:
            request: HTTP request containing login credentials
            
        Returns:
            Response containing token and user details on success,
            validation errors on failure
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileListView(ListAPIView):
    """
    List user profiles with optional filtering by user type.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Get profiles with optional user type filtering.
        
        Returns:
            QuerySet of UserProfile instances
        """
        queryset = UserProfile.objects.select_related('user').all()
        user_type = self.kwargs.get('user_type')
        
        if user_type:
            queryset = queryset.filter(type=user_type)
            
        return queryset

class ProfileView(RetrieveUpdateAPIView):
    """
    Handle user profile retrieval and updates.
    """
    queryset = UserProfile.objects.select_related('user')
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieve user profile by user ID with proper permission checks.
        
        Returns:
            UserProfile instance for the specified user
            
        Raises:
            Http404: If profile doesn't exist
            PermissionDenied: If user doesn't own the profile (for updates)
        """
        pk = self.kwargs['pk']
        try:
            profile = UserProfile.objects.select_related('user').get(user__pk=pk)
        except UserProfile.DoesNotExist:
            from django.http import Http404
            raise Http404("Profile not found")
        
        # Allow read access for all authenticated users
        if self.request.method == 'GET':
            return profile
            
        # For updates (PATCH, PUT), only allow profile owner
        if profile.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only update your own profile")
            
        return profile


class BusinessProfileListView(APIView):
    """
    List business user profiles without pagination.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get list of business profiles as array."""
        queryset = UserProfile.objects.select_related('user').filter(type='business')
        serializer = UserProfileSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerProfileListView(APIView):
    """
    List customer user profiles without pagination.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get list of customer profiles as array."""
        queryset = UserProfile.objects.select_related('user').filter(type='customer')
        serializer = UserProfileSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
