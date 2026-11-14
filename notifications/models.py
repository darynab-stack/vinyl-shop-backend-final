from django.conf import settings
from django.db import models

from shop.models import Album


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "album")

    def __str__(self):
        return f"{self.user} - {self.album}"
