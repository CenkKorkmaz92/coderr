from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import UserProfile
from offers.models import Offer, OfferDetail
from orders.models import Order
from rest_framework import status

class OrderTests(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(username='biz', password='pass', email='biz@mail.de')
        UserProfile.objects.create(user=self.business_user, type='business')
        self.customer_user = User.objects.create_user(username='cust', password='pass', email='cust@mail.de')
        UserProfile.objects.create(user=self.customer_user, type='customer')
        self.offer = Offer.objects.create(user=self.business_user, title="O1", description="D1")
        self.detail = OfferDetail.objects.create(offer=self.offer, title="Basic", revisions=1, delivery_time_in_days=2, price=10, features=["A"], offer_type="basic")

    def test_create_order_customer(self):
        self.client.force_authenticate(self.customer_user)
        url = reverse('order-list-create')
        response = self.client.post(url, {"offer_detail_id": self.detail.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

    def test_create_order_business_forbidden(self):
        self.client.force_authenticate(self.business_user)
        url = reverse('order-list-create')
        response = self.client.post(url, {"offer_detail_id": self.detail.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_orders(self):
        Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, offer_detail=self.detail, title="T", revisions=1, delivery_time_in_days=2, price=10, features=["A"], offer_type="basic")
        self.client.force_authenticate(self.customer_user)
        url = reverse('order-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_order_status(self):
        order = Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, offer_detail=self.detail, title="T", revisions=1, delivery_time_in_days=2, price=10, features=["A"], offer_type="basic")
        self.client.force_authenticate(self.business_user)
        url = reverse('order-detail', args=[order.id])
        response = self.client.patch(url, {"status": "completed"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, "completed")

    def test_update_order_status_forbidden(self):
        order = Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, offer_detail=self.detail, title="T", revisions=1, delivery_time_in_days=2, price=10, features=["A"], offer_type="basic")
        self.client.force_authenticate(self.customer_user)
        url = reverse('order-detail', args=[order.id])
        response = self.client.patch(url, {"status": "completed"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_admin(self):
        order = Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, offer_detail=self.detail, title="T", revisions=1, delivery_time_in_days=2, price=10, features=["A"], offer_type="basic")
        admin = User.objects.create_superuser(username='admin', password='adminpass', email='admin@mail.de')
        self.client.force_authenticate(admin)
        url = reverse('order-detail', args=[order.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_order_forbidden(self):
        order = Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, offer_detail=self.detail, title="T", revisions=1, delivery_time_in_days=2, price=10, features=["A"], offer_type="basic")
        self.client.force_authenticate(self.customer_user)
        url = reverse('order-detail', args=[order.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_count(self):
        Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, offer_detail=self.detail, title="T", revisions=1, delivery_time_in_days=2, price=10, features=["A"], offer_type="basic", status='in_progress')
        self.client.force_authenticate(self.business_user)
        url = reverse('order-count', args=[self.business_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('order_count', response.data)

    def test_completed_order_count(self):
        Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, offer_detail=self.detail, title="T", revisions=1, delivery_time_in_days=2, price=10, features=["A"], offer_type="basic", status='completed')
        self.client.force_authenticate(self.business_user)
        url = reverse('completed-order-count', args=[self.business_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('completed_order_count', response.data)
