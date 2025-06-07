# student_data/admin/student_admin.py
from django.contrib import admin
from student_data.models.student_model import StudentData

@admin.register(StudentData)
class StudentDataAdmin(admin.ModelAdmin):
    list_display = ['user_data', 'registration', 'corp_email', 'monitor', 'status']
