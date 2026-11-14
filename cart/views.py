from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import Album

from .models import CartItem
from .serializers import CartItemSerializer


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = CartItem.objects.filter(user=request.user)

        total = 0
        for item in items:
            total += item.album.price * item.quantity

        serializer = CartItemSerializer(items, many=True)
        return Response({"items": serializer.data, "total": total})

    def post(self, request):
        try:
            album = Album.objects.get(pk=request.data.get("album"))
        except (Album.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Платівку не знайдено"}, status=404)

        try:
            quantity = int(request.data.get("quantity", 1))
        except (ValueError, TypeError):
            return Response({"error": "Кількість має бути числом"}, status=400)
        if quantity < 1:
            return Response({"error": "Кількість має бути не менше 1"}, status=400)

        try:
            item = CartItem.objects.get(user=request.user, album=album)
            item.quantity += quantity
            item.save()
            return Response(CartItemSerializer(item).data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            item = CartItem.objects.create(
                user=request.user, album=album, quantity=quantity
            )
            return Response(
                CartItemSerializer(item).data, status=status.HTTP_201_CREATED
            )


class CartDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            item = CartItem.objects.get(pk=pk, user=request.user)
        except CartItem.DoesNotExist:
            return Response({"error": "Позицію не знайдено"}, status=404)

        try:
            quantity = int(request.data.get("quantity"))
        except (ValueError, TypeError):
            return Response({"error": "Кількість має бути числом"}, status=400)
        if quantity < 1:
            return Response({"error": "Кількість має бути не менше 1"}, status=400)

        item.quantity = quantity
        item.save()
        return Response(CartItemSerializer(item).data)

    def delete(self, request, pk):
        try:
            item = CartItem.objects.get(pk=pk, user=request.user)
        except CartItem.DoesNotExist:
            return Response({"error": "Позицію не знайдено"}, status=404)

        item.delete()
        return Response(status=204)
