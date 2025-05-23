from django.contrib import admin
from seletivo.models.exam_scheduled_model import ExamLocal, ExamDate, ExamHour

@admin.register(ExamLocal)
class ExamLocalAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_address')
    search_fields = ('name',)

@admin.register(ExamDate)
class ExamDateAdmin(admin.ModelAdmin):
    list_display = ('local', 'date')
    search_fields = ('local__name', 'date')

@admin.register(ExamHour)
class ExamHourAdmin(admin.ModelAdmin):
    list_display = ('exam_date', 'hour')
    search_fields = ('exam_date__date', 'hour')
