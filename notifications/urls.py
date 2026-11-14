from django.urls import path

from .views import SubscribeView, SubscriptionListView

urlpatterns = [
    path(
        "albums/<int:album_id>/subscribe/",
        SubscribeView.as_view(),
        name="album-subscribe",
    ),
    path("subscriptions/", SubscriptionListView.as_view(), name="subscription-list"),
]
