from django.contrib import admin
from seletivo.models.guardian_model import Guardian

@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ('name', 'relationship', 'cpf', 'user_data_column')
    search_fields = ['name', 'cpf', 'user_data__cpf']
    autocomplete_fields = ['user_data']
    ordering = ['name']

    def user_data_column(self, obj):
        return obj.user_data.user.email if obj.user_data and obj.user_data.user else "-"
    user_data_column.short_description = "Usuário"
