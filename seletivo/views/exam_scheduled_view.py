from rest_framework import viewsets, permissions
from seletivo.models.exam_scheduled_model import ExamLocal, ExamDate, ExamHour, Exam
from seletivo.serializers.exam_scheduled_serializer import (
    ExamLocalSerializer,
    ExamDateSerializer,
    ExamHourSerializer,
    ExamSerializer,
    ExamDetailSerializer,
    ExamDateDetailSerializer,
    ExamHourDetailSerializer,
)
from seletivo.models.user_data_model import UserData
from django.contrib.auth.models import AnonymousUser

class PublicReadOnly(permissions.BasePermission):
    """
    Permite acesso público para leitura (GET), mas exige autenticação para criação ou edição.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite acesso ao proprietário ou a um admin.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user_data.user == request.user

# -------------------------------
# VIEWSETS PARA LOCAIS, DATAS, HORAS
# -------------------------------

class ExamLocalViewSet(viewsets.ModelViewSet):
    queryset = ExamLocal.objects.all()
    serializer_class = ExamLocalSerializer
    permission_classes = [PublicReadOnly]

class ExamDateViewSet(viewsets.ModelViewSet):
    queryset = ExamDate.objects.all()
    permission_classes = [PublicReadOnly]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return ExamDateDetailSerializer
        return ExamDateSerializer

class ExamHourViewSet(viewsets.ModelViewSet):
    queryset = ExamHour.objects.all()
    permission_classes = [PublicReadOnly]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return ExamHourDetailSerializer
        return ExamHourSerializer

# -------------------------------
# VIEWSET PARA EXAMES
# -------------------------------

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            # Return empty queryset for unauthenticated users (e.g., Swagger)
            return self.queryset.none()
        if user.is_staff:
            return self.queryset.all()
        return self.queryset.filter(user_data__user=user)

    def get_permissions(self):
        if self.action in ['list', 'create']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return ExamDetailSerializer
        return ExamSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff and self.request.data.get('user_data'):
            serializer.save()
        else:
            serializer.save(user_data=user.user_data)