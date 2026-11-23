import logging

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from .models import Subscription
from .services import notify_subscribers


@pytest.fixture
def out_of_stock_album(album):
    album.in_stock = False
    album.save()
    return album


@pytest.fixture
def subscriber():
    return User.objects.create_user(
        username="subscriber",
        email="subscriber@example.com",
        password="StrongPass2026!",
    )


@pytest.fixture
def admin_api_client():
    admin = User.objects.create_superuser(
        username="admin", email="admin@example.com", password="StrongPass2026!"
    )
    client = APIClient()
    client.force_authenticate(user=admin)
    return client


@pytest.mark.django_db
def test_subscribe_without_token(api_client, out_of_stock_album):
    url = f"/api/albums/{out_of_stock_album.id}/subscribe/"
    response = api_client.post(url, format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_subscribe(auth_client, user, out_of_stock_album):
    url = f"/api/albums/{out_of_stock_album.id}/subscribe/"
    response = auth_client.post(url, format="json")
    assert response.status_code == 201
    assert response.data["album_title"] == "Abbey Road"
    assert Subscription.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_subscribe_twice(auth_client, out_of_stock_album):
    url = f"/api/albums/{out_of_stock_album.id}/subscribe/"
    auth_client.post(url, format="json")
    response = auth_client.post(url, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_subscribe_to_album_in_stock(auth_client, album):
    response = auth_client.post(f"/api/albums/{album.id}/subscribe/", format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_subscribe_to_unknown_album(auth_client):
    response = auth_client.post("/api/albums/999/subscribe/", format="json")
    assert response.status_code == 404


@pytest.mark.django_db
def test_subscription_list_shows_only_own(
    auth_client, user, subscriber, out_of_stock_album
):
    Subscription.objects.create(user=user, album=out_of_stock_album)
    Subscription.objects.create(user=subscriber, album=out_of_stock_album)
    response = auth_client.get("/api/subscriptions/", format="json")
    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_unsubscribe(auth_client, user, out_of_stock_album):
    Subscription.objects.create(user=user, album=out_of_stock_album)
    url = f"/api/albums/{out_of_stock_album.id}/subscribe/"
    response = auth_client.delete(url, format="json")
    assert response.status_code == 204
    assert Subscription.objects.count() == 0


@pytest.mark.django_db
def test_unsubscribe_when_not_subscribed(auth_client, out_of_stock_album):
    url = f"/api/albums/{out_of_stock_album.id}/subscribe/"
    response = auth_client.delete(url, format="json")
    assert response.status_code == 404


@pytest.mark.django_db
def test_notify_subscribers_sends_email(
    subscriber, out_of_stock_album, mailoutbox, caplog
):
    Subscription.objects.create(user=subscriber, album=out_of_stock_album)

    with caplog.at_level(logging.INFO):
        sent = notify_subscribers(out_of_stock_album)

    assert sent == 1
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == ["subscriber@example.com"]
    assert "Abbey Road" in mailoutbox[0].subject
    assert Subscription.objects.count() == 0
    assert "Sent 1 back-in-stock emails" in caplog.text


@pytest.mark.django_db
def test_restock_sends_email(
    admin_api_client, subscriber, out_of_stock_album, mailoutbox
):
    Subscription.objects.create(user=subscriber, album=out_of_stock_album)
    response = admin_api_client.patch(
        f"/api/albums/{out_of_stock_album.id}/", {"in_stock": True}, format="json"
    )
    assert response.status_code == 200
    assert len(mailoutbox) == 1


@pytest.mark.django_db
def test_price_change_does_not_send_email(
    admin_api_client, subscriber, out_of_stock_album, mailoutbox
):
    Subscription.objects.create(user=subscriber, album=out_of_stock_album)
    response = admin_api_client.patch(
        f"/api/albums/{out_of_stock_album.id}/", {"price": "30.00"}, format="json"
    )
    assert response.status_code == 200
    assert len(mailoutbox) == 0
    assert Subscription.objects.count() == 1


def admin_form_data(album, in_stock):
    data = {
        "title": album.title,
        "price": album.price,
        "artist": album.artist.id,
        "genre": album.genre.id,
        "cover_url": album.cover_url,
        "year": album.year or "",
    }
    if in_stock:
        data["in_stock"] = "on"
    return data


@pytest.mark.django_db
def test_restock_in_admin_sends_email(
    admin_client, subscriber, out_of_stock_album, mailoutbox
):
    Subscription.objects.create(user=subscriber, album=out_of_stock_album)
    response = admin_client.post(
        f"/admin/shop/album/{out_of_stock_album.id}/change/",
        admin_form_data(out_of_stock_album, in_stock=True),
    )
    assert response.status_code == 302
    assert len(mailoutbox) == 1


@pytest.mark.django_db
def test_other_change_in_admin_does_not_send_email(
    admin_client, subscriber, out_of_stock_album, mailoutbox
):
    Subscription.objects.create(user=subscriber, album=out_of_stock_album)
    data = admin_form_data(out_of_stock_album, in_stock=False)
    data["price"] = "30.00"
    response = admin_client.post(
        f"/admin/shop/album/{out_of_stock_album.id}/change/", data
    )
    assert response.status_code == 302
    assert len(mailoutbox) == 0
