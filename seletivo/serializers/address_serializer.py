from rest_framework import serializers
from django.contrib.auth.models import User
from seletivo.models.address_model import Address


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class AddressSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False
    )
    user_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Address
        fields = [
            'id', 'cep', 'logradouro', 'complemento',
            'bairro', 'localidade', 'uf', 'user', 'user_display',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'user_display', 'created_at', 'updated_at', 'deleted_at']

    def validate_cep(self, value):
        if len(value) not in [8, 9]:
            raise serializers.ValidationError("CEP inválido. Deve conter 8 ou 9 dígitos.")
        return value

    def get_user_display(self, obj):
        if obj.user:
            return UserPublicSerializer(obj.user).data
        return None

    def create(self, validated_data):
        if 'user' not in validated_data and self.context['request'].user.is_authenticated:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AddressDetailSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Address
        fields = [
            'id', 'cep', 'logradouro', 'complemento',
            'bairro', 'localidade', 'uf', 'user',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'deleted_at']
