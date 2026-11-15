import pytest
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_register_success(api_client):
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "StrongPass2026!",
        "password2": "StrongPass2026!",
    }
    response = api_client.post("/api/auth/register/", data, format="json")
    assert response.status_code == 201
    assert User.objects.filter(username="newuser").exists()


@pytest.mark.django_db
def test_register_passwords_do_not_match(api_client):
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "StrongPass2026!",
        "password2": "OtherPass2026!",
    }
    response = api_client.post("/api/auth/register/", data, format="json")
    assert response.status_code == 400
    assert not User.objects.filter(username="newuser").exists()


@pytest.mark.django_db
def test_login_returns_access_and_refresh(api_client, user):
    data = {"username": "testuser", "password": "StrongPass2026!"}
    response = api_client.post("/api/auth/login/", data, format="json")
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_refresh_returns_new_access(api_client, user):
    data = {"username": "testuser", "password": "StrongPass2026!"}
    tokens = api_client.post("/api/auth/login/", data, format="json").data
    response = api_client.post(
        "/api/auth/refresh/", {"refresh": tokens["refresh"]}, format="json"
    )
    assert response.status_code == 200
    assert "access" in response.data
