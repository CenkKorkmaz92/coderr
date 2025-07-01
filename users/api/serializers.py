"""Serializers for users app"""

from django.contrib.auth.models import User
from rest_framework import serializers
from ..models import UserProfile
from django.contrib.auth import authenticate


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile data.
    
    Includes fields for username and email from the related User model.
    Username is read-only, but email can be updated.
    """
    
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email')
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel',
            'description', 'working_hours', 'type', 'email', 'created_at'
        ]
    
    def update(self, instance, validated_data):
        """Update user profile and related user fields like email."""
        user_data = validated_data.pop('user', {})
        
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class RegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    
    Handles user account creation along with profile setup.
    Validates password confirmation and uniqueness constraints.
    """
    
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=UserProfile.USER_TYPE_CHOICES)

    def validate(self, data):
        """Validate registration data including password confirmation and uniqueness."""
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError("Passwords do not match.")
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists.")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists.")
        return data

    def create(self, validated_data):
        """Create a new user and associated profile."""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        profile = UserProfile.objects.create(
            user=user,
            type=validated_data['type']
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user authentication.
    
    Validates user credentials and returns the authenticated user.
    """
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate user credentials."""
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        data['user'] = user
        return data
