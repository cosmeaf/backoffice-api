from django.db import models

class Persona(models.Model):
    user_data = models.OneToOneField("seletivo.UserData", on_delete=models.CASCADE, related_name="persona")
    professional_status = models.CharField("Status Profissional", max_length=255)
    experience = models.TextField("Experiência")
    experience_duration = models.CharField("Duração da Experiência", max_length=100)
    programming_knowledge_level = models.CharField("Nível de Programação", max_length=100)
    motivation_level = models.CharField("Nível de Motivação", max_length=100)
    project_priority = models.CharField("Prioridade de Projeto", max_length=100)
    weekly_available_hours = models.CharField("Horas Semanais Disponíveis", max_length=50)
    study_commitment = models.CharField("Comprometimento com Estudo", max_length=100)
    frustration_handling = models.CharField("Lidar com Frustração", max_length=255)

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        indexes = [
            models.Index(fields=["professional_status"]),
            models.Index(fields=["programming_knowledge_level"]),
        ]

    def __str__(self):
        return f"Persona de {self.user_data.user.get_full_name()}"
