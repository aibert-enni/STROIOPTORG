from django.db import IntegrityError
from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from apps.order.models import OrderItem, OrderStatus
from apps.review.models import Review


class ReviewService:
    def __init__(self, request):
        self.request = request

    def create_review(self, order_item_id: int, score: float, comment: str = None) -> Review:
        order_item = get_object_or_404(OrderItem.objects.select_related('order'), pk=order_item_id)

        if order_item.order.status != OrderStatus.COMPLETED:
            raise ValidationError('Заказ не выполненный')
        if order_item.order.user != self.request.user:
            raise ValidationError('Данный пользователь не делал такой заказ')

        review = Review(user=self.request.user,product=order_item.product, score=score, comment=comment)

        try:
            review.save()
        except IntegrityError:
            raise ValidationError('Отзыв на этот продукт уже существует')

        return review

    def update_review(self, review_id: int, score: float, comment: str = None) -> Review:
        review = get_object_or_404(Review, pk=review_id)

        if review.user != self.request.user:
            raise ValidationError('Вы не владелец отзыва')

        review.score = score
        review.comment = comment
        review.save()
        return review

    @staticmethod
    def get_review(review_id: int) -> Review:
        review = get_object_or_404(Review, pk=review_id)
        return review

    @staticmethod
    def get_reviews_by_user_id(user_id: int) -> Review:
        reviews = Review.objects.filter(user__id=user_id)
        return reviews

    @staticmethod
    def delete_review(review_id: int) -> Review:
        review = get_object_or_404(Review, pk=review_id)
        review.delete()
        return review

    @staticmethod
    def get_product_reviews(product_id: int) -> QuerySet[Review]:
        reviews = Review.objects.filter(product=product_id)
        return reviews
