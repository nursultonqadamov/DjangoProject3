from django.urls import path
from .views import CustomerProfileView

urlpatterns = [
    path('me/', CustomerProfileView.as_view(), name='customer-profile'),
]
