from rest_framework import serializers

from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    album_title = serializers.CharField(source="album.title", read_only=True)

    class Meta:
        model = Subscription
        fields = ["id", "album", "album_title", "created_at"]
        read_only_fields = ["album", "created_at"]
