import django
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mesero.models import Mesa
from accounts.models import Sucursal

User = get_user_model()

def configurar_acceso_simple():
    """Configurar acceso simple para meseros"""
    print("=== CONFIGURANDO ACCESO PARA MESEROS ===")
    
    # 1. Crear grupo si no existe
    grupo, created = Group.objects.get_or_create(name='Meseros')
    if created:
        print("✓ Grupo 'Meseros' creado")
    else:
        print("✓ Grupo 'Meseros' ya existe")
    
    # 2. Obtener sucursal
    sucursal = Sucursal.objects.get(nombre="Sucursal Centro")
    print(f"✓ Sucursal encontrada: {sucursal.nombre}")
    
    # 3. Crear usuario de prueba
    username = "mesero_demo"
    password = "demo123"
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@sushi.com',
            'first_name': 'Demo',
            'last_name': 'Mesero',
            'is_active': True,
            'sucursal': sucursal
        }
    )
    
    if created:
        user.set_password(password)
        print(f"✓ Usuario {username} creado")
    else:
        print(f"✓ Usuario {username} ya existe")
    
    # Asegurar que tenga la sucursal y esté activo
    user.sucursal = sucursal
    user.is_active = True
    user.set_password(password)  # Asegurar contraseña
    user.save()
    
    # Añadir al grupo
    user.groups.add(grupo)
    
    print(f"✓ Usuario configurado:")
    print(f"  - Username: {username}")
    print(f"  - Password: {password}")
    print(f"  - Sucursal: {user.sucursal.nombre}")
    print(f"  - Activo: {user.is_active}")
    print(f"  - Grupos: {[g.name for g in user.groups.all()]}")
    
    # 4. Verificar mesas disponibles
    mesas = Mesa.objects.filter(sucursal=sucursal, activa=True)
    print(f"✓ Mesas disponibles en {sucursal.nombre}: {mesas.count()}")
    
    # 5. Mostrar algunas mesas
    print("\n=== MESAS DISPONIBLES ===")
    for mesa in mesas[:5]:
        print(f"  - Mesa {mesa.numero} (ID: {mesa.id}) - Estado: {mesa.get_estado_display()}")
    
    return user

def main():
    """Función principal"""
    try:
        user = configurar_acceso_simple()
        
        print("\n=== INSTRUCCIONES DE PRUEBA ===")
        print("1. Abre tu navegador web")
        print("2. Ve a: http://127.0.0.1:8000/accounts/login/")
        print("3. Ingresa las credenciales:")
        print(f"   - Usuario: {user.username}")
        print("   - Contraseña: demo123")
        print("4. Después del login, ve a: http://127.0.0.1:8000/mesero/seleccionar-mesa/")
        print("5. Deberías ver las mesas disponibles")
        
        print("\n=== DATOS TÉCNICOS ===")
        print(f"- Usuario ID: {user.id}")
        print(f"- Sucursal ID: {user.sucursal.id}")
        print(f"- Mesas en la sucursal: {Mesa.objects.filter(sucursal=user.sucursal, activa=True).count()}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
