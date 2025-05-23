from django.contrib import admin
from seletivo.models.registration_data_model import RegistrationData

@admin.register(RegistrationData)
class RegistrationDataAdmin(admin.ModelAdmin):
    list_display = ('profession', 'education_level', 'user_column')
    search_fields = ('profession', 'education_level', 'user_data__user__email')
    autocomplete_fields = ['user_data']

    def user_column(self, obj):
        return obj.user_data.user.email
    user_column.short_description = 'Usuário'
