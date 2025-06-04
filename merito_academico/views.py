from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, serializers
from seletivo.models.user_data_model import UserData
from seletivo.models.academic_merit_document import AcademicMeritDocument
from seletivo.serializers.academic_merit_document_serializer import AcademicMeritDocumentSerializer, AcademicMeritDocumentDetailSerializer
from django.http import HttpResponse
import logging
from .utils.generate_docx import generate_docx
from .utils.generate_pdf import convert_to_pdf
import os

logger = logging.getLogger(__name__)

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff or (request.user.is_authenticated and hasattr(request.user, 'user_data'))

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, AcademicMeritDocument):
            return request.user.is_staff or obj.user_data.user == request.user
        return request.user.is_staff or obj.user == request.user

class RecommendationLetterViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action == 'generate_recommendation_letter':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'], url_path='generate-letter')
    def generate_recommendation_letter(self, request):
        """Gera a carta de recomendação em PDF e retorna para download."""
        required_fields = ['school_name', 'school_Principal_Name', 'school_complete_address', 'HighSchool_score']
        missing_fields = [field for field in required_fields if not request.data.get(field)]
        if missing_fields:
            logger.error(f"Campos faltando: {missing_fields}")
            return Response({'error': f'Campos obrigatórios faltando: {", ".join(missing_fields)}'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            float(request.data['HighSchool_score'])
        except ValueError:
            logger.error("HighSchool_score inválido")
            return Response({'error': 'HighSchool_score deve ser um número válido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user
            if user.is_staff and request.data.get('user_id'):
                try:
                    user_info = UserData.objects.get(user__id=request.data['user_id'])
                except UserData.DoesNotExist:
                    logger.error("UserData não encontrado para user_id fornecido")
                    return Response({'error': 'UserData não encontrado para o user_id fornecido'}, status=status.HTTP_404_NOT_FOUND)
            else:
                try:
                    user_info = UserData.objects.get(user=user)
                except UserData.DoesNotExist:
                    logger.error("UserData não encontrado para o usuário autenticado")
                    return Response({'error': 'Usuário não possui UserData vinculado'}, status=status.HTTP_404_NOT_FOUND)

            data = request.data.copy()
            data['first_name'] = user_info.user.first_name
            data['last_name'] = user_info.user.last_name

            temp_docx_path = generate_docx(data)
            pdf_path = convert_to_pdf(temp_docx_path)

            with open(pdf_path, 'rb') as pdf_file:
                pdf_content = pdf_file.read()

            response = HttpResponse(
                pdf_content,
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="carta_recomendacao.pdf"'

            os.remove(temp_docx_path)
            os.remove(pdf_path)
            logger.info(f"Arquivos temporários removidos: {temp_docx_path}, {pdf_path}")

            return response
        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {str(e)}")
            if 'temp_docx_path' in locals() and os.path.exists(temp_docx_path):
                os.remove(temp_docx_path)
            return Response({'error': f'Erro ao gerar PDF: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AcademicMeritDocumentViewSet(viewsets.ModelViewSet):
    queryset = AcademicMeritDocument.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        if user.is_authenticated and hasattr(user, 'user_data'):
            return self.queryset.filter(user_data__user=user)
        return AcademicMeritDocument.objects.none()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['approve', 'recuse']:
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return AcademicMeritDocumentDetailSerializer
        return AcademicMeritDocumentSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff and self.request.data.get("user_data"):
            serializer.save()
        else:
            try:
                serializer.save(user_data=user.user_data)
            except AttributeError:
                logger.error("Usuário não possui UserData vinculado")
                raise serializers.ValidationError("Usuário não possui UserData vinculado.")

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """Aprova o documento especificado."""
        try:
            document = self.get_object()
            if document.status != 'PENDING':
                logger.warning(f"Tentativa de aprovar documento não pendente: {document.id}")
                return Response({'error': 'Documento já foi processado'}, status=status.HTTP_400_BAD_REQUEST)
            
            document.status = 'APPROVED'
            document.save()
            logger.info(f"Documento {document.id} aprovado")
            return Response({'status': 'Documento aprovado'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Erro ao aprovar documento {pk}: {str(e)}")
            return Response({'error': f'Erro ao aprovar documento: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='recuse')
    def recuse(self, request, pk=None):
        """Recusa o documento especificado."""
        try:
            document = self.get_object()
            if document.status != 'PENDING':
                logger.warning(f"Tentativa de recusar documento não pendente: {document.id}")
                return Response({'error': 'Documento já foi processado'}, status=status.HTTP_400_BAD_REQUEST)
            
            document.status = 'REJECTED'
            document.save()
            logger.info(f"Documento {document.id} recusado")
            return Response({'status': 'Documento recusado'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Erro ao recusar documento {pk}: {str(e)}")
            return Response({'error': f'Erro ao recusar documento: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)