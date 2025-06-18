from django.shortcuts import render
from rest_framework import generics, permissions
from .models import CustomerProfile
from .serializers import CustomerProfileSerializer
# Create your views here.


class CustomerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = CustomerProfile.objects.get_or_create(user=self.request.user)
        return profile
