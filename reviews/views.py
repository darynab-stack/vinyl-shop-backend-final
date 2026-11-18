from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import Album

from .models import Review
from .serializers import ReviewSerializer


class AlbumReviewListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, album_id):
        try:
            album = Album.objects.get(pk=album_id)
        except Album.DoesNotExist:
            return Response({"error": "Платівку не знайдено"}, status=404)

        reviews = Review.objects.filter(album=album)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, album_id):
        try:
            album = Album.objects.get(pk=album_id)
        except Album.DoesNotExist:
            return Response({"error": "Платівку не знайдено"}, status=404)

        if Review.objects.filter(user=request.user, album=album).exists():
            return Response(
                {"error": "Ви вже залишили відгук на цю платівку"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, album=album)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response({"error": "Відгук не знайдено"}, status=404)

        if review.user != request.user:
            return Response(
                {"error": "Редагувати можна лише власний відгук"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response({"error": "Відгук не знайдено"}, status=404)

        if review.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "Видаляти можна лише власний відгук"},
                status=status.HTTP_403_FORBIDDEN,
            )

        review.delete()
        return Response(status=204)
