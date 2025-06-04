from rest_framework import serializers
from django.contrib.auth.models import User
from seletivo.models.user_data_model import UserData
from seletivo.models.allowed_city_model import AllowedCity

class AllowedCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowedCity
        fields = ['id', 'localidade', 'uf', 'active']
        ref_name = 'UserDataAllowedCity'  # Evita conflito no Swagger

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        ref_name = 'UserDataUserPublic'  # Evita conflito no Swagger

class UserDataSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='email',
        queryset=User.objects.all()
    )
    allowed_city = serializers.PrimaryKeyRelatedField(
        queryset=AllowedCity.objects.all(),
        allow_null=True
    )

    class Meta:
        model = UserData
        fields = [
            'id', 'cpf', 'birth_date', 'social_name', 'celphone',
            'guardian_email', 'allowed_city', 'user'
        ]
        read_only_fields = ['id']
        ref_name = 'UserData'  # Nome único para o Swagger

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserPublicSerializer(instance.user).data
        data['allowed_city'] = (
            AllowedCitySerializer(instance.allowed_city).data
            if instance.allowed_city else None
        )
        return data

class UserDataDetailSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='email',
        queryset=User.objects.all()
    )
    allowed_city = serializers.PrimaryKeyRelatedField(
        queryset=AllowedCity.objects.all(),
        allow_null=True
    )

    class Meta:
        model = UserData
        fields = [
            'id', 'cpf', 'birth_date', 'social_name', 'celphone',
            'guardian_email', 'allowed_city', 'user'
        ]
        read_only_fields = ['id', 'user']
        ref_name = 'UserDataDetail'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserPublicSerializer(instance.user).data
        data['allowed_city'] = (
            AllowedCitySerializer(instance.allowed_city).data
            if instance.allowed_city else None
        )
        return data