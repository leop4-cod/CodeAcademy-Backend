from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.models import User


class Command(BaseCommand):
    help = 'Crea grupos Usuario y Administrador con permisos y un superusuario inicial'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            default='admin@codeacademy.com',
            help='Email del superusuario administrador',
        )
        parser.add_argument(
            '--password',
            default='admin123',
            help='Contraseña del superusuario administrador',
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']

        grupo_usuario, _ = Group.objects.get_or_create(name='Usuario')
        grupo_admin, _ = Group.objects.get_or_create(name='Administrador')

        permisos_vista = Permission.objects.filter(codename__startswith='view_')
        grupo_usuario.permissions.set(permisos_vista)

        permisos_completos = Permission.objects.all()
        grupo_admin.permissions.set(permisos_completos)

        if User.objects.filter(email=email).exists():
            usuario = User.objects.get(email=email)
            self.stdout.write(self.style.WARNING(f'El usuario {email} ya existe.'))
        else:
            usuario = User.objects.create_superuser(
                email=email,
                password=password,
                first_name='Admin',
                last_name='CodeAcademy',
            )
            self.stdout.write(self.style.SUCCESS(f'Superusuario creado: {email}'))

        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.set_password(password)
        usuario.save()
        usuario.groups.add(grupo_admin)

        self.stdout.write(self.style.SUCCESS('Grupos "Usuario" y "Administrador" configurados.'))
