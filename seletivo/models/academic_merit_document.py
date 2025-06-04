from django.db import models
from seletivo.models.user_data_model import UserData

class AcademicMeritDocument(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pendente'),
        ('APPROVED', 'Aprovado'),
        ('REJECTED', 'Recusado'),
    )

    user_data = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='academic_merit_documents')
    document = models.FileField(upload_to='academic_merit_documents/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Document {self.id} - {self.user_data.user.get_full_name()} - {self.status}"