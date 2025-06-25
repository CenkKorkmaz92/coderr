from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

class AuthTests(APITestCase):
    def test_registration_success(self):
        url = reverse('registration')
        data = {
            "username": "testuser",
            "email": "testuser@mail.de",
            "password": "testpassword123",
            "repeated_password": "testpassword123",
            "type": "customer"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])
        self.assertIn('user_id', response.data)

    def test_registration_invalid(self):
        url = reverse('registration')
        data = {
            "username": "",
            "email": "invalid",
            "password": "123",
            "repeated_password": "456",
            "type": "customer"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        # Register first
        reg_url = reverse('registration')
        reg_data = {
            "username": "loginuser",
            "email": "loginuser@mail.de",
            "password": "testpassword123",
            "repeated_password": "testpassword123",
            "type": "customer"
        }
        self.client.post(reg_url, reg_data, format='json')
        # Now login
        url = reverse('login')
        data = {
            "username": "loginuser",
            "password": "testpassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], data['username'])
        self.assertIn('user_id', response.data)

    def test_login_invalid(self):
        url = reverse('login')
        data = {
            "username": "doesnotexist",
            "password": "wrongpass"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
