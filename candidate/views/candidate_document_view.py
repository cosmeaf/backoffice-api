from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from candidate.models.candidate_document_model import CandidateDocument
from candidate.serializers.candidate_document_serializer import (
    CandidateDocumentSerializer,
    CandidateDocumentDetailSerializer,
    SingleDocumentSerializer
)
from seletivo.models.user_data_model import UserData
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger(__name__)

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite apenas ao usuário dono ou admin acessar ou editar.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user_data.user == request.user

class CandidateDocumentViewSet(viewsets.ModelViewSet):
    queryset = CandidateDocument.objects.all()

    def get_queryset(self):
        user = self.request.user
        logger.debug(f"User in get_queryset: {user}, is_authenticated: {user.is_authenticated}")
        if user.is_staff:
            return self.queryset.all()
        elif user.is_authenticated:
            return self.queryset.filter(user_data__user=user)
        else:
            return self.queryset.none()

    def get_permissions(self):
        if self.action in ['list', 'create', 'upload_id_doc', 'upload_address_doc', 'upload_school_history_doc', 'upload_contract_doc']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return CandidateDocumentDetailSerializer
        elif self.action in ['upload_id_doc', 'upload_address_doc', 'upload_school_history_doc', 'upload_contract_doc']:
            return SingleDocumentSerializer
        return CandidateDocumentSerializer

    @swagger_auto_schema(
        operation_description="Create a new candidate document. Only authenticated users can create documents.",
        request_body=CandidateDocumentSerializer,
        responses={
            201: CandidateDocumentSerializer,
            400: openapi.Response("Bad Request", examples={"application/json": {"error": "Invalid data"}}),
            401: openapi.Response("Unauthorized", examples={"application/json": {"detail": "Authentication credentials were not provided."}})
        }
    )
    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"User {request.user} is creating a candidate document")
            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error creating candidate document for user {request.user}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Retrieve a candidate document. Only the owner or admin can access.",
        responses={
            200: CandidateDocumentDetailSerializer,
            401: openapi.Response("Unauthorized", examples={"application/json": {"detail": "Authentication credentials were not provided."}}),
            403: openapi.Response("Forbidden", examples={"application/json": {"detail": "You do not have permission to perform this action."}}),
            404: openapi.Response("Not Found", examples={"application/json": {"detail": "Not found."}})
        }
    )
    def retrieve(self, request, *args, **kwargs):
        logger.info(f"User {request.user} is retrieving candidate document")
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff and self.request.data.get('user_data'):
            try:
                user_data_id = self.request.data.get('user_data')
                user_data = UserData.objects.get(id=user_data_id)
                serializer.save(user_data=user_data)
            except UserData.DoesNotExist:
                logger.error(f"UserData with id {user_data_id} does not exist")
                raise serializers.ValidationError({"user_data": "Invalid UserData ID"})
        else:
            try:
                user_data = user.user_data
                serializer.save(user_data=user_data)
            except AttributeError:
                logger.error(f"User {user} does not have associated UserData")
                raise serializers.ValidationError({"user_data": "User has no associated UserData"})

    @swagger_auto_schema(
        operation_description="Upload an ID document for a specific candidate document. Only the owner or admin can upload.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'id_doc': openapi.Schema(type=openapi.TYPE_FILE)},
            required=['id_doc']
        ),
        responses={
            200: CandidateDocumentDetailSerializer,
            400: openapi.Response("Bad Request", examples={"application/json": {"error": "Invalid file"}}),
            401: openapi.Response("Unauthorized", examples={"application/json": {"detail": "Authentication credentials were not provided."}}),
            403: openapi.Response("Forbidden", examples={"application/json": {"detail": "You do not have permission to perform this action."}}),
            404: openapi.Response("Not Found", examples={"application/json": {"detail": "Candidate document not found."}})
        }
    )
    @action(detail=True, methods=['post'], url_path='id-doc')
    def upload_id_doc(self, request, pk=None):
        try:
            obj = self.get_object()
            serializer = self.get_serializer(obj, data={'id_doc': request.data.get('id_doc')}, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"User {request.user} uploaded id_doc for candidate document {pk}")
                return Response(CandidateDocumentDetailSerializer(obj).data, status=status.HTTP_200_OK)
            logger.error(f"Invalid id_doc upload for candidate document {pk}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error uploading id_doc for candidate document {pk}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Upload an address document for a specific candidate document. Only the owner or admin can upload.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'address_doc': openapi.Schema(type=openapi.TYPE_FILE)},
            required=['address_doc']
        ),
        responses={
            200: CandidateDocumentDetailSerializer,
            400: openapi.Response("Bad Request", examples={"application/json": {"error": "Invalid file"}}),
            401: openapi.Response("Unauthorized", examples={"application/json": {"detail": "Authentication credentials were not provided."}}),
            403: openapi.Response("Forbidden", examples={"application/json": {"detail": "You do not have permission to perform this action."}}),
            404: openapi.Response("Not Found", examples={"application/json": {"detail": "Candidate document not found."}})
        }
    )
    @action(detail=True, methods=['post'], url_path='address-doc')
    def upload_address_doc(self, request, pk=None):
        try:
            obj = self.get_object()
            serializer = self.get_serializer(obj, data={'address_doc': request.data.get('address_doc')}, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"User {request.user} uploaded address_doc for candidate document {pk}")
                return Response(CandidateDocumentDetailSerializer(obj).data, status=status.HTTP_200_OK)
            logger.error(f"Invalid address_doc upload for candidate document {pk}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error uploading address_doc for candidate document {pk}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Upload a school history document for a specific candidate document. Only the owner or admin can upload.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'school_history_doc': openapi.Schema(type=openapi.TYPE_FILE)},
            required=['school_history_doc']
        ),
        responses={
            200: CandidateDocumentDetailSerializer,
            400: openapi.Response("Bad Request", examples={"application/json": {"error": "Invalid file"}}),
            401: openapi.Response("Unauthorized", examples={"application/json": {"detail": "Authentication credentials were not provided."}}),
            403: openapi.Response("Forbidden", examples={"application/json": {"detail": "You do not have permission to perform this action."}}),
            404: openapi.Response("Not Found", examples={"application/json": {"detail": "Candidate document not found."}})
        }
    )
    @action(detail=True, methods=['post'], url_path='school-history-doc')
    def upload_school_history_doc(self, request, pk=None):
        try:
            obj = self.get_object()
            serializer = self.get_serializer(obj, data={'school_history_doc': request.data.get('school_history_doc')}, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"User {request.user} uploaded school_history_doc for candidate document {pk}")
                return Response(CandidateDocumentDetailSerializer(obj).data, status=status.HTTP_200_OK)
            logger.error(f"Invalid school_history_doc upload for candidate document {pk}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error uploading school_history_doc for candidate document {pk}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Upload a contract document for a specific candidate document. Only the owner or admin can upload.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'contract_doc': openapi.Schema(type=openapi.TYPE_FILE)},
            required=['contract_doc']
        ),
        responses={
            200: CandidateDocumentDetailSerializer,
            400: openapi.Response("Bad Request", examples={"application/json": {"error": "Invalid file"}}),
            401: openapi.Response("Unauthorized", examples={"application/json": {"detail": "Authentication credentials were not provided."}}),
            403: openapi.Response("Forbidden", examples={"application/json": {"detail": "You do not have permission to perform this action."}}),
            404: openapi.Response("Not Found", examples={"application/json": {"detail": "Candidate document not found."}})
        }
    )
    @action(detail=True, methods=['post'], url_path='contract-doc')
    def upload_contract_doc(self, request, pk=None):
        try:
            obj = self.get_object()
            serializer = self.get_serializer(obj, data={'contract_doc': request.data.get('contract_doc')}, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"User {request.user} uploaded contract_doc for candidate document {pk}")
                return Response(CandidateDocumentDetailSerializer(obj).data, status=status.HTTP_200_OK)
            logger.error(f"Invalid contract_doc upload for candidate document {pk}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error uploading contract_doc for candidate document {pk}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)