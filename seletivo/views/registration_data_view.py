from rest_framework import viewsets, permissions
from seletivo.models.registration_data_model import RegistrationData
from seletivo.serializers.registration_data_serializer import (
    RegistrationDataSerializer,
    RegistrationDataDetailSerializer
)

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user_data.user == request.user

class RegistrationDataViewSet(viewsets.ModelViewSet):
    queryset = RegistrationData.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        return self.queryset.filter(user_data__user=user)

    def get_permissions(self):
        if self.action in ['list', 'create']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return RegistrationDataDetailSerializer
        return RegistrationDataSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff and self.request.data.get("user_data"):
            serializer.save()
        else:
            serializer.save(user_data=user.user_data)
