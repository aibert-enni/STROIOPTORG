from django.urls import path

from apps.review.views import ReviewCreateUpdateAPIView, ReviewListByMeAPIView, \
    ReviewListByUserIdAPIView, ReviewListByProductAPIView, ReviewGetDeleteAPIView

app_name = 'api-review'

urlpatterns = [
    path('reviews/', ReviewCreateUpdateAPIView.as_view(), name='reviews'),
    path('reviews/<int:pk>/', ReviewGetDeleteAPIView.as_view(), name='review_delete'),
    path('reviews/me/', ReviewListByMeAPIView.as_view(), name='review-list-me'),
    path('reviews/user/<int:pk>/', ReviewListByUserIdAPIView.as_view(), name='review-list-user'),
    path('reviews/product/<int:pk>/', ReviewListByProductAPIView.as_view(), name='review-list-by-product'),
]
