from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import UserProfile
from reviews.models import Review
from rest_framework import status

class ReviewTests(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(username='biz', password='pass', email='biz@mail.de')
        UserProfile.objects.create(user=self.business_user, type='business')
        self.customer_user = User.objects.create_user(username='cust', password='pass', email='cust@mail.de')
        UserProfile.objects.create(user=self.customer_user, type='customer')

    def test_create_review_customer(self):
        self.client.force_authenticate(self.customer_user)
        url = reverse('review-list-create')
        data = {"business_user": self.business_user.id, "rating": 5, "description": "Great!"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)

    def test_create_review_business_forbidden(self):
        self.client.force_authenticate(self.business_user)
        url = reverse('review-list-create')
        data = {"business_user": self.business_user.id, "rating": 5, "description": "Great!"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_duplicate_review_forbidden(self):
        Review.objects.create(business_user=self.business_user, reviewer=self.customer_user, rating=5, description="Great!")
        self.client.force_authenticate(self.customer_user)
        url = reverse('review-list-create')
        data = {"business_user": self.business_user.id, "rating": 5, "description": "Great!"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_reviews(self):
        Review.objects.create(business_user=self.business_user, reviewer=self.customer_user, rating=5, description="Great!")
        self.client.force_authenticate(self.customer_user)
        url = reverse('review-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_review(self):
        review = Review.objects.create(business_user=self.business_user, reviewer=self.customer_user, rating=5, description="Great!")
        self.client.force_authenticate(self.customer_user)
        url = reverse('review-detail', args=[review.id])
        response = self.client.patch(url, {"rating": 4, "description": "Updated!"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.description, "Updated!")

    def test_update_review_forbidden(self):
        review = Review.objects.create(business_user=self.business_user, reviewer=self.customer_user, rating=5, description="Great!")
        other_user = User.objects.create_user(username='other', password='pass', email='other@mail.de')
        UserProfile.objects.create(user=other_user, type='customer')
        self.client.force_authenticate(other_user)
        url = reverse('review-detail', args=[review.id])
        response = self.client.patch(url, {"rating": 4}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review(self):
        review = Review.objects.create(business_user=self.business_user, reviewer=self.customer_user, rating=5, description="Great!")
        self.client.force_authenticate(self.customer_user)
        url = reverse('review-detail', args=[review.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    def test_delete_review_forbidden(self):
        review = Review.objects.create(business_user=self.business_user, reviewer=self.customer_user, rating=5, description="Great!")
        other_user = User.objects.create_user(username='other', password='pass', email='other@mail.de')
        UserProfile.objects.create(user=other_user, type='customer')
        self.client.force_authenticate(other_user)
        url = reverse('review-detail', args=[review.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
