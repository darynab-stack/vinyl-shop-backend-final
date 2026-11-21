import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from .models import Review


@pytest.fixture
def other_user():
    return User.objects.create_user(username="other", password="StrongPass2026!")


@pytest.fixture
def other_client(other_user):
    client = APIClient()
    client.force_authenticate(user=other_user)
    return client


@pytest.fixture
def admin_api_client():
    admin = User.objects.create_superuser(
        username="admin", email="admin@example.com", password="StrongPass2026!"
    )
    client = APIClient()
    client.force_authenticate(user=admin)
    return client


@pytest.fixture
def review(user, album):
    return Review.objects.create(user=user, album=album, text="Чудово", rating=5)


@pytest.mark.django_db
def test_list_reviews_without_token(api_client, review):
    response = api_client.get(f"/api/albums/{review.album.id}/reviews/", format="json")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["username"] == "testuser"


@pytest.mark.django_db
def test_list_reviews_for_unknown_album(api_client):
    response = api_client.get("/api/albums/999/reviews/", format="json")
    assert response.status_code == 404


@pytest.mark.django_db
def test_create_review_without_token(api_client, album):
    response = api_client.post(
        f"/api/albums/{album.id}/reviews/",
        {"text": "Гість", "rating": 3},
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_review(auth_client, user, album):
    response = auth_client.post(
        f"/api/albums/{album.id}/reviews/",
        {"text": "Класика", "rating": 5},
        format="json",
    )
    assert response.status_code == 201
    assert Review.objects.filter(user=user, album=album).count() == 1


@pytest.mark.django_db
def test_create_second_review_for_same_album(auth_client, review):
    response = auth_client.post(
        f"/api/albums/{review.album.id}/reviews/",
        {"text": "Ще раз", "rating": 4},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
@pytest.mark.parametrize("rating", [0, 6])
def test_create_review_with_wrong_rating(auth_client, album, rating):
    response = auth_client.post(
        f"/api/albums/{album.id}/reviews/",
        {"text": "Текст", "rating": rating},
        format="json",
    )
    assert response.status_code == 400
    assert "rating" in response.data


@pytest.mark.django_db
def test_create_review_without_text(auth_client, album):
    response = auth_client.post(
        f"/api/albums/{album.id}/reviews/", {"rating": 4}, format="json"
    )
    assert response.status_code == 400
    assert "text" in response.data


@pytest.mark.django_db
def test_update_own_review(auth_client, review):
    response = auth_client.patch(
        f"/api/reviews/{review.id}/", {"rating": 3}, format="json"
    )
    assert response.status_code == 200
    review.refresh_from_db()
    assert review.rating == 3


@pytest.mark.django_db
def test_update_other_users_review(other_client, review):
    response = other_client.patch(
        f"/api/reviews/{review.id}/", {"rating": 1}, format="json"
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_cannot_update_other_users_review(admin_api_client, review):
    response = admin_api_client.patch(
        f"/api/reviews/{review.id}/", {"rating": 1}, format="json"
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_other_users_review(other_client, review):
    response = other_client.delete(f"/api/reviews/{review.id}/", format="json")
    assert response.status_code == 403
    assert Review.objects.count() == 1


@pytest.mark.django_db
def test_admin_deletes_other_users_review(admin_api_client, review):
    response = admin_api_client.delete(f"/api/reviews/{review.id}/", format="json")
    assert response.status_code == 204
    assert Review.objects.count() == 0


@pytest.mark.django_db
def test_delete_own_review(auth_client, review):
    response = auth_client.delete(f"/api/reviews/{review.id}/", format="json")
    assert response.status_code == 204
    assert Review.objects.count() == 0


@pytest.mark.django_db
def test_delete_unknown_review(auth_client):
    response = auth_client.delete("/api/reviews/999/", format="json")
    assert response.status_code == 404
