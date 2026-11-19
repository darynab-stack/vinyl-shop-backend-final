import pytest
from django.contrib.auth.models import User

from .models import CartItem


@pytest.mark.django_db
def test_cart_without_token(api_client):
    response = api_client.get("/api/cart/", format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_get_empty_cart(auth_client):
    response = auth_client.get("/api/cart/", format="json")
    assert response.status_code == 200
    assert response.data["items"] == []
    assert response.data["total"] == 0


@pytest.mark.django_db
def test_add_to_cart(auth_client, album):
    response = auth_client.post("/api/cart/", {"album": album.id}, format="json")
    assert response.status_code == 201


@pytest.mark.django_db
def test_add_unknown_album(auth_client):
    response = auth_client.post("/api/cart/", {"album": 999}, format="json")
    assert response.status_code == 404


@pytest.mark.django_db
def test_add_same_album_increases_quantity(auth_client, album):
    auth_client.post("/api/cart/", {"album": album.id}, format="json")
    response = auth_client.post("/api/cart/", {"album": album.id}, format="json")
    assert response.data["quantity"] == 2


@pytest.mark.django_db
def test_add_quantity_zero(auth_client, album):
    data = {"album": album.id, "quantity": 0}
    response = auth_client.post("/api/cart/", data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_add_quantity_not_a_number(auth_client, album):
    data = {"album": album.id, "quantity": "abc"}
    response = auth_client.post("/api/cart/", data, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_cart_total(auth_client, album, album2):
    auth_client.post("/api/cart/", {"album": album.id, "quantity": 2}, format="json")
    auth_client.post("/api/cart/", {"album": album2.id}, format="json")
    response = auth_client.get("/api/cart/", format="json")
    assert len(response.data["items"]) == 2
    assert response.data["total"] == 70


@pytest.mark.django_db
def test_cart_shows_only_own_items(auth_client, album):
    other = User.objects.create_user(username="other", password="StrongPass2026!")
    CartItem.objects.create(user=other, album=album)
    response = auth_client.get("/api/cart/", format="json")
    assert response.data["items"] == []


@pytest.mark.django_db
def test_update_quantity(auth_client, user, album):
    item = CartItem.objects.create(user=user, album=album)
    response = auth_client.patch(
        f"/api/cart/{item.id}/", {"quantity": 5}, format="json"
    )
    assert response.data["quantity"] == 5


@pytest.mark.django_db
def test_update_quantity_to_zero(auth_client, user, album):
    item = CartItem.objects.create(user=user, album=album)
    response = auth_client.patch(
        f"/api/cart/{item.id}/", {"quantity": 0}, format="json"
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_update_quantity_not_a_number(auth_client, user, album):
    item = CartItem.objects.create(user=user, album=album)
    response = auth_client.patch(
        f"/api/cart/{item.id}/", {"quantity": "abc"}, format="json"
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_update_foreign_item_not_found(auth_client, album):
    other = User.objects.create_user(username="other", password="StrongPass2026!")
    item = CartItem.objects.create(user=other, album=album)
    response = auth_client.patch(
        f"/api/cart/{item.id}/", {"quantity": 5}, format="json"
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_item(auth_client, user, album):
    item = CartItem.objects.create(user=user, album=album)
    response = auth_client.delete(f"/api/cart/{item.id}/", format="json")
    assert response.status_code == 204


@pytest.mark.django_db
def test_delete_foreign_item_not_found(auth_client, album):
    other = User.objects.create_user(username="other", password="StrongPass2026!")
    item = CartItem.objects.create(user=other, album=album)
    response = auth_client.delete(f"/api/cart/{item.id}/", format="json")
    assert response.status_code == 404
    assert CartItem.objects.filter(id=item.id).exists()


@pytest.mark.django_db
def test_delete_missing_item(auth_client):
    response = auth_client.delete("/api/cart/999/", format="json")
    assert response.status_code == 404
