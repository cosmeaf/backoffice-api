from django.contrib import admin
from django import forms
from seletivo.models.allowed_city_model import AllowedCity

class AllowedCityAdminForm(forms.ModelForm):
    class Meta:
        model = AllowedCity
        fields = '__all__'

@admin.register(AllowedCity)
class AllowedCityAdmin(admin.ModelAdmin):
    form = AllowedCityAdminForm
    list_display = ('localidade', 'uf', 'active')
    search_fields = ['localidade', 'uf']
    list_filter = ['active']
    ordering = ['localidade']
    actions = ['toggle_active']

    def toggle_active(self, request, queryset):
        for city in queryset:
            city.active = not city.active
            city.save()
    toggle_active.short_description = 'Ativar/Inativar cidades selecionadas'
