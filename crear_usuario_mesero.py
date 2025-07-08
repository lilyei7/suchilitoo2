from django.contrib.auth import get_user_model
from django.core.management import execute_from_command_line
import os, django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

User = get_user_model()

# Crear usuario de prueba
username = 'mesero1'
password = 'mesero123'

try:
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name='Mesero',
            last_name='Prueba'
        )
        print(f'Usuario {username} creado exitosamente')
        print(f'Contraseña: {password}')
    else:
        print(f'El usuario {username} ya existe')
        print(f'Contraseña: {password}')
except Exception as e:
    print(f'Error al crear usuario: {e}')
