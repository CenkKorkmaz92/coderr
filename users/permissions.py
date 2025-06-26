from rest_framework import permissions

class IsBusinessUser(permissions.BasePermission):
    """Allow only business users to create offers."""
    def has_permission(self, request, view):
        if request.method == 'POST':
            return hasattr(request.user, 'profile') and getattr(request.user.profile, 'type', None) == 'business'
        return True

class IsCustomerUser(permissions.BasePermission):
    """Allow only customer users to create orders."""
    def has_permission(self, request, view):
        if request.method == 'POST':
            return hasattr(request.user, 'profile') and getattr(request.user.profile, 'type', None) == 'customer'
        return True

class IsProfileOwnerOrReadOnly(permissions.BasePermission):
    """Allow only the owner of the profile to update it."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
