from django.db import models
from django.utils import timezone

from user_profile.models import UserProfile           # <-- trocado
from student_data.models.student_model import StudentData

class Psychologist(models.Model):
    user_profile = models.ForeignKey(                 # <-- trocado
        UserProfile,
        on_delete=models.PROTECT,
        related_name="psychologist_links"
    )
    student_data = models.ForeignKey(
        StudentData,
        on_delete=models.CASCADE,
        related_name="psychologist_links"
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Psychologist"
        verbose_name_plural = "Psychologists"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user_profile", "student_data"],
                name="uniq_psychologist_userprofile_student"
            )
        ]
        indexes = [
            models.Index(fields=["user_profile"]),
            models.Index(fields=["student_data"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Psychologist(user_profile={self.user_profile_id}, student={self.student_data_id})"
