from rest_framework import serializers
from seletivo.models.allowed_city_model import AllowedCity
from seletivo.models.exam_scheduled_model import (
    ExamLocal, ExamDate, ExamHour, Exam
)
from seletivo.models.user_data_model import UserData
from seletivo.serializers.user_data_serializer import UserDataSerializer


class AllowedCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowedCity
        fields = ['id', 'localidade', 'uf', 'active']
        read_only_fields = ['id']


class ExamLocalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamLocal
        fields = ['id', 'name', 'full_address', 'allowed_city']
        read_only_fields = ['id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.allowed_city:
            data['allowed_city'] = AllowedCitySerializer(instance.allowed_city).data
        return data


class ExamDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamDate
        fields = ['id', 'local', 'date']
        read_only_fields = ['id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['local'] = ExamLocalSerializer(instance.local).data
        return data


class ExamHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamHour
        fields = ['id', 'exam_date', 'hour']
        read_only_fields = ['id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['exam_date'] = ExamDateSerializer(instance.exam_date).data
        return data


class ExamDateDetailSerializer(serializers.ModelSerializer):
    local = ExamLocalSerializer(read_only=True)

    class Meta:
        model = ExamDate
        fields = ['id', 'local', 'date']
        read_only_fields = ['id']


class ExamHourDetailSerializer(serializers.ModelSerializer):
    exam_date = ExamDateDetailSerializer(read_only=True)

    class Meta:
        model = ExamHour
        fields = ['id', 'exam_date', 'hour']
        read_only_fields = ['id']


class ExamSerializer(serializers.ModelSerializer):
    user_data = serializers.SlugRelatedField(
        slug_field='cpf',
        queryset=UserData.objects.all()
    )

    class Meta:
        model = Exam
        fields = ['id', 'user_data', 'score', 'status', 'exam_scheduled_hour']
        read_only_fields = ['id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user_data'] = UserDataSerializer(instance.user_data).data
        data['exam_scheduled_hour'] = ExamHourDetailSerializer(instance.exam_scheduled_hour).data if instance.exam_scheduled_hour else None
        return data


class ExamDetailSerializer(serializers.ModelSerializer):
    user_data = serializers.PrimaryKeyRelatedField(queryset=UserData.objects.all())

    class Meta:
        model = Exam
        fields = ['id', 'user_data', 'score', 'status', 'exam_scheduled_hour']
        read_only_fields = ['id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user_data'] = UserDataSerializer(instance.user_data).data
        data['exam_scheduled_hour'] = ExamHourDetailSerializer(instance.exam_scheduled_hour).data if instance.exam_scheduled_hour else None
        return data
