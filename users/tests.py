from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class RegisterTests(APITestCase):
    def test_register_success(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPass2026!",
            "password2": "StrongPass2026!",
        }
        response = self.client.post("/api/auth/register/", data)
        self.assertEqual(response.status_code, 201)

    def test_register_passwords_do_not_match(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPass2026!",
            "password2": "OtherPass2026!",
        }
        response = self.client.post("/api/auth/register/", data)
        self.assertEqual(response.status_code, 400)


class LoginTests(APITestCase):
    def setUp(self):
        User.objects.create_user(username="testuser", password="StrongPass2026!")
        self.data = {"username": "testuser", "password": "StrongPass2026!"}

    def test_login_returns_access_and_refresh(self):
        response = self.client.post("/api/auth/login/", self.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_returns_new_access(self):
        login = self.client.post("/api/auth/login/", self.data)
        response = self.client.post(
            "/api/auth/refresh/", {"refresh": login.data["refresh"]}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
