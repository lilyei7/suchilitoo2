from django.contrib.auth import get_user_model
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Obtener el modelo de Usuario
User = get_user_model()

def crear_superusuario():
    try:
        User.objects.get(username='admin')
        print("El superusuario 'admin' ya existe")
    except User.DoesNotExist:
        User.objects.create_superuser('admin', 'admin@example.com', 'admin12345')
        print("Superusuario 'admin' creado")

def crear_usuario_mesero():
    try:
        User.objects.get(username='mesero')
        print("El usuario 'mesero' ya existe")
    except User.DoesNotExist:
        user = User.objects.create_user('mesero', 'mesero@example.com', 'mesero12345')
        if hasattr(user, 'rol'):
            user.rol = 'mesero'
            user.save()
        print("Usuario 'mesero' creado")

if __name__ == '__main__':
    print("=== Creando usuarios básicos ===")
    crear_superusuario()
    crear_usuario_mesero()
    print("=== Proceso completado ===")
