from django.db import models
from django.contrib.auth.models import User

class EnemResult(models.Model):
    STATUS_CHOICES = [
        ("fileSent", "Arquivo Enviado"),
        ("processed", "Processado"),
        ("invalid", "Inválido"),
        ("approved", "Aprovado"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enem_results')
    inscription_number = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True)
    foreign_language = models.CharField(max_length=50)
    languages_score = models.FloatField()
    human_sciences_score = models.FloatField()
    natural_sciences_score = models.FloatField()
    math_score = models.FloatField()
    essay_score = models.FloatField()
    pdf_file = models.FileField(upload_to='enem_pdfs/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="fileSent")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.inscription_number}"

    class Meta:
        verbose_name = "ENEM Result"
        verbose_name_plural = "ENEM Results"
        indexes = [models.Index(fields=['cpf'])]