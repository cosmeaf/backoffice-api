from rest_framework import serializers
from seletivo.models.contract_model import Contract
from seletivo.models.user_data_model import UserData
from seletivo.models.guardian_model import Guardian  # ✅ IMPORTAÇÃO FALTANTE
from seletivo.serializers.user_data_serializer import UserDataSerializer
from seletivo.serializers.address_serializer import AddressSerializer
from seletivo.serializers.guardian_serializer import GuardianSerializer
from seletivo.serializers.registration_data_serializer import RegistrationDataSerializer


class ContractSerializer(serializers.ModelSerializer):
    user_data = serializers.SlugRelatedField(
        slug_field='cpf',
        queryset=UserData.objects.all()
    )

    class Meta:
        model = Contract
        fields = ['id', 'user_data', 'status']
        read_only_fields = ['id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user_data_obj = instance.user_data

        data['user_data'] = UserDataSerializer(user_data_obj).data
        data['addresses'] = AddressSerializer(
            user_data_obj.user.addresses.all(), many=True
        ).data

        registration_data = getattr(user_data_obj, 'registration_data', None)
        data['registration_data'] = (
            RegistrationDataSerializer(registration_data).data if registration_data else {}
        )

        guardian = Guardian.objects.filter(user_data=user_data_obj).first()
        data['guardian'] = (
            GuardianSerializer(guardian).data if guardian else {}
        )

        return data
