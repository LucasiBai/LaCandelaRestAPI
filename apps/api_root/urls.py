from apps.products.routers import router as products_router

app_name = "api"

urlpatterns = []

urlpatterns += products_router.urls
