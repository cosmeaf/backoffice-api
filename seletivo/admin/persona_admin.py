from django.contrib import admin
from seletivo.models.persona_model import Persona

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = (
        'professional_status', 'programming_knowledge_level',
        'project_priority', 'user_data_column'
    )
    search_fields = ['professional_status', 'user_data__cpf']
    list_display_links = ('professional_status', 'user_data_column')
    ordering = ['user_data__cpf']

    def user_data_column(self, obj):
        return obj.user_data.user.email if obj.user_data and obj.user_data.user else '-'
    user_data_column.short_description = 'Usuário'
