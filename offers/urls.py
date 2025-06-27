# URLs for offers app
from django.urls import path
from .views import OfferListCreateView, OfferRetrieveUpdateDestroyView, OfferDetailRetrieveView, OfferDetailListCreateView

urlpatterns = [
    path('offers/', OfferListCreateView.as_view(), name='offer-list-create'),
    path('offers/<int:pk>/', OfferRetrieveUpdateDestroyView.as_view(), name='offer-detail'),
    path('offerdetails/', OfferDetailListCreateView.as_view(), name='offerdetail-list-create'),
    path('offerdetails/<int:pk>/', OfferDetailRetrieveView.as_view(), name='offerdetail-detail'),
]
