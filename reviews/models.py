from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from shop.models import Album


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "album")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.album} ({self.rating})"
