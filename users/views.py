from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import RegistrationSerializer, LoginSerializer, UserProfileSerializer
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

class RegistrationView(APIView):
    """
    Handle user registration and return authentication token.
    """
    
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

class ProfileView(RetrieveUpdateAPIView):
    """
    Handle user profile retrieval and updates.
    """
    queryset = UserProfile.objects.select_related('user')
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieve user profile by user ID.
        
        Returns:
            UserProfile instance for the specified user
        """
        pk = self.kwargs['pk']
        return UserProfile.objects.get(user__pk=pk)
