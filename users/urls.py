from django.urls import path
from .api.views import (
    RegistrationView, LoginView, ProfileView, ProfileListView,
    BusinessProfileListView, CustomerProfileListView
)

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileListView.as_view(), name='profile-list'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile-detail'),
    path('profiles/business/', BusinessProfileListView.as_view(), name='business-profiles'),
    path('profiles/customer/', CustomerProfileListView.as_view(), name='customer-profiles'),
]
