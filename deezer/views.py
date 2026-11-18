import logging

import requests
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import Album

logger = logging.getLogger(__name__)


class AlbumTracksView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            album = Album.objects.select_related("artist").get(pk=pk)
        except Album.DoesNotExist:
            return Response(
                {"error": "Платівку не знайдено"},
                status=status.HTTP_404_NOT_FOUND,
            )

        query = f"{album.artist.name} {album.title}"
        try:
            search_response = requests.get(
                "https://api.deezer.com/search/album",
                params={"q": query},
                timeout=5,
            )
            search_response.raise_for_status()
            search_data = search_response.json()
        except (requests.RequestException, ValueError) as exc:
            logger.error("Deezer album search error for album %s: %s", pk, exc)
            return Response(
                {"error": "Не вдалося отримати дані з Deezer"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        albums_found = search_data.get("data", [])
        if not albums_found:
            return Response([], status=status.HTTP_200_OK)

        deezer_album_id = albums_found[0].get("id")
        if not deezer_album_id:
            return Response([], status=status.HTTP_200_OK)

        try:
            tracks_response = requests.get(
                f"https://api.deezer.com/album/{deezer_album_id}/tracks",
                timeout=5,
            )
            tracks_response.raise_for_status()
            tracks_data = tracks_response.json()
        except (requests.RequestException, ValueError) as exc:
            logger.error(
                "Deezer tracks fetch error for deezer_id %s: %s", deezer_album_id, exc
            )
            return Response(
                {"error": "Не вдалося завантажити треки з Deezer"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        tracks = [
            {
                "title": track.get("title", ""),
                "duration": track.get("duration", 0),
                "preview": track.get("preview", ""),
            }
            for track in tracks_data.get("data", [])
        ]
        return Response(tracks, status=status.HTTP_200_OK)
