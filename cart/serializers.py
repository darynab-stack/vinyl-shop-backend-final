from rest_framework import serializers

from .models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    album_title = serializers.CharField(source="album.title", read_only=True)
    album_price = serializers.DecimalField(
        source="album.price",
        max_digits=8,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CartItem
        fields = ["id", "album", "album_title", "album_price", "quantity"]
