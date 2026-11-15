from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import Album, Artist, Genre


class WishlistTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="StrongPass2026!"
        )
        artist = Artist.objects.create(name="The Beatles")
        genre = Genre.objects.create(name="Rock")
        self.album = Album.objects.create(
            title="Abbey Road", price="25.00", artist=artist, genre=genre
        )

    def test_wishlist_without_token(self):
        response = self.client.get("/api/wishlist/")
        self.assertEqual(response.status_code, 401)

    def test_add_to_wishlist(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/wishlist/", {"album": self.album.id})
        self.assertEqual(response.status_code, 201)

    def test_add_same_album_twice(self):
        self.client.force_authenticate(user=self.user)
        self.client.post("/api/wishlist/", {"album": self.album.id})
        self.client.post("/api/wishlist/", {"album": self.album.id})
        response = self.client.get("/api/wishlist/")
        self.assertEqual(len(response.data), 1)

    def test_delete_from_wishlist(self):
        self.client.force_authenticate(user=self.user)
        self.client.post("/api/wishlist/", {"album": self.album.id})
        response = self.client.delete(f"/api/wishlist/{self.album.id}/")
        self.assertEqual(response.status_code, 204)
