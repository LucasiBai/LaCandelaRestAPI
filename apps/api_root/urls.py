from apps.products.routers import router as products_router
from apps.comments.routers import router as comment_router

app_name = "api"

urlpatterns = []

urlpatterns += products_router.urls + comment_router.urls
