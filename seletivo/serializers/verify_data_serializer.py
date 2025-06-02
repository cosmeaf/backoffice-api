from rest_framework import serializers

class VerifyDataSerializer(serializers.Serializer):
    cpf = serializers.CharField(max_length=14)
