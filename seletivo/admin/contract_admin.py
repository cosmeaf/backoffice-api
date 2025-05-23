from django.contrib import admin
from django import forms
from seletivo.models.contract_model import Contract

class ContractAdminForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = '__all__'

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    form = ContractAdminForm
    list_display = ('user_data_column', 'status')
    search_fields = ['user_data__cpf', 'user_data__user__email']
    list_display_links = ('user_data_column',)
    ordering = ['id']
    autocomplete_fields = ['user_data']

    def user_data_column(self, obj):
        return obj.user_data.user.email if obj.user_data and obj.user_data.user else '-'
    user_data_column.short_description = 'Usuário'
