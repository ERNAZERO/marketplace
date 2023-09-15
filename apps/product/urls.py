from django.urls import path, include
from .views import (ProductCreateAPIView,
                    ProductListAPIView,
                    ProductDetailAPIView,
                    ProductUpdateAPIView,
                    ProductDeleteAPIView,
                    AddToCartAPIView,
                    CartDetailAPIView,
                    ProductRatingAPIView,
                    CommentCreateAPIView,
                    ProductPaginationListView,
                    ProductSearchAPIView,
                    PaymentAPIView, ProductCommentsListAPIView
                    )

urlpatterns = [
    path('create/', ProductCreateAPIView.as_view(), name='product-create'),
    path('list/', ProductListAPIView.as_view(), name='product-list'),
    path('<int:id>/', ProductDetailAPIView.as_view(), name="product-detail"),
    path('<int:id>/update', ProductUpdateAPIView.as_view(), name="product-update"),
    path('<int:id>/delete', ProductDeleteAPIView.as_view(), name="product-delete"),
    path('add_to_cart/', AddToCartAPIView.as_view(), name="add-to-cart"),
    path('cart/', CartDetailAPIView.as_view(), name="cart-detail"),
    path('<int:id>/rating/', ProductRatingAPIView.as_view(), name="product-rating"),
    path('<int:id>/comments/create/', CommentCreateAPIView.as_view(), name='comment-create'),
    path('pagination/', ProductPaginationListView.as_view(), name='pagination'),
    path('search/', ProductSearchAPIView.as_view(), name='product-search'),
    path('<int:id>/payment/', PaymentAPIView.as_view(), name='payment'),
    path('<int:id>/comments/', ProductCommentsListAPIView.as_view(), name='product-comments-list'),
]



