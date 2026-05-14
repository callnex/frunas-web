from django.urls import path

from .views import (
    AccountView,
    ActivateAccountView,
    CheckoutView,
    OrderDetailView,
    OrderSuccessView,
    RegisterView,
    StoreView,
    UserLoginView,
    UserLogoutView,
)

urlpatterns = [
    path('', StoreView.as_view(), name='store'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate_account'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('account/', AccountView.as_view(), name='account'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/success/', OrderSuccessView.as_view(), name='order_success'),
]
