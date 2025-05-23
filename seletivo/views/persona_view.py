from rest_framework import viewsets, permissions
from seletivo.models.persona_model import Persona
from rest_framework import serializers
from seletivo.serializers.persona_serializer import PersonaSerializer, PersonaDetailSerializer

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user_data.user == request.user

class PersonaViewSet(viewsets.ModelViewSet):
    queryset = Persona.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return self.queryset.none()  # Protege o Swagger
        if user.is_staff:
            return self.queryset.all()
        return self.queryset.filter(user_data__user=user)

    def get_permissions(self):
        if self.action in ['list', 'create']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return PersonaDetailSerializer
        return PersonaSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff and self.request.data.get("user_data"):
            serializer.save()
        else:
            # Garante que user_data existe para o usuário
            if hasattr(user, 'user_data'):
                serializer.save(user_data=user.user_data)
            else:
                raise serializers.ValidationError("Usuário não possui dados vinculados (user_data).")
