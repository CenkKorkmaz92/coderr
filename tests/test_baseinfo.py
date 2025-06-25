from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import UserProfile
from offers.models import Offer
from reviews.models import Review
from rest_framework import status

class BaseInfoTests(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(username='biz', password='pass', email='biz@mail.de')
        UserProfile.objects.create(user=self.business_user, type='business')
        self.customer_user = User.objects.create_user(username='cust', password='pass', email='cust@mail.de')
        UserProfile.objects.create(user=self.customer_user, type='customer')
        Offer.objects.create(user=self.business_user, title="O1", description="D1")
        Review.objects.create(business_user=self.business_user, reviewer=self.customer_user, rating=5, description="Great!")

    def test_base_info(self):
        url = reverse('base-info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('review_count', response.data)
        self.assertIn('average_rating', response.data)
        self.assertIn('business_profile_count', response.data)
        self.assertIn('offer_count', response.data)
