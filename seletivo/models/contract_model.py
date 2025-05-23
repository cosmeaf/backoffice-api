from django.db import models
from seletivo.models.user_data_model import UserData

class Contract(models.Model):
    user_data = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='contracts')
    status = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        indexes = [models.Index(fields=['status'])]

    def __str__(self):
        return f"Contrato - {self.user_data.user.get_full_name()} - {self.status}"
