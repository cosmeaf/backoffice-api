from django.contrib import admin
from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from seletivo.models.address_model import Address

class AddressAdminForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'

    def clean_user(self):
        user = self.cleaned_data.get('user')
        if not user:
            raise forms.ValidationError('É necessário selecionar um usuário.')
        return user

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    form = AddressAdminForm
    list_display = (
        'cep', 'logradouro', 'complemento', 'bairro', 'localidade', 'uf', 'user_column'
    )
    search_fields = ['cep', 'user__email', 'bairro', 'localidade']
    list_display_links = ('cep', 'user_column')
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    autocomplete_fields = ['user']
    ordering = ['created_at']
    actions = ['delete_selected']

    class Media:
        js = ('address/scripts.js',)

    def user_column(self, obj):
        return obj.user.email if obj.user else '-'
    user_column.short_description = 'Usuário'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not change and not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def delete_selected(self, request, queryset):
        for obj in queryset:
            obj.deleted_at = timezone.now()
            obj.save()
    delete_selected.short_description = 'Marcar selecionados como deletados'
