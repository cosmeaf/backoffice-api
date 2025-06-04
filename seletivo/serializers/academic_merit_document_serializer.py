from rest_framework import serializers
from seletivo.models.academic_merit_document import AcademicMeritDocument
from seletivo.models.user_data_model import UserData
from django.contrib.auth.models import User

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        ref_name = 'AcademicMeritUserPublic'  # Evita conflito no Swagger

class UserDataPublicSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = UserData
        fields = ['id', 'user']
        ref_name = 'AcademicMeritUserDataPublic'  # Nome único para o Swagger

class AcademicMeritDocumentSerializer(serializers.ModelSerializer):
    user_data = serializers.PrimaryKeyRelatedField(
        queryset=UserData.objects.all(), write_only=True, required=False
    )
    user_data_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AcademicMeritDocument
        fields = ['id', 'user_data', 'user_data_display', 'document', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_data_display', 'status', 'created_at', 'updated_at']
        ref_name = 'AcademicMeritDocument'

    def get_user_data_display(self, obj):
        if obj.user_data:
            return UserDataPublicSerializer(obj.user_data).data
        return None

    def create(self, validated_data):
        if 'user_data' not in validated_data and self.context['request'].user.is_authenticated:
            try:
                validated_data['user_data'] = UserData.objects.get(user=self.context['request'].user)
            except UserData.DoesNotExist:
                raise serializers.ValidationError("Usuário não possui UserData vinculado.")
        return super().create(validated_data)

class AcademicMeritDocumentDetailSerializer(serializers.ModelSerializer):
    user_data = UserDataPublicSerializer(read_only=True)

    class Meta:
        model = AcademicMeritDocument
        fields = ['id', 'user_data', 'document', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_data', 'status', 'created_at', 'updated_at']
        ref_name = 'AcademicMeritDocumentDetail'