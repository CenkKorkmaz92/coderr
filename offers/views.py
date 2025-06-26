from django.shortcuts import render
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from .models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from users.permissions import IsBusinessUser

class OfferListCreateView(generics.ListCreateAPIView):
    queryset = Offer.objects.all().prefetch_related('details')
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsBusinessUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    filterset_fields = ['user', 'details__price', 'details__delivery_time_in_days']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OfferRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all().prefetch_related('details')
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

class OfferDetailRetrieveView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [permissions.AllowAny]
