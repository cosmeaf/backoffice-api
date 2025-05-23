from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Cria os grupos de acesso: admin, staff, user'

    def handle(self, *args, **kwargs):
        for role in ['admin', 'staff', 'user']:
            Group.objects.get_or_create(name=role)
        self.stdout.write(self.style.SUCCESS('Grupos criados com sucesso.'))
