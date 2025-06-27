from django.utils.deprecation import MiddlewareMixin
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from django.urls import resolve
from django.views.decorators.csrf import csrf_exempt

class StrictTokenAuthMiddleware(MiddlewareMixin):
    """
    Custom middleware for strict token-based authentication.
    
    Exempts API endpoints from CSRF protection and enforces token authentication
    for all API endpoints except login and registration.
    """
    
    def process_request(self, request):
        """
        Process incoming requests to enforce token authentication.
        
        Args:
            request: The HTTP request object
            
        Returns:
            None if authentication passes, JsonResponse with 401 if authentication fails
        """
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        
        allowed_paths = [
            '/api/login/',
            '/api/registration/',
        ]
        if request.path in allowed_paths or request.method == 'OPTIONS':
            return None
            
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Token '):
            token_key = auth_header.split(' ')[1]
            try:
                token = Token.objects.get(key=token_key)
                request.user = token.user
                return None
            except Token.DoesNotExist:
                pass
                
        return JsonResponse({'detail': 'Invalid or missing token.'}, status=401)
