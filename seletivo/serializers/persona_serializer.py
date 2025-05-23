from rest_framework import serializers
from seletivo.models.persona_model import Persona
from seletivo.models.user_data_model import UserData
from seletivo.serializers.user_data_serializer import UserDataDetailSerializer

class PersonaSerializer(serializers.ModelSerializer):
    user_data = serializers.SlugRelatedField(
        slug_field='cpf',
        queryset=UserData.objects.all()
    )

    class Meta:
        model = Persona
        fields = [
            'id', 'user_data', 'professional_status', 'experience', 'experience_duration',
            'programming_knowledge_level', 'motivation_level', 'project_priority',
            'weekly_available_hours', 'study_commitment', 'frustration_handling'
        ]
        read_only_fields = ['id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user_data'] = UserDataDetailSerializer(instance.user_data).data
        return data


class PersonaDetailSerializer(serializers.ModelSerializer):
    user_data = serializers.PrimaryKeyRelatedField(
        queryset=UserData.objects.all()
    )

    class Meta:
        model = Persona
        fields = [
            'id', 'user_data', 'professional_status', 'experience', 'experience_duration',
            'programming_knowledge_level', 'motivation_level', 'project_priority',
            'weekly_available_hours', 'study_commitment', 'frustration_handling'
        ]
        read_only_fields = ['id', 'user_data']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user_data'] = UserDataDetailSerializer(instance.user_data).data
        return data
