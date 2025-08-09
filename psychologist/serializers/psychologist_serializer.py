from rest_framework import serializers
from psychologist.models import Psychologist
from user_profile.models import UserProfile
from student_data.models.student_model import StudentData

# nested (read-only)
class UserProfilePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["id", "user"]  # mantem o "user" como pk (int), conforme seu exemplo

class StudentDataPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentData
        # inclui TODOS os campos do modelo que você passou (inclui user_data como ID)
        fields = ["id", "user_data", "registration", "corp_email", "monitor", "status"]

class PsychologistSerializer(serializers.ModelSerializer):
    # escrita por PK
    user_profile = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), required=True)
    student_data = serializers.PrimaryKeyRelatedField(queryset=StudentData.objects.all(), required=True)

    class Meta:
        model = Psychologist
        fields = ["id", "user_profile", "student_data", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def to_representation(self, instance):
        base = super().to_representation(instance)
        # substitui IDs por objetos aninhados
        base["user_profile"] = UserProfilePublicSerializer(instance.user_profile).data
        base["student_data"] = StudentDataPublicSerializer(instance.student_data).data
        return base
