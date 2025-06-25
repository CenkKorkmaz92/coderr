from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import UserProfile
from rest_framework import status

class ProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass', email='test@mail.de')
        self.profile = UserProfile.objects.create(user=self.user, type='customer', first_name='A', last_name='B')

    def test_get_profile(self):
        self.client.force_authenticate(self.user)
        url = reverse('profile-detail', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_patch_profile(self):
        self.client.force_authenticate(self.user)
        url = reverse('profile-detail', args=[self.user.id])
        response = self.client.patch(url, {"first_name": "New"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.first_name, "New")

    def test_patch_profile_forbidden(self):
        other = User.objects.create_user(username='other', password='pass', email='other@mail.de')
        self.client.force_authenticate(other)
        url = reverse('profile-detail', args=[self.user.id])
        response = self.client.patch(url, {"first_name": "Hack"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_not_found(self):
        self.client.force_authenticate(self.user)
        url = reverse('profile-detail', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
