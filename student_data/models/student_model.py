from django.db import models
from seletivo.models.user_data_model import UserData
import re

class StudentData(models.Model):
    """
    Model representing student data linked to a UserData instance.
    Stores student-specific information such as registration, corporate email, monitor status, and account status.
    """
    user_data = models.OneToOneField(
        UserData,
        on_delete=models.CASCADE,
        related_name='student_data',
        help_text="The associated user data record."
    )
    registration = models.CharField(
        max_length=20,
        unique=True,
        help_text="A unique alphanumeric registration code (up to 20 characters, e.g., PDDB0004, PDITA001)."
    )
    corp_email = models.EmailField(
        unique=True,
        help_text="Corporate email address for the student."
    )
    monitor = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Text describing the student's monitor status."
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('suspended', 'Suspended')
        ],
        default='active',
        help_text="The student's account status."
    )

    class Meta:
        verbose_name = "Student Data"
        verbose_name_plural = "Student Data"
        ordering = ['registration']
        indexes = [
            models.Index(fields=['registration']),
            models.Index(fields=['corp_email']),
        ]

    def clean(self):
        """
        Validate the registration and corp_email fields before saving.
        """
        if not re.match(r'^[a-zA-Z0-9]{1,20}$', self.registration):
            raise models.ValidationError({
                'registration': "Registration must be an alphanumeric code of up to 20 characters (e.g., PDDB0004)"
            })
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.corp_email):
            raise models.ValidationError({
                'corp_email': "Invalid corporate email format"
            })

    def __str__(self):
        """
        String representation of the StudentData instance.
        """
        try:
            return f"{self.user_data.user.username} - {self.registration}"
        except AttributeError:
            return f"StudentData {self.registration}"