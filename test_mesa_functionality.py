import django
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from mesero.models import Mesa
from accounts.models import Sucursal

User = get_user_model()

def test_mesa_selection():
    """Test the mesa selection functionality"""
    print("=== PRUEBA DE FUNCIONALIDAD DE SELECCIÓN DE MESA ===")
    
    # 1. Crear cliente de prueba
    client = Client()
    
    # 2. Obtener usuario de prueba
    try:
        user = User.objects.get(username='mesero_demo')
        print(f"✓ Usuario encontrado: {user.username}")
        print(f"  - Sucursal: {user.sucursal}")
        print(f"  - Activo: {user.is_active}")
    except User.DoesNotExist:
        print("✗ Usuario mesero_demo no encontrado")
        return False
    
    # 3. Hacer login
    print("\n1. Probando login...")
    login_success = client.login(username='mesero_demo', password='demo123')
    print(f"   Login exitoso: {login_success}")
    
    if not login_success:
        print("   ✗ Error en login")
        return False
    
    # 4. Acceder a la vista de selección de mesa
    print("\n2. Accediendo a selección de mesa...")
    try:
        # Usar la URL correcta
        response = client.get('/mesero/seleccionar-mesa/')
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✓ Vista accesible")
            
            # Verificar el contexto
            context = response.context
            if context:
                mesas = context.get('mesas', [])
                sucursal = context.get('sucursal')
                mesero = context.get('mesero')
                
                print(f"   - Mesas en contexto: {len(mesas)}")
                print(f"   - Sucursal: {sucursal}")
                print(f"   - Mesero: {mesero}")
                
                # Mostrar algunas mesas
                for i, mesa in enumerate(mesas[:3]):
                    print(f"     Mesa {i+1}: {mesa}")
                
                # Verificar contenido HTML
                content = response.content.decode('utf-8')
                if 'Mesa' in content and mesas:
                    print("   ✓ Contenido de mesas encontrado en HTML")
                    return True
                else:
                    print("   ✗ No se encontraron mesas en el HTML")
                    print("   Contenido HTML (primeros 500 chars):")
                    print(content[:500])
                    return False
            else:
                print("   ✗ No hay contexto en la respuesta")
                return False
        else:
            print(f"   ✗ Error en vista: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ✗ Error al acceder a la vista: {e}")
        return False

def verify_database_state():
    """Verify the current database state"""
    print("\n=== VERIFICACIÓN DEL ESTADO DE LA BASE DE DATOS ===")
    
    # Verificar sucursales
    sucursales = Sucursal.objects.all()
    print(f"Sucursales: {sucursales.count()}")
    for sucursal in sucursales:
        print(f"  - {sucursal.nombre} (ID: {sucursal.id})")
    
    # Verificar usuario de prueba
    try:
        user = User.objects.get(username='mesero_demo')
        print(f"\nUsuario mesero_demo:")
        print(f"  - ID: {user.id}")
        print(f"  - Sucursal: {user.sucursal}")
        print(f"  - Activo: {user.is_active}")
        
        # Verificar mesas de su sucursal
        if user.sucursal:
            mesas = Mesa.objects.filter(sucursal=user.sucursal, activa=True)
            print(f"  - Mesas disponibles: {mesas.count()}")
            for mesa in mesas[:3]:
                print(f"    * Mesa {mesa.numero} - Estado: {mesa.estado}")
        else:
            print("  - Sin sucursal asignada")
            
    except User.DoesNotExist:
        print("Usuario mesero_demo no encontrado")

def main():
    """Función principal"""
    try:
        verify_database_state()
        success = test_mesa_selection()
        
        if success:
            print("\n✅ PRUEBA EXITOSA")
            print("   Las mesas se están mostrando correctamente en la vista")
            print("   El usuario puede ver las mesas de su sucursal")
        else:
            print("\n❌ PRUEBA FALLIDA")
            print("   Hay un problema con la visualización de mesas")
            print("   Revisar los logs del servidor Django para más detalles")
            
        print("\n=== PRÓXIMOS PASOS ===")
        print("1. Abrir navegador en: http://127.0.0.1:8000/accounts/login/")
        print("2. Usar credenciales: mesero_demo / demo123")
        print("3. Ir a: http://127.0.0.1:8000/mesero/seleccionar-mesa/")
        print("4. Verificar que se muestren las mesas disponibles")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
