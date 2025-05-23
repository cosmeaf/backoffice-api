from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from seletivo.models.user_data_model import UserData
from seletivo.serializers.user_data_serializer import UserDataSerializer, UserDataDetailSerializer

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite apenas ao usuário dono ou admin acessar ou editar.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user

class UserDataViewSet(viewsets.ModelViewSet):
    queryset = UserData.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        return self.queryset.filter(user=user)

    def get_permissions(self):
        if self.action in ['list', 'create']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return UserDataDetailSerializer
        return UserDataSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff and self.request.data.get('user'):
            serializer.save()
        else:
            serializer.save(user=user)
