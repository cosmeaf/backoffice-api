from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from user_profile.models import UserProfile
from user_profile.serializers import (
    UserProfileSerializer,
    UserProfileDetailSerializer,
    BatchUserProfileSerializer
)
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
        return request.user.is_staff or obj.user == request.user

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return self.queryset.none()
        if user.is_staff:
            return self.queryset.all()
        return self.queryset.filter(user=user)

    def get_permissions(self):
        if self.action in ['list', 'create', 'batch_create']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return UserProfileDetailSerializer
        elif self.action == 'batch_create':
            return BatchUserProfileSerializer
        return UserProfileSerializer

    @swagger_auto_schema(
        operation_description="Create or update a user profile. Only authenticated users can create/update their own profile. Admins can specify a user ID.",
        request_body=UserProfileSerializer,
        responses={
            201: UserProfileDetailSerializer,
            200: UserProfileDetailSerializer,
            400: openapi.Response("Bad Request", examples={"application/json": {"error": "Invalid data"}}),
            401: openapi.Response("Unauthorized", examples={"application/json": {"detail": "Authentication credentials were not provided."}})
        }
    )
    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"User {request.user} is creating/updating a user profile")
            serializer = self.get_serializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                profile = serializer.save()
                status_code = status.HTTP_201_CREATED if not UserProfile.objects.filter(user=profile.user).exists() else status.HTTP_200_OK
                return Response(UserProfileDetailSerializer(profile).data, status=status_code)
            logger.error(f"Invalid user profile data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating/updating user profile for user {request.user}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Retrieve a user profile. Only the owner or admin can access.",
        responses={
            200: UserProfileDetailSerializer,
            401: openapi.Response("Unauthorized", examples={"application/json": {"detail": "Authentication credentials were not provided."}}),
            403: openapi.Response("Forbidden", examples={"application/json": {"detail": "You do not have permission to perform this action."}}),
            404: openapi.Response("Not Found", examples={"application/json": {"detail": "Not found."}})
        }
    )
    def retrieve(self, request, *args, **kwargs):
        logger.info(f"User {request.user} is retrieving user profile")
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Batch create or update user profiles. Admins can specify user IDs; non-staff users can only create their own profile.",
        request_body=BatchUserProfileSerializer,
        responses={
            201: UserProfileDetailSerializer(many=True),
            400: openapi.Response("Bad Request", examples={"application/json": {"error": "Invalid data"}}),
            401: openapi.Response("Unauthorized", examples={"application/json": {"detail": "Authentication credentials were not provided."}})
        }
    )
    @action(detail=False, methods=['post'], url_path='batch')
    def batch_create(self, request, *args, **kwargs):
        try:
            logger.info(f"User {request.user} is batch creating/updating user profiles")
            serializer = BatchUserProfileSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                profiles = serializer.save()
                return Response(UserProfileDetailSerializer(profiles, many=True).data, status=status.HTTP_201_CREATED)
            logger.error(f"Invalid batch user profile data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error batch creating/updating user profiles for user {request.user}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff and self.request.data.get('user'):
            serializer.save()
        else:
            serializer.save(user=user)