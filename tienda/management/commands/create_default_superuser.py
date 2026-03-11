import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Crea el superusuario por defecto si no existe (no interactivo)'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')

        if User.objects.filter(username=username).exists():
            self.stdout.write(f'  Superusuario "{username}" ya existe — omitiendo.')
            return

        User.objects.create_superuser(username=username, password=password, email=email)
        self.stdout.write(self.style.SUCCESS(
            f'  Superusuario creado: usuario="{username}" contraseña="{password}"'
        ))
        self.stdout.write(self.style.WARNING(
            '  Cambia la contraseña en producción: DJANGO_SUPERUSER_PASSWORD en .env'
        ))
