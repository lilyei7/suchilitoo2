#!/usr/bin/env python3
"""
Test para verificar la vista del croquis
"""
import os
import django
import sys

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test.client import Client
from accounts.models import Usuario
from accounts.models import Sucursal

def test_croquis_view():
    print("🔍 TEST DE LA VISTA DEL CROQUIS")
    print("=" * 40)
    
    # 1. Verificar que la sucursal existe
    try:
        sucursal = Sucursal.objects.get(id=3)
        print(f"✅ Sucursal encontrada: {sucursal.nombre}")
    except Sucursal.DoesNotExist:
        print("❌ Sucursal con ID 3 no existe")
        return
    
    # 2. Crear cliente de test
    client = Client()
    
    # 3. Crear/obtener usuario de test
    try:
        user = Usuario.objects.filter(is_superuser=True).first()
        if not user:
            print("❌ No se encontró usuario superuser")
            return
        print(f"✅ Usuario encontrado: {user.username}")
    except Exception as e:
        print(f"❌ Error obteniendo usuario: {e}")
        return
    
    # 4. Hacer login
    client.force_login(user)
    print("✅ Login forzado exitoso")
    
    # 5. Test de la URL del croquis
    url = f'/dashboard/croquis/{sucursal.id}/'
    print(f"📡 Testeando URL: {url}")
    
    try:
        response = client.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Vista carga correctamente")
            print(f"Template utilizado: {response.templates[0].name if response.templates else 'N/A'}")
        else:
            print(f"❌ Error en la vista: {response.status_code}")
            if hasattr(response, 'content'):
                content = response.content.decode()[:500]
                print(f"Contenido (primeros 500 chars): {content}")
                
    except Exception as e:
        print(f"❌ Excepción en test: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
    
    print("\n" + "=" * 40)
    print("TEST COMPLETADO")

if __name__ == '__main__':
    test_croquis_view()
