from django.contrib import admin
from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from .models import City

class CityAdminForm(forms.ModelForm):
    class Meta:
        model = City
        fields = '__all__'

    def clean_user(self):
        user = self.cleaned_data.get('user')
        if not user:
            raise forms.ValidationError('É necessário selecionar um usuário.')
        return user

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    form = CityAdminForm
    list_display = ('cep', 'logradouro', 'bairro', 'localidade', 'uf', 'user_column')
    search_fields = ['cep', 'user__email', 'localidade', 'bairro']
    list_display_links = ('cep', 'user_column')
    autocomplete_fields = ['user']
    ordering = ['-id']
    readonly_fields = []

    class Media:
        js = ('city/scripts.js',)  # opcional, só se quiser JS custom

    def user_column(self, instance):
        return instance.user.email
    user_column.short_description = 'Usuário'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser and form.cleaned_data.get('user'):
            obj.user = form.cleaned_data.get('user')
        elif not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def delete_selected(self, request, queryset):
        queryset.update(deleted_at=timezone.now())  # só funciona se modelo tiver `deleted_at`

    delete_selected.short_description = 'Marcar selecionados como deletados'
