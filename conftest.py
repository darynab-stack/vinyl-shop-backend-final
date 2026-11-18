import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="StrongPass2026!")


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def album():
    from shop.models import Album, Artist, Genre

    artist = Artist.objects.create(name="The Beatles")
    genre = Genre.objects.create(name="Rock")
    return Album.objects.create(
        title="Abbey Road", price="25.00", artist=artist, genre=genre
    )


@pytest.fixture
def album2(album):
    from shop.models import Album

    return Album.objects.create(
        title="Revolver", price="20.00", artist=album.artist, genre=album.genre
    )
