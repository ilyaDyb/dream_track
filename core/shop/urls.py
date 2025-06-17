from django.urls import path

from .views import ShopView, BuyShopItemView

app_name = 'shop'

urlpatterns = [
    path('shop/', ShopView.as_view(), name='shop'),
    path('shop/buy/<int:item_id>/', BuyShopItemView.as_view(), name='buy_shop_item'),
]