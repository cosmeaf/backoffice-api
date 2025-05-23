from rest_framework import serializers
from seletivo.models.guardian_model import Guardian
from seletivo.models.user_data_model import UserData
from seletivo.serializers.user_data_serializer import UserDataSerializer

class GuardianSerializer(serializers.ModelSerializer):
    user_data = serializers.SlugRelatedField(
        slug_field='cpf',
        queryset=UserData.objects.all()
    )

    class Meta:
        model = Guardian
        fields = [
            'id', 'user_data', 'relationship', 'name',
            'cpf', 'nationality', 'cellphone', 'email'
        ]
        read_only_fields = ['id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user_data'] = UserDataSerializer(instance.user_data).data
        return data


class GuardianDetailSerializer(serializers.ModelSerializer):
    user_data = serializers.PrimaryKeyRelatedField(
        queryset=UserData.objects.all()
    )

    class Meta:
        model = Guardian
        fields = [
            'id', 'user_data', 'relationship', 'name',
            'cpf', 'nationality', 'cellphone', 'email'
        ]
        read_only_fields = ['id', 'user_data']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user_data'] = UserDataSerializer(instance.user_data).data
        return data
