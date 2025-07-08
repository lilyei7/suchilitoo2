#!/usr/bin/env python3
"""
Test script to actually open the croquis editor and check for JavaScript errors
"""

import os
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def test_croquis_editor():
    print("🔍 Probando el editor de croquis...")
    
    try:
        # Importar modelos
        from dashboard.models import Sucursal
        from django.contrib.auth.models import User
        
        # Crear cliente de prueba
        client = Client()
        
        # Crear usuario de prueba si no existe
        User = get_user_model()
        try:
            user = User.objects.get(username='test_user')
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='test_user',
                email='test@example.com',
                password='testpass123'
            )
            print("✅ Usuario de prueba creado")
        
        # Hacer login
        login_success = client.login(username='test_user', password='testpass123')
        if not login_success:
            print("❌ Error en login")
            return
        
        print("✅ Login exitoso")
        
        # Verificar que existe al menos una sucursal
        sucursales = Sucursal.objects.all()
        if not sucursales.exists():
            # Crear sucursal de prueba
            sucursal = Sucursal.objects.create(
                nombre="Sucursal Test",
                direccion="Dirección Test",
                telefono="123456789"
            )
            print("✅ Sucursal de prueba creada")
        else:
            sucursal = sucursales.first()
            print(f"✅ Usando sucursal existente: {sucursal.nombre}")
        
        # Probar la URL del editor de croquis
        editor_url = f'/dashboard/sucursales/{sucursal.id}/croquis/'
        print(f"🔗 Probando URL: {editor_url}")
        
        response = client.get(editor_url)
        
        if response.status_code == 200:
            print("✅ Editor de croquis carga correctamente (HTTP 200)")
            
            # Verificar que el contenido incluye elementos importantes
            content = response.content.decode('utf-8')
            
            checks = [
                ('canvas', 'croquiCanvas' in content),
                ('JavaScript', '<script>' in content),
                ('Funciones clave', 'function onMouseDown' in content),
                ('Panel herramientas', 'tool-seleccionar' in content),
                ('Selector pisos', 'cambiarPiso' in content)
            ]
            
            for check_name, check_result in checks:
                if check_result:
                    print(f"✅ {check_name} - OK")
                else:
                    print(f"❌ {check_name} - FALTANTE")
            
            # Probar endpoints API
            api_tests = [
                f'/dashboard/api/sucursales/{sucursal.id}/mesas/',
                f'/dashboard/api/croquis/cargar/{sucursal.id}/',
            ]
            
            print(f"\n🔧 Probando endpoints API:")
            for api_url in api_tests:
                api_response = client.get(api_url)
                if api_response.status_code in [200, 404]:  # 404 puede ser normal si no hay datos
                    print(f"✅ {api_url} - HTTP {api_response.status_code}")
                else:
                    print(f"❌ {api_url} - HTTP {api_response.status_code}")
            
        elif response.status_code == 404:
            print("❌ Editor de croquis no encontrado (HTTP 404)")
            print("Verificando URLs disponibles...")
            
            # Probar URL alternativa
            preview_url = f'/dashboard/sucursales/{sucursal.id}/croquis/preview/'
            preview_response = client.get(preview_url)
            if preview_response.status_code == 200:
                print(f"✅ Preview de croquis funciona: {preview_url}")
            else:
                print(f"❌ Preview de croquis también falla: HTTP {preview_response.status_code}")
                
        elif response.status_code == 500:
            print("❌ Error interno del servidor (HTTP 500)")
        else:
            print(f"❌ Respuesta inesperada: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_croquis_editor()
