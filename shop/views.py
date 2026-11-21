from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.services import notify_subscribers

from .models import Album, Artist, Genre, Wishlist
from .permissions import IsAdminOrReadOnly
from .serializers import AlbumSerializer, ArtistSerializer, GenreSerializer


class ArtistListView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        artists = Artist.objects.all()
        serializer = ArtistSerializer(artists, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ArtistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenreListView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GenreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArtistDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):
        try:
            artist = Artist.objects.get(pk=pk)
        except Artist.DoesNotExist:
            return Response({"error": "Виконавця не знайдено"}, status=404)

        serializer = ArtistSerializer(artist)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            artist = Artist.objects.get(pk=pk)
        except Artist.DoesNotExist:
            return Response({"error": "Виконавця не знайдено"}, status=404)

        serializer = ArtistSerializer(artist, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            artist = Artist.objects.get(pk=pk)
        except Artist.DoesNotExist:
            return Response({"error": "Виконавця не знайдено"}, status=404)

        if artist.albums.exists():
            return Response(
                {"error": "Неможливо видалити виконавця, у нього є платівки"},
                status=409,
            )

        artist.delete()
        return Response(status=204)


class AlbumListView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        albums = Album.objects.all()

        search = request.query_params.get("search")
        genre = request.query_params.get("genre")
        artist = request.query_params.get("artist")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        in_stock = request.query_params.get("in_stock")

        if search:
            albums = albums.filter(title__icontains=search)
        if genre:
            albums = albums.filter(genre_id=genre)
        if artist:
            albums = albums.filter(artist_id=artist)
        if min_price:
            albums = albums.filter(price__gte=min_price)
        if max_price:
            albums = albums.filter(price__lte=max_price)
        if in_stock is not None:
            in_stock_lower = in_stock.lower()
            if in_stock_lower == "true":
                albums = albums.filter(in_stock=True)
            elif in_stock_lower == "false":
                albums = albums.filter(in_stock=False)

        serializer = AlbumSerializer(albums, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AlbumSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AlbumDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):
        try:
            album = Album.objects.get(pk=pk)
        except Album.DoesNotExist:
            return Response({"error": "Платівку не знайдено"}, status=404)

        serializer = AlbumSerializer(album)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            album = Album.objects.get(pk=pk)
        except Album.DoesNotExist:
            return Response({"error": "Платівку не знайдено"}, status=404)

        was_in_stock = album.in_stock
        serializer = AlbumSerializer(album, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if not was_in_stock and album.in_stock:
                notify_subscribers(album)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            album = Album.objects.get(pk=pk)
        except Album.DoesNotExist:
            return Response({"error": "Платівку не знайдено"}, status=404)

        album.delete()
        return Response(status=204)


class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Wishlist.objects.filter(user=request.user)
        albums = [item.album for item in items]
        serializer = AlbumSerializer(albums, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            album = Album.objects.get(pk=request.data.get("album"))
        except (Album.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Платівку не знайдено"}, status=404)

        Wishlist.objects.get_or_create(user=request.user, album=album)
        return Response(AlbumSerializer(album).data, status=201)


class WishlistDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        deleted, _ = Wishlist.objects.filter(user=request.user, album_id=pk).delete()
        if deleted == 0:
            return Response({"error": "Платівки немає у списку бажаного"}, status=404)
        return Response(status=204)
