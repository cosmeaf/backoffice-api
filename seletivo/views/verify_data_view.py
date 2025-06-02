from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from seletivo.models.user_data_model import UserData
from seletivo.serializers.verify_data_serializer import VerifyDataSerializer

class VerifyDataViewSet(viewsets.ViewSet):
    """
    Verifica se um CPF já está registrado no sistema.
    Endpoint: /verify-data/cpf/{cpf}
    """
    permission_classes = [AllowAny]
    serializer_class = VerifyDataSerializer

    def retrieve(self, request, pk=None):
        cpf = pk
        if UserData.objects.filter(cpf=cpf).exists():
            return Response({"message": "CPF encontrado."}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)
