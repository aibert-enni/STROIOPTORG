from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.review.serializers import ReviewCreateSerializer, ReviewSerializer, ReviewUpdateSerializer
from apps.review.services import ReviewService


class ReviewCreateUpdateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=ReviewCreateSerializer,
        responses=ReviewCreateSerializer,
    )
    def post(self, request):
        request_serializer = ReviewCreateSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        review = ReviewService(request).create_review(**request_serializer.validated_data)
        response_serializer = ReviewSerializer(review)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=ReviewUpdateSerializer
    )
    def put(self, request, *args, **kwargs):
        request_serializer = ReviewUpdateSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        review = ReviewService(request).update_review(**request_serializer.validated_data)

        response_serializer = ReviewSerializer(review)

        return Response(response_serializer.data, status=status.HTTP_200_OK)



class ReviewGetDeleteAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    extend_schema(
        responses=ReviewSerializer
    )
    def get(self, request, pk):
        review = ReviewService.get_review(pk)
        response_serializer = ReviewSerializer(review)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        ReviewService.delete_review(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReviewListByMeAPIView(ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        reviews = ReviewService.get_reviews_by_user_id(self.request.user.id)
        return reviews

class ReviewListByUserIdAPIView(ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        reviews = ReviewService.get_reviews_by_user_id(pk)
        return reviews

class ReviewListByProductAPIView(ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        reviews = ReviewService.get_product_reviews(pk)
        return reviews