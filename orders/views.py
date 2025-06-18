from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Order
from .serializers import OrderSerializer
# Create your views here.


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
