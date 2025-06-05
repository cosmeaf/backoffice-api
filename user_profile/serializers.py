from rest_framework import serializers
from user_profile.models import UserProfile
from django.contrib.auth.models import User
import re

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        ref_name = 'UserProfileUserPublic'  # Unique ref_name to avoid conflict

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False
    )
    user_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'profile_photo', 'cpf', 'personal_email', 'bio', 'birth_date',
            'hire_date', 'occupation', 'department', 'equipment_patrimony',
            'work_location', 'manager', 'user', 'user_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_display', 'created_at', 'updated_at']

    def validate_cpf(self, value):
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', value):
            raise serializers.ValidationError("CPF must be in the format 000.000.000-00")
        return value

    def validate_profile_photo(self, value):
        if value and value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("Profile photo size exceeds 2MB limit.")
        return value

    def get_user_display(self, obj):
        if obj.user:
            return UserPublicSerializer(obj.user).data
        return None

    def create(self, validated_data):
        if 'user' not in validated_data and self.context['request'].user.is_authenticated:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class UserProfileDetailSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'profile_photo', 'cpf', 'personal_email', 'bio', 'birth_date',
            'hire_date', 'occupation', 'department', 'equipment_patrimony',
            'work_location', 'manager', 'user', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class BatchUserProfileSerializer(serializers.ListSerializer):
    child = UserProfileSerializer()

    def create(self, validated_data):
        profiles = []
        request = self.context.get('request')
        for data in validated_data:
            user = data.pop('user', None)
            if not user and request.user.is_authenticated:
                user = request.user
            elif not request.user.is_staff:
                raise serializers.ValidationError({"user": "Non-staff users can only create their own profile"})
            
            profile, created = UserProfile.objects.get_or_create(user=user)
            serializer = UserProfileSerializer(profile, data=data, partial=True, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=user)
                profiles.append(profile)
        return profiles