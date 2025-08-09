from rest_framework import viewsets, permissions, status, serializers, filters
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.models import AnonymousUser
import logging

from psychologist.models import Psychologist
from psychologist.serializers.psychologist_serializer import PsychologistSerializer
from user_profile.models import UserProfile

logger = logging.getLogger(__name__)

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            return request.user.is_staff or obj.user_profile.user == request.user
        except Exception as e:
            logger.error(f"IsOwnerOrAdmin error: {e}")
            return False

class PsychologistViewSet(viewsets.ModelViewSet):
    queryset = Psychologist.objects.select_related(
        "user_profile",
        "student_data",
        "student_data__user_data",  # evita N+1 para nested user_data no StudentData
    ).all()
    serializer_class = PsychologistSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "student_data__registration",
        "student_data__corp_email",
        "user_profile__user__username",
        "user_profile__user__email",
    ]
    ordering_fields = ["created_at", "updated_at", "id"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return self.queryset.none()
        return self.queryset if user.is_staff else self.queryset.filter(user_profile__user=user)

    def get_permissions(self):
        if self.action in ["list", "create"]:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        return [p() for p in permission_classes]

    @swagger_auto_schema(
        operation_description="Cria vínculo Psychologist (user_profile x student_data). Admin pode definir qualquer user_profile; usuário comum só cria vínculos do próprio perfil.",
        request_body=PsychologistSerializer,
        responses={201: PsychologistSerializer, 400: openapi.Response("Bad Request")}
    )
    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        data = ser.validated_data.copy()

        if not request.user.is_staff:
            up = UserProfile.objects.filter(user=request.user).first()
            if not up:
                raise serializers.ValidationError({"user_profile": "UserProfile not found for current user"})
            data["user_profile"] = up

        obj = Psychologist.objects.create(**data)
        return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)
