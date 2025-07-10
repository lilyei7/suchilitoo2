from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Lista los usuarios con rol de cocina y mesero en formato simple.'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        roles = ['cocina', 'mesero']
        for rol in roles:
            usuarios = User.objects.filter(rol__nombre__iexact=rol)
            if usuarios.exists():
                self.stdout.write(f"{rol}")
                for user in usuarios:
                    # Si tienes un campo de contraseña en texto plano, cámbialo aquí. Por defecto Django solo almacena el hash.
                    self.stdout.write(f"user {user.username} contrasena {user.password}")
            else:
                self.stdout.write(f"{rol}\nNinguno encontrado.")
