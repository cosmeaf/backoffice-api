from django.db import models
from seletivo.models.user_data_model import UserData
from seletivo.models.allowed_city_model import AllowedCity

class ExamLocal(models.Model):
    name = models.CharField(max_length=255)
    full_address = models.TextField()
    allowed_city = models.ForeignKey(AllowedCity, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Local de Exame"
        verbose_name_plural = "Locais de Exame"
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

class ExamDate(models.Model):
    local = models.ForeignKey(ExamLocal, on_delete=models.CASCADE, related_name="dates")
    date = models.DateField()

    class Meta:
        verbose_name = "Data de Exame"
        verbose_name_plural = "Datas de Exame"
        indexes = [
            models.Index(fields=["date"]),
        ]

    def __str__(self):
        return f"{self.local.name} - {self.date}"

class ExamHour(models.Model):
    exam_date = models.ForeignKey(ExamDate, on_delete=models.CASCADE, related_name="hours")
    hour = models.TimeField()

    class Meta:
        verbose_name = "Horário de Exame"
        verbose_name_plural = "Horários de Exame"
        indexes = [
            models.Index(fields=["hour"]),
        ]

    def __str__(self):
        return f"{self.exam_date.date} - {self.hour}"

class Exam(models.Model):
    user_data = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='exams')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=50)  # Livre para receber via POST
    exam_scheduled_hour = models.ForeignKey(ExamHour, on_delete=models.SET_NULL, null=True, blank=True, related_name='exams')

    class Meta:
        verbose_name = "Exame"
        verbose_name_plural = "Exames"
        indexes = [
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Exame de {self.user_data.user.get_full_name()} - {self.status}"