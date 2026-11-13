from django.conf import settings
from django.db import models

from shop.models import Album


class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("user", "album")

    def __str__(self):
        return f"{self.user} - {self.album} x{self.quantity}"
