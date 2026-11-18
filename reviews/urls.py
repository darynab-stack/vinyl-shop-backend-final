from django.urls import path

from .views import AlbumReviewListView, ReviewDetailView

urlpatterns = [
    path(
        "albums/<int:album_id>/reviews/",
        AlbumReviewListView.as_view(),
        name="album-reviews",
    ),
    path("reviews/<int:pk>/", ReviewDetailView.as_view(), name="review-detail"),
]
