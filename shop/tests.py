import pytest


@pytest.mark.django_db
def test_wishlist_without_token(api_client):
    response = api_client.get("/api/wishlist/", format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_add_to_wishlist(auth_client, album):
    response = auth_client.post("/api/wishlist/", {"album": album.id}, format="json")
    assert response.status_code == 201


@pytest.mark.django_db
def test_add_same_album_twice(auth_client, album):
    auth_client.post("/api/wishlist/", {"album": album.id}, format="json")
    auth_client.post("/api/wishlist/", {"album": album.id}, format="json")
    response = auth_client.get("/api/wishlist/", format="json")
    assert len(response.data) == 1


@pytest.mark.django_db
def test_delete_from_wishlist(auth_client, album):
    auth_client.post("/api/wishlist/", {"album": album.id}, format="json")
    response = auth_client.delete(f"/api/wishlist/{album.id}/", format="json")
    assert response.status_code == 204


@pytest.mark.django_db
def test_add_unknown_album_to_wishlist(auth_client):
    response = auth_client.post("/api/wishlist/", {"album": 999}, format="json")
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_album_not_in_wishlist(auth_client):
    response = auth_client.delete("/api/wishlist/999/", format="json")
    assert response.status_code == 404
