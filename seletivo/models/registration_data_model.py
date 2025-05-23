# seletivo/models/registration_data_model.py
from django.db import models
from seletivo.models.user_data_model import UserData

class RegistrationData(models.Model):
    user_data = models.OneToOneField(UserData, on_delete=models.CASCADE, related_name='registration_data')
    profession = models.CharField(max_length=255)
    maritial_status = models.CharField(max_length=50)
    family_income = models.CharField(max_length=100)
    education_level = models.CharField(max_length=100)
    pcd = models.CharField(max_length=255)
    internet_type = models.CharField(max_length=100)
    public_school = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Dados de Registro"
        verbose_name_plural = "Dados de Registro"
        indexes = [models.Index(fields=['profession', 'education_level'])]

    def __str__(self):
        return f"{self.user_data.user.email} - {self.profession}"
