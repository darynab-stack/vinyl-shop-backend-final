from rest_framework import serializers

from .models import Album, Artist, Genre


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ["id", "name"]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class AlbumSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source="artist.name", read_only=True)
    genre_name = serializers.CharField(source="genre.name", read_only=True)

    class Meta:
        model = Album
        fields = [
            "id",
            "title",
            "price",
            "in_stock",
            "cover_url",
            "year",
            "artist",
            "artist_name",
            "genre",
            "genre_name",
        ]
