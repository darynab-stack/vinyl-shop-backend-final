import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from shop.models import Album, Artist, Genre


@pytest.fixture
def admin_client():
    admin = User.objects.create_superuser(
        username="admin",
        password="AdminPass2026!",
        email="admin@example.com",
    )
    client = APIClient()
    client.force_authenticate(user=admin)
    return client


@pytest.mark.django_db
def test_albums_list_without_token(api_client, album, album2):
    response = api_client.get("/api/albums/")
    assert response.status_code == 200
    assert len(response.data) == 2


@pytest.mark.django_db
def test_albums_list_contains_artist_and_genre_names(api_client, album):
    response = api_client.get("/api/albums/")
    assert response.status_code == 200
    assert response.data[0]["artist_name"] == "The Beatles"
    assert response.data[0]["genre_name"] == "Rock"


@pytest.mark.django_db
def test_album_detail_not_found(api_client):
    response = api_client.get("/api/albums/999/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_filter_albums_by_search_case_insensitive(api_client, album, album2):
    response = api_client.get("/api/albums/", {"search": "abbey"})
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Abbey Road"


@pytest.mark.django_db
def test_filter_albums_by_genre(api_client, album):
    jazz = Genre.objects.create(name="Jazz")
    Album.objects.create(
        title="Kind of Blue",
        price="30.00",
        artist=album.artist,
        genre=jazz,
    )
    response = api_client.get("/api/albums/", {"genre": album.genre.id})
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Abbey Road"


@pytest.mark.django_db
def test_filter_albums_by_artist(api_client, album):
    pink_floyd = Artist.objects.create(name="Pink Floyd")
    Album.objects.create(
        title="The Wall",
        price="28.00",
        artist=pink_floyd,
        genre=album.genre,
    )
    response = api_client.get("/api/albums/", {"artist": pink_floyd.id})
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == "The Wall"


@pytest.mark.django_db
def test_filter_albums_by_min_price(api_client, album, album2):
    response = api_client.get("/api/albums/", {"min_price": "22"})
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Abbey Road"


@pytest.mark.django_db
def test_filter_albums_by_max_price(api_client, album, album2):
    response = api_client.get("/api/albums/", {"max_price": "22"})
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Revolver"


@pytest.mark.django_db
def test_filter_albums_by_in_stock_true(api_client, album):
    Album.objects.create(
        title="Sold Out Vinyl",
        price="18.00",
        artist=album.artist,
        genre=album.genre,
        in_stock=False,
    )
    response = api_client.get("/api/albums/", {"in_stock": "true"})
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Abbey Road"


@pytest.mark.django_db
def test_filter_albums_by_in_stock_false(api_client, album):
    Album.objects.create(
        title="Sold Out Vinyl",
        price="18.00",
        artist=album.artist,
        genre=album.genre,
        in_stock=False,
    )
    response = api_client.get("/api/albums/", {"in_stock": "false"})
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Sold Out Vinyl"


@pytest.mark.django_db
def test_filter_albums_combined(api_client, album, album2):
    Album.objects.create(
        title="Rubber Soul",
        price="35.00",
        artist=album.artist,
        genre=album.genre,
    )
    response = api_client.get("/api/albums/", {"search": "r", "max_price": "22"})
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Revolver"


@pytest.mark.django_db
def test_create_album_unauthenticated_returns_401(api_client, album):
    payload = {
        "title": "Let It Be",
        "price": "24.00",
        "artist": album.artist.id,
        "genre": album.genre.id,
    }
    response = api_client.post("/api/albums/", payload, format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_album_regular_user_returns_403(auth_client, album):
    payload = {
        "title": "Let It Be",
        "price": "24.00",
        "artist": album.artist.id,
        "genre": album.genre.id,
    }
    response = auth_client.post("/api/albums/", payload, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_album_admin_returns_201(admin_client, album):
    payload = {
        "title": "Let It Be",
        "price": "24.00",
        "artist": album.artist.id,
        "genre": album.genre.id,
    }
    response = admin_client.post("/api/albums/", payload, format="json")
    assert response.status_code == 201
    assert response.data["title"] == "Let It Be"


@pytest.mark.django_db
def test_patch_album_regular_user_returns_403(auth_client, album):
    response = auth_client.patch(
        f"/api/albums/{album.id}/", {"price": "30.00"}, format="json"
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_patch_album_admin_returns_200(admin_client, album):
    response = admin_client.patch(
        f"/api/albums/{album.id}/", {"price": "30.00"}, format="json"
    )
    assert response.status_code == 200
    assert response.data["price"] == "30.00"


@pytest.mark.django_db
def test_delete_album_admin_returns_204(admin_client, album):
    response = admin_client.delete(f"/api/albums/{album.id}/")
    assert response.status_code == 204


@pytest.mark.django_db
def test_create_genre_regular_user_returns_403(auth_client):
    response = auth_client.post("/api/genres/", {"name": "Electronic"}, format="json")
    assert response.status_code == 403
