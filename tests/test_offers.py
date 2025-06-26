from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import UserProfile
from offers.models import Offer, OfferDetail
from rest_framework import status

class OfferTests(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(username='biz', password='pass', email='biz@mail.de')
        UserProfile.objects.create(user=self.business_user, type='business')
        self.customer_user = User.objects.create_user(username='cust', password='pass', email='cust@mail.de')
        UserProfile.objects.create(user=self.customer_user, type='customer')
        self.offer_data = {
            "title": "Test Offer",
            "image": None,
            "description": "Test Desc",
            "details": [
                {"title": "Basic", "revisions": 1, "delivery_time_in_days": 2, "price": 10, "features": ["A"], "offer_type": "basic"},
                {"title": "Standard", "revisions": 2, "delivery_time_in_days": 3, "price": 20, "features": ["B"], "offer_type": "standard"},
                {"title": "Premium", "revisions": 3, "delivery_time_in_days": 4, "price": 30, "features": ["C"], "offer_type": "premium"}
            ]
        }

    def test_create_offer_business_user(self):
        self.client.force_authenticate(self.business_user)
        url = reverse('offer-list-create')
        response = self.client.post(url, self.offer_data, format='json')
        print('OFFER CREATE RESPONSE:', response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferDetail.objects.count(), 3)

    def test_create_offer_customer_forbidden(self):
        self.client.force_authenticate(self.customer_user)
        url = reverse('offer-list-create')
        response = self.client.post(url, self.offer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_offers(self):
        Offer.objects.create(user=self.business_user, title="O1", description="D1")
        url = reverse('offer-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offer_detail(self):
        offer = Offer.objects.create(user=self.business_user, title="O1", description="D1")
        detail = OfferDetail.objects.create(offer=offer, title="Basic", revisions=1, delivery_time_in_days=2, price=10, features=["A"], offer_type="basic")
        url = reverse('offerdetail-detail', args=[detail.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], detail.id)

    def test_update_offer(self):
        self.client.force_authenticate(self.business_user)
        offer = Offer.objects.create(user=self.business_user, title="O1", description="D1")
        url = reverse('offer-detail', args=[offer.id])
        response = self.client.patch(url, {"title": "Updated"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        offer.refresh_from_db()
        self.assertEqual(offer.title, "Updated")

    def test_delete_offer(self):
        self.client.force_authenticate(self.business_user)
        offer = Offer.objects.create(user=self.business_user, title="O1", description="D1")
        url = reverse('offer-detail', args=[offer.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(id=offer.id).exists())

    def test_offer_not_found(self):
        url = reverse('offer-detail', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
