import os
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

def get_file_path(instance, filename):
    """
    Generate a filename based on user ID and timestamp, preserving the file extension.
    Example: user_6_202506051844.jpg
    """
    ext = filename.split('.')[-1]
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"user_{instance.user.id}_{timestamp}.{ext}"
    return os.path.join('user_profiles', filename)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    profile_photo = models.FileField(upload_to=get_file_path, null=True, blank=True)
    cpf = models.CharField(max_length=14, unique=True, help_text="Format: 000.000.000-00")
    personal_email = models.EmailField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    equipment_patrimony = models.CharField(max_length=50, blank=True)
    work_location = models.CharField(max_length=100, blank=True)
    manager = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

    def delete_old_image(self):
        """
        Delete the existing profile photo file from the filesystem if it exists.
        """
        try:
            old_profile = UserProfile.objects.get(id=self.id)
            if old_profile.profile_photo and old_profile.profile_photo != self.profile_photo:
                if os.path.isfile(old_profile.profile_photo.path):
                    os.remove(old_profile.profile_photo.path)
        except UserProfile.DoesNotExist:
            pass

    def save(self, *args, **kwargs):
        """
        Override save to delete the old image before saving a new one.
        """
        self.delete_old_image()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Override delete to remove the profile photo file before deleting the profile.
        """
        if self.profile_photo and os.path.isfile(self.profile_photo.path):
            os.remove(self.profile_photo.path)
        super().delete(*args, **kwargs)

    class Meta:
        indexes = [models.Index(fields=['user'])]