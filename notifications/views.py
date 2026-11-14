from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import Album

from .models import Subscription
from .serializers import SubscriptionSerializer


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, album_id):
        try:
            album = Album.objects.get(pk=album_id)
        except Album.DoesNotExist:
            return Response({"error": "Платівку не знайдено"}, status=404)

        if album.in_stock:
            return Response(
                {"error": "Платівка вже є в наявності"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Subscription.objects.filter(user=request.user, album=album).exists():
            return Response(
                {"error": "Ви вже підписані на цю платівку"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription = Subscription.objects.create(user=request.user, album=album)
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data, status=201)

    def delete(self, request, album_id):
        try:
            subscription = Subscription.objects.get(
                user=request.user, album_id=album_id
            )
        except Subscription.DoesNotExist:
            return Response({"error": "Підписку не знайдено"}, status=404)

        subscription.delete()
        return Response(status=204)


class SubscriptionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)
