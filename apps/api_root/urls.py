from apps.products.urls import urlpatterns as products_urls
from apps.comments.urls import urlpatterns as comment_urls
from apps.orders.urls import urlpatterns as order_urls

app_name = "api"

urlpatterns = products_urls + comment_urls + order_urls
