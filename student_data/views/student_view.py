from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from student_data.models.student_model import StudentData
from student_data.serializers.student_serializer import (
    StudentDataSerializer,
    StudentDataDetailSerializer,
    BatchStudentDataSerializer
)
from seletivo.models.user_data_model import UserData
from django.contrib.auth.models import AnonymousUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger(__name__)

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite apenas ao usuário dono ou admin acessar ou editar.
    """
    def has_object_permission(self, request, view, obj):
        try:
            return request.user.is_staff or obj.user_data.user == request.user
        except AttributeError:
            logger.error(f"AttributeError in IsOwnerOrAdmin: user_data or user field missing in {obj}")
            return False

class StudentDataViewSet(viewsets.ModelViewSet):
    queryset = StudentData.objects.all()

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            logger.info("Anonymous user attempted to access StudentData queryset")
            return self.queryset.none()
        if user.is_staff:
            logger.info(f"Admin user {user} accessing full StudentData queryset")
            return self.queryset.all()
        logger.info(f"User {user} accessing own StudentData queryset")
        return self.queryset.filter(user_data__user=user)

    def get_permissions(self):
        if self.action in ['list', 'create', 'batch_create']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return StudentDataDetailSerializer
        elif self.action == 'batch_create':
            return BatchStudentDataSerializer
        return StudentDataSerializer

    @swagger_auto_schema(
        operation_description="Create or update a student data profile. Only authenticated users can create/update their own profile. Admins can specify a user_data ID.",
        request_body=StudentDataSerializer,
        responses={
            201: StudentDataDetailSerializer,
            200: StudentDataDetailSerializer,
            400: openapi.Response("Bad Request", examples={"application/json": {"error": "Invalid data"}}),
            401: openapi.Response("Unauthorized", examples={"application/json": {"detail": "Authentication credentials were not provided."}}),
            403: openapi.Response("Forbidden", examples={"application/json": {"detail": "You do not have permission to perform this action."}})
        }
    )
    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"User {request.user} is creating/updating a student data profile")
            serializer = self.get_serializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                profile = serializer.save()
                status_code = status.HTTP_201_CREATED if not StudentData.objects.filter(user_data=profile.user_data).exists() else status.HTTP_200_OK
                return Response(StudentDataDetailSerializer(profile).data, status=status_code)
            logger.error(f"Invalid student data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating/updating student data for user {request.user}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Retrieve a student data profile. Only the owner or admin can access.",
        responses={
            200: StudentDataDetailSerializer,
            401: openapi.Response("Unauthorized", examples={"application/json": {"detail": "Authentication credentials were not provided."}}),
            403: openapi.Response("Forbidden", examples={"application/json": {"detail": "You do not have permission to perform this action."}}),
            404: openapi.Response("Not Found", examples={"application/json": {"detail": "Not found."}})
        }
    )
    def retrieve(self, request, *args, **kwargs):
        logger.info(f"User {request.user} is retrieving student data profile")
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Batch create or update student data profiles. Admins can specify user_data IDs; non-staff users can only create their own profile.",
        request_body=BatchStudentDataSerializer,
        responses={
            201: StudentDataDetailSerializer(many=True),
            400: openapi.Response("Bad Request", examples={"application/json": {"error": "Invalid data"}}),
            401: openapi.Response("Unauthorized", examples={"application/json": {"detail": "Authentication credentials were not provided."}})
        }
    )
    @action(detail=False, methods=['post'], url_path='batch')
    def batch_create(self, request, *args, **kwargs):
        try:
            logger.info(f"User {request.user} is batch creating/updating student data profiles")
            serializer = BatchStudentDataSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                profiles = serializer.save()
                return Response(StudentDataDetailSerializer(profiles, many=True).data, status=status.HTTP_201_CREATED)
            logger.error(f"Invalid batch student data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error batch creating/updating student data for user {request.user}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff and serializer.validated_data.get('user_data'):
            serializer.save()
        else:
            user_data = UserData.objects.filter(user=user).first()
            if not user_data:
                logger.error(f"No UserData found for user {user}")
                raise serializers.ValidationError({"user_data": "UserData not found for the current user"})
            serializer.save(user_data=user_data)