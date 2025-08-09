from rest_framework import serializers
from student_data.models.student_model import StudentData
from seletivo.models.user_data_model import UserData
import re
import logging

logger = logging.getLogger(__name__)

class UserDataPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = ['id', 'user']
        ref_name = 'StudentDataUserDataPublic'

class StudentDataSerializer(serializers.ModelSerializer):
    user_data = serializers.PrimaryKeyRelatedField(
        queryset=UserData.objects.all(), write_only=True, required=True
    )
    user_data_display = serializers.SerializerMethodField(read_only=True)
    registration = serializers.CharField(max_length=20)
    corp_email = serializers.EmailField()
    monitor = serializers.CharField(max_length=100, allow_blank=True, default='')
    status = serializers.CharField(max_length=50, allow_blank=True, default='active')

    class Meta:
        model = StudentData
        fields = [
            'id', 'user_data', 'user_data_display', 'registration', 'corp_email',
            'monitor', 'status'
        ]
        read_only_fields = ['id', 'user_data_display']
        ref_name = 'StudentDataSerializer'

    def validate_registration(self, value):
        if not re.match(r'^[a-zA-Z0-9]{1,20}$', value):
            raise serializers.ValidationError("Registration must be an alphanumeric code of up to 20 characters (e.g., PDDB0004)")
        if StudentData.objects.filter(registration=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Registration code already exists")
        return value

    def validate_corp_email(self, value):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError("Invalid corporate email format")
        return value

    def get_user_data_display(self, obj):
        if obj.user_data:
            return UserDataPublicSerializer(obj.user_data).data
        return None

    def create(self, validated_data):
        try:
            logger.info(f"Creating student data with validated data: {validated_data}")
            if 'user_data' not in validated_data and self.context['request'].user.is_authenticated:
                user_data = UserData.objects.filter(user=self.context['request'].user).first()
                if not user_data:
                    raise serializers.ValidationError({"user_data": "UserData not found for the current user"})
                validated_data['user_data'] = user_data
            return super().create(validated_data)
        except Exception as e:
            logger.error(f"Error creating student data: {str(e)}")
            raise serializers.ValidationError({"error": str(e)})

    def update(self, instance, validated_data):
        try:
            logger.info(f"Updating student data with validated data: {validated_data}")
            return super().update(instance, validated_data)
        except Exception as e:
            logger.error(f"Error updating student data: {str(e)}")
            raise serializers.ValidationError({"error": str(e)})

class StudentDataDetailSerializer(serializers.ModelSerializer):
    user_data = UserDataPublicSerializer(read_only=True)
    registration = serializers.CharField(max_length=20)
    corp_email = serializers.EmailField()
    monitor = serializers.CharField(max_length=100, allow_blank=True, default='')
    status = serializers.CharField(max_length=50, allow_blank=True, default='active')

    class Meta:
        model = StudentData
        fields = [
            'id', 'user_data', 'registration', 'corp_email',
            'monitor', 'status'
        ]
        read_only_fields = ['id', 'user_data']
        ref_name = 'StudentDataDetailSerializer'

class BatchStudentDataSerializer(serializers.ListSerializer):
    child = StudentDataSerializer()

    def create(self, validated_data):
        profiles = []
        request = self.context.get('request')
        try:
            for data in validated_data:
                user_data = data.pop('user_data', None)
                if not user_data and request.user.is_authenticated:
                    user_data = UserData.objects.filter(user=request.user).first()
                    if not user_data:
                        raise serializers.ValidationError({"user_data": "UserData not found for the current user"})
                elif not request.user.is_staff:
                    raise serializers.ValidationError({"user_data": "Non-staff users can only create their own student data"})
                
                profile, created = StudentData.objects.get_or_create(user_data=user_data)
                serializer = StudentDataSerializer(profile, data=data, partial=True, context={'request': request})
                if serializer.is_valid(raise_exception=True):
                    serializer.save(user_data=user_data)
                    profiles.append(profile)
            return profiles
        except Exception as e:
            logger.error(f"Error in batch create student data: {str(e)}")
            raise serializers.ValidationError({"error": str(e)})