from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse


class ApiAuthViewTests(TestCase):
    def setUp(self):
        # Create test user.
        User = get_user_model()
        self.usr = User.objects.create_user(
            username="michael", email="michael@bluth.com", password="bananastand"
        )

    def test_login(self):
        # Get login url.
        login_url = reverse("api-token-login")
        # Login.
        response = self.client.post(
            login_url, data={"username": "michael", "password": "bananastand"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Token.objects.filter(user=self.usr).exists())
