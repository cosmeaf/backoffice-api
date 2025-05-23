# seletivo/views/allowed_city_view.py
from rest_framework import viewsets, permissions
from seletivo.models.allowed_city_model import AllowedCity
from seletivo.serializers.allowed_city_serializer import (
    AllowedCitySerializer,
    AllowedCityDetailSerializer
)

class AllowedCityViewSet(viewsets.ModelViewSet):
    queryset = AllowedCity.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return AllowedCityDetailSerializer
        return AllowedCitySerializer
