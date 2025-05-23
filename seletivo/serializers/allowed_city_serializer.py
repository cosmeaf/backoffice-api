from rest_framework import serializers
from seletivo.models.allowed_city_model import AllowedCity


class AllowedCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowedCity
        fields = ['id', 'localidade', 'uf', 'active']
        read_only_fields = ['id']


class AllowedCityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowedCity
        fields = ['id', 'localidade', 'uf', 'active']
        read_only_fields = ['id']
