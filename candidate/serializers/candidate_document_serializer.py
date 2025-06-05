from rest_framework import serializers
from candidate.models.candidate_document_model import CandidateDocument
from seletivo.serializers.user_data_serializer import UserDataDetailSerializer

class CandidateDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateDocument
        fields = '__all__'
        read_only_fields = ['user_data', 'created_at']

    def validate_id_doc(self, value):
        if value and value.size > 5 * 1024 * 1024:  # 5MB limit
            raise serializers.ValidationError("File size exceeds 5MB limit.")
        return value

    def validate_address_doc(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size exceeds 5MB limit.")
        return value

    def validate_school_history_doc(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size exceeds 5MB limit.")
        return value

    def validate_contract_doc(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size exceeds 5MB limit.")
        return value

class CandidateDocumentDetailSerializer(serializers.ModelSerializer):
    user_data = UserDataDetailSerializer(read_only=True)

    class Meta:
        model = CandidateDocument
        fields = '__all__'
        read_only_fields = ['user_data', 'created_at']

class SingleDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateDocument
        fields = ['id_doc', 'address_doc', 'school_history_doc', 'contract_doc']

    def validate_id_doc(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size exceeds 5MB limit.")
        return value

    def validate_address_doc(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size exceeds 5MB limit.")
        return value

    def validate_school_history_doc(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size exceeds 5MB limit.")
        return value

    def validate_contract_doc(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size exceeds 5MB limit.")
        return value