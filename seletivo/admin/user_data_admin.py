from django.contrib import admin
from django import forms
from django.contrib.auth.models import User
from seletivo.models.user_data_model import UserData

class UserDataAdminForm(forms.ModelForm):
    class Meta:
        model = UserData
        fields = '__all__'

    def clean_user(self):
        user = self.cleaned_data.get('user')
        if not user:
            raise forms.ValidationError('Usuário é obrigatório.')
        return user

@admin.register(UserData)
class UserDataAdmin(admin.ModelAdmin):
    form = UserDataAdminForm
    list_display = ('cpf', 'birth_date', 'user_column', 'allowed_city_column')
    search_fields = ['cpf', 'user__email', 'social_name']
    list_display_links = ('cpf', 'user_column')
    autocomplete_fields = ['user', 'allowed_city']
    ordering = ['cpf']

    def user_column(self, obj):
        return obj.user.email if obj.user else '-'
    user_column.short_description = 'Usuário'

    def allowed_city_column(self, obj):
        if obj.allowed_city:
            return f"{obj.allowed_city.localidade} - {obj.allowed_city.uf}"
        return '-'
    allowed_city_column.short_description = 'Cidade Permitida'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not change and not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)
