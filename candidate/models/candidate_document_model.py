from django.db import models
from seletivo.models.user_data_model import UserData

STATUS_CHOICES = [
    ("pending", "Pendente"),
    ("approved", "Aprovado"),
    ("rejected", "Rejeitado"),
]

def id_doc_upload_path(instance, filename):
    return f"candidate_documents/{instance.user_data.id}/id_doc/{filename}"

def address_doc_upload_path(instance, filename):
    return f"candidate_documents/{instance.user_data.id}/address_doc/{filename}"

def school_history_doc_upload_path(instance, filename):
    return f"candidate_documents/{instance.user_data.id}/school_history_doc/{filename}"

def contract_doc_upload_path(instance, filename):
    return f"candidate_documents/{instance.user_data.id}/contract_doc/{filename}"

class CandidateDocument(models.Model):
    user_data = models.OneToOneField(UserData, on_delete=models.CASCADE, related_name='candidate_documents')

    id_doc = models.FileField(upload_to=id_doc_upload_path, null=True, blank=True)
    id_doc_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    id_doc_refuse_reason = models.TextField(null=True, blank=True)

    address_doc = models.FileField(upload_to=address_doc_upload_path, null=True, blank=True)
    address_doc_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    address_doc_refuse_reason = models.TextField(null=True, blank=True)

    school_history_doc = models.FileField(upload_to=school_history_doc_upload_path, null=True, blank=True)
    school_history_doc_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    school_history_doc_refuse_reason = models.TextField(null=True, blank=True)

    contract_doc = models.FileField(upload_to=contract_doc_upload_path, null=True, blank=True)
    contract_doc_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    contract_doc_refuse_reason = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Documentos de {self.user_data}"