from apps.products.routers import router as products_router
from apps.comments.routers import router as comment_router
from apps.orders.routers import router as order_router

app_name = "api"

urlpatterns = []

urlpatterns += products_router.urls + comment_router.urls + order_router.urls
