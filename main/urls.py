from django.urls import path
from .views import (
    HomeListView, ShopDetailView, ShopListView,
    CartListView, CheckoutListView, ContactListView, Search, login_request, register_request, logout_request
)

urlpatterns = [
    path('', HomeListView.as_view(), name='home'),
    path('shop/', ShopListView.as_view(), name='shop'),
    path('shop/<int:prod_id>/', ShopDetailView.as_view(), name='detail'),  # TODO: add unique indicator
    path('shopping-cart/', CartListView.as_view(), name='cart'),
    path('shopping-cart/checkout/', CheckoutListView.as_view(), name='checkout'),
    path('contact/', ContactListView.as_view(), name='contact'),
    path('search/', Search.as_view(), name='search'),  
    path('login/', login_request, name='login'),
    path('register/', register_request, name='register'),
    path('logout/', logout_request, name='logout'),
]
