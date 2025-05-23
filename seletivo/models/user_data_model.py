from django.db import models
from django.contrib.auth.models import User
from seletivo.models.allowed_city_model import AllowedCity

class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_data')
    cpf = models.CharField(max_length=14, unique=True)
    birth_date = models.DateField()
    social_name = models.CharField(max_length=255, blank=True, null=True)
    celphone = models.CharField(max_length=20)
    guardian_email = models.EmailField(blank=True, null=True)
    allowed_city = models.ForeignKey(AllowedCity, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Dados do Usuário"
        verbose_name_plural = "Dados dos Usuários"
        indexes = [models.Index(fields=['cpf'])]

    def __str__(self):
        return f"{self.user.get_full_name()} - CPF: {self.cpf}"
