from django.urls import path
from .views import (CustomerRegisterView,
                    SellerRegisterView,
                    LoginView,
                    CustomerListAPIView,
                    SellerListAPIView,
                    CustomerDetailAPIView,
                    SellerDetailAPIView,
                    AllUsersAPIView,
                    AdminRegisterAPIView,
                    VerifyEmailAPIView,
                    UserDeleteAPIView,
                    UserSettingsChangeAPIView,
                    ProductsForAdminAPIView,
                    UserSearchAPIView,
                    UserPaginationListView)

from apps.product.views import CartDetailAPIView


urlpatterns = [
    path('register/seller/', SellerRegisterView.as_view(), name='seller-register'),
    path('register/customer/', CustomerRegisterView.as_view(), name='customer-register'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/customer/verify_code/', VerifyEmailAPIView.as_view(), name='verify-code'),
    path('customers_list/', CustomerListAPIView.as_view(), name='users-list'),
    path('sellers_list/', SellerListAPIView.as_view(), name='sellers-list'),
    path('<int:id>/', CustomerDetailAPIView.as_view(), name='customer-deatil'),
    path('seller/<int:seller_id>/', SellerDetailAPIView.as_view(), name='seller_detail'),
    path('cart/', CartDetailAPIView.as_view(), name='my-cart'),
    path('admin/users_list/', AllUsersAPIView.as_view(), name='all-users'),
    path('admin/register/', AdminRegisterAPIView.as_view(), name='admin_registration'),
    path('admin/<int:id>/delete/', UserDeleteAPIView.as_view(), name='user-delete'),
    path('admin/products/', ProductsForAdminAPIView.as_view(), name='all-products'),
    path('admin/<int:id>/user_settings', UserSettingsChangeAPIView.as_view(), name='change-user_settings'),
    path('admin/search/', UserSearchAPIView.as_view(), name='user-search'),
    path('admin/user_pagination/', UserPaginationListView.as_view(), name='user-pagination'),
]
