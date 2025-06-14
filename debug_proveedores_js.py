#!/usr/bin/env python3
"""
Debug específico de los errores JavaScript en proveedores
"""

import requests
import json

def debug_javascript_errors():
    """Debug de errores específicos de JavaScript"""
    print("=== DEBUG DE ERRORES JAVASCRIPT EN PROVEEDORES ===\n")
    
    base_url = "http://127.0.0.1:8001"
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # 1. Login
    print("1. Realizando login...")
    login_response = session.get(f"{base_url}/dashboard/login/")
    csrf_token = None
    for line in login_response.text.split('\n'):
        if 'csrfmiddlewaretoken' in line and 'value=' in line:
            start = line.find('value="') + 7
            end = line.find('"', start)
            csrf_token = line[start:end]
            break
    
    login_data = {
        'username': 'admin_test',
        'password': '123456',
        'csrfmiddlewaretoken': csrf_token
    }
    
    session.post(f"{base_url}/dashboard/login/", data=login_data)
    
    # 2. Obtener la página de proveedores y verificar JavaScript
    print("\n2. Analizando JavaScript en la página...")
    proveedores_response = session.get(f"{base_url}/dashboard/proveedores/")
    
    if proveedores_response.status_code == 200:
        content = proveedores_response.text
        
        # Verificar funciones JavaScript clave
        js_functions = [
            'verDetalleProveedor',
            'editarProveedor', 
            'eliminarProveedor',
            'fetch(`/dashboard/proveedor/${proveedorId}/detalle/`)',
        ]
        
        print("Verificando funciones JavaScript:")
        for func in js_functions:
            if func in content:
                print(f"   ✓ {func}: Encontrada")
            else:
                print(f"   ❌ {func}: No encontrada")
        
        # Verificar URLs en el JavaScript
        print("\n3. Verificando URLs en JavaScript...")
        
        # Buscar patrones de URL problemáticos
        problematic_patterns = [
            '/dashboard/proveedor/${proveedorId}/detalle/',
            '/dashboard/proveedor/${proveedorId}/editar/',
            '/dashboard/proveedor/${proveedorId}/eliminar/',
        ]
        
        for pattern in problematic_patterns:
            if pattern in content:
                print(f"   ✓ Patrón encontrado: {pattern}")
                
                # Buscar el contexto alrededor del patrón
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if pattern in line:
                        print(f"   📍 Línea {i+1}: {line.strip()}")
                        # Mostrar líneas de contexto
                        for j in range(max(0, i-2), min(len(lines), i+3)):
                            if j != i:
                                print(f"   {j+1:4}: {lines[j].strip()}")
                        break
            else:
                print(f"   ❌ Patrón no encontrado: {pattern}")
        
        # 4. Test directo de un endpoint específico que causa error
        print(f"\n4. Probando endpoint específico que causaba error...")
        
        # Obtener un ID de proveedor real
        import os
        import django
        import sys
        
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
        django.setup()
        
        from dashboard.models import Proveedor
        proveedor = Proveedor.objects.first()
        
        if proveedor:
            # Test del endpoint que aparecía en el error: proveedor/40/detalle/
            test_url = f"{base_url}/dashboard/proveedor/{proveedor.id}/detalle/"
            test_response = session.get(test_url)
            
            print(f"   URL de prueba: {test_url}")
            print(f"   Status: {test_response.status_code}")
            print(f"   Content-Type: {test_response.headers.get('content-type', 'N/A')}")
            
            if test_response.status_code == 200:
                try:
                    json_data = test_response.json()
                    print(f"   ✅ JSON válido: {json_data.get('success', False)}")
                    if json_data.get('success'):
                        print(f"   ✅ Datos del proveedor cargados correctamente")
                    else:
                        print(f"   ❌ Error en JSON: {json_data.get('message')}")
                except json.JSONDecodeError as e:
                    print(f"   ❌ Error al parsear JSON: {e}")
                    print(f"   Contenido: {test_response.text[:200]}...")
            else:
                print(f"   ❌ Error HTTP: {test_response.status_code}")
                print(f"   Contenido: {test_response.text[:200]}...")
    
    else:
        print(f"❌ No se pudo cargar la página de proveedores: {proveedores_response.status_code}")

if __name__ == '__main__':
    debug_javascript_errors()
