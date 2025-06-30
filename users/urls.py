from django.urls import path
from .views import RegistrationView, LoginView, ProfileView, ProfileListView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileListView.as_view(), name='profile-list'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile-detail'),
    path('profiles/business/', ProfileListView.as_view(), {'user_type': 'business'}, name='business-profiles'),
    path('profiles/customer/', ProfileListView.as_view(), {'user_type': 'customer'}, name='customer-profiles'),
]
