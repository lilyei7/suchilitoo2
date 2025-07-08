import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario
from django.contrib.auth.models import Group

print("👤 VERIFICACIÓN DE USUARIOS")
print("=" * 50)

# Buscar todos los usuarios
usuarios = Usuario.objects.all()
print(f"Total usuarios: {usuarios.count()}")

for usuario in usuarios:
    grupos = [grupo.name for grupo in usuario.groups.all()]
    print(f"  - {usuario.username} | Nombre: {usuario.first_name} {usuario.last_name} | Grupos: {grupos}")

# Buscar grupos
grupos = Group.objects.all()
print(f"\nTotal grupos: {grupos.count()}")

for grupo in grupos:
    print(f"  - {grupo.name}")

print("\n🔐 INSTRUCCIONES PARA ACCEDER:")
print("1. Ve a: http://127.0.0.1:8000/")
print("2. Haz login con cualquier usuario")
print("3. Ve a: http://127.0.0.1:8000/mesero/menu/")
print("4. Haz clic en cualquier imagen de producto para ver el modal")

print("\n💡 Si no tienes usuarios, crea uno con:")
print("python manage.py createsuperuser")
