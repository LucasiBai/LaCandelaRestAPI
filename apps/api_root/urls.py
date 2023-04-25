from apps.products.urls import urlpatterns as products_urls
from apps.comments.urls import urlpatterns as comment_urls
from apps.orders.urls import urlpatterns as order_urls
from apps.categories.urls import urlpatterns as category_urls
from apps.cart.urls import urlpatterns as cart_urls
from apps.payment_methods.urls import urlpatterns as pay_urls
from apps.shipping.urls import urlpatterns as ship_urls
from apps.favourites.urls import urlpatterns as fav_urls
from apps.promos.urls import urlpatterns as promo_urls

app_name = "api"

urlpatterns = products_urls + comment_urls + order_urls + category_urls + cart_urls + pay_urls + ship_urls + fav_urls + promo_urls
