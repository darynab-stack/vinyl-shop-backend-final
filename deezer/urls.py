from django.urls import path

from .views import AlbumTracksView

urlpatterns = [
    path("albums/<int:pk>/tracks/", AlbumTracksView.as_view(), name="album-tracks"),
]
