from rest_framework import serializers
from seletivo.models.registration_data_model import RegistrationData
from seletivo.models.user_data_model import UserData
from seletivo.serializers.user_data_serializer import UserDataSerializer

class RegistrationDataSerializer(serializers.ModelSerializer):
    user_data = serializers.SlugRelatedField(
        slug_field='cpf',
        queryset=UserData.objects.all()
    )

    class Meta:
        model = RegistrationData
        fields = [
            'id', 'user_data', 'profession', 'maritial_status', 'family_income',
            'education_level', 'pcd', 'internet_type', 'public_school'
        ]
        read_only_fields = ['id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user_data'] = UserDataSerializer(instance.user_data).data
        return data


class RegistrationDataDetailSerializer(serializers.ModelSerializer):
    user_data = serializers.SlugRelatedField(
        slug_field='cpf',
        queryset=UserData.objects.all()
    )

    class Meta:
        model = RegistrationData
        fields = [
            'id', 'user_data', 'profession', 'maritial_status', 'family_income',
            'education_level', 'pcd', 'internet_type', 'public_school'
        ]
        read_only_fields = ['id', 'user_data']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user_data'] = UserDataSerializer(instance.user_data).data
        return data
