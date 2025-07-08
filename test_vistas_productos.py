import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from accounts.models import Usuario
import json

def test_vista():
    print("\n=== PROBANDO LAS VISTAS DE PRODUCTOS ===")
    print("=" * 50)
    
    # Crear cliente de prueba
    client = Client()
    
    # Intentar obtener un usuario admin
    try:
        user = Usuario.objects.filter(is_superuser=True).first()
        if not user:
            print("No hay usuarios superusuario disponibles")
            return
            
        print(f"Usuario de prueba: {user.username}")
        
        # Hacer login
        client.force_login(user)
        
        # Probar ambas URLs
        urls_to_test = [
            '/dashboard/productos-venta/',
            '/dashboard/productos/'
        ]
        
        for url in urls_to_test:
            print(f"\n--- Probando URL: {url} ---")
            try:
                response = client.get(url)
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.content.decode('utf-8')
                    
                    # Buscar el debug que agregamos
                    if 'DEBUG: Total productos en contexto' in content:
                        start = content.find('DEBUG: Total productos en contexto')
                        end = content.find('</small>', start)
                        debug_info = content[start:end]
                        print(f"Debug encontrado: {debug_info}")
                    
                    # Buscar si aparece el producto en la tabla
                    if 'rollosake' in content:
                        print("✅ Producto 'rollosake' encontrado en la respuesta")
                        
                        # Buscar estado del producto
                        if 'ACTIVO' in content:
                            print("✅ Estado ACTIVO encontrado")
                        if 'INACTIVO' in content:
                            print("✅ Estado INACTIVO encontrado")
                    else:
                        print("❌ Producto 'rollosake' NO encontrado en la respuesta")
                    
                    # Buscar contadores
                    if 'Total:' in content:
                        start = content.find('(Total:')
                        end = content.find(')', start)
                        contador_info = content[start:end+1]
                        print(f"Contadores: {contador_info}")
                        
                elif response.status_code == 404:
                    print("❌ URL no encontrada (404)")
                elif response.status_code == 403:
                    print("❌ Sin permisos (403)")
                else:
                    print(f"❌ Error: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error al probar URL: {str(e)}")
        
    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == '__main__':
    test_vista()
