from django.db import models

class AllowedCity(models.Model):
    localidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cidade Permitida"
        verbose_name_plural = "Cidades Permitidas"
        indexes = [
            models.Index(fields=['localidade', 'uf']),
        ]

    def __str__(self):
        return f"{self.localidade}/{self.uf}"
