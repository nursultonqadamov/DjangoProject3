from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import StockEntryViewSet, StockExitViewSet, CurrentStockViewSet

router = DefaultRouter()
router.register(r'entries', StockEntryViewSet)
router.register(r'exits', StockExitViewSet)
router.register(r'current', CurrentStockViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
