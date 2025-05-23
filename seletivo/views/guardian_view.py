from rest_framework import viewsets, permissions
from seletivo.models.guardian_model import Guardian
from seletivo.serializers.guardian_serializer import GuardianSerializer, GuardianDetailSerializer

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user_data.user == request.user

class GuardianViewSet(viewsets.ModelViewSet):
    queryset = Guardian.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        if user.is_authenticated and hasattr(user, 'user_data'):
            return self.queryset.filter(user_data__user=user)
        return Guardian.objects.none()

    def get_permissions(self):
        if self.action in ['list', 'create']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return GuardianDetailSerializer
        return GuardianSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff and self.request.data.get("user_data"):
            serializer.save()
        else:
            if hasattr(user, 'user_data'):
                serializer.save(user_data=user.user_data)
            else:
                raise ValueError("Usuário não possui UserData vinculado.")
