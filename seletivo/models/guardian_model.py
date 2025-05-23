from django.db import models
from seletivo.models.user_data_model import UserData

class Guardian(models.Model):
    user_data = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='guardians')
    relationship = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14)
    nationality = models.CharField(max_length=100)
    cellphone = models.CharField(max_length=20)
    email = models.EmailField()

    class Meta:
        verbose_name = "Responsável"
        verbose_name_plural = "Responsáveis"
        indexes = [
            models.Index(fields=['cpf', 'name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.relationship})"
