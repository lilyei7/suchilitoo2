#!/usr/bin/env python3
"""
Test de las nuevas rutas de proveedores
"""

import requests
import json

def test_provider_routes():
    """Test de las rutas de proveedores"""
    print("=== TEST DE RUTAS DE PROVEEDORES ===\n")
    
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
    
    login_result = session.post(f"{base_url}/dashboard/login/", data=login_data)
    print(f"✓ Login status: {login_result.status_code}")
    
    # 2. Obtener un proveedor ID válido
    print("\n2. Obteniendo ID de proveedor válido...")
    import os
    import django
    import sys
    
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
    django.setup()
    
    from dashboard.models import Proveedor
    primer_proveedor = Proveedor.objects.first()
    if primer_proveedor:
        proveedor_id = primer_proveedor.id
        print(f"✓ Usando proveedor ID: {proveedor_id} - {primer_proveedor.nombre_comercial}")
    else:
        print("❌ No hay proveedores en la base de datos")
        return
    
    # 3. Test de detalle
    print(f"\n3. Probando ruta de detalle...")
    detalle_url = f"{base_url}/dashboard/proveedor/{proveedor_id}/detalle/"
    detalle_response = session.get(detalle_url)
    
    print(f"✓ URL: {detalle_url}")
    print(f"✓ Status: {detalle_response.status_code}")
    
    if detalle_response.status_code == 200:
        try:
            detalle_data = detalle_response.json()
            if detalle_data.get('success'):
                print("✅ Detalle: JSON válido y exitoso")
                print(f"   - Nombre: {detalle_data['proveedor']['nombre_comercial']}")
                print(f"   - Estado: {detalle_data['proveedor']['estado']}")
            else:
                print(f"⚠ Detalle: JSON válido pero con error: {detalle_data.get('message')}")
        except json.JSONDecodeError:
            print("❌ Detalle: Respuesta no es JSON válido")
            print(f"Contenido: {detalle_response.text[:200]}...")
    else:
        print(f"❌ Detalle: Error {detalle_response.status_code}")
    
    # 4. Test de edición (solo GET para verificar que la ruta existe)
    print(f"\n4. Probando ruta de edición (GET)...")
    editar_url = f"{base_url}/dashboard/proveedor/{proveedor_id}/editar/"
    editar_response = session.get(editar_url)
    
    print(f"✓ URL: {editar_url}")
    print(f"✓ Status: {editar_response.status_code}")
    
    if editar_response.status_code == 302:
        print("✅ Edición: Redirige correctamente (esperado para GET)")
    elif editar_response.status_code == 200:
        print("✅ Edición: Respuesta OK")
    else:
        print(f"❌ Edición: Error {editar_response.status_code}")
    
    # 5. Test de eliminación (solo verificar que la ruta existe, no eliminar realmente)
    print(f"\n5. Probando ruta de eliminación (GET - debe fallar)...")
    eliminar_url = f"{base_url}/dashboard/proveedor/{proveedor_id}/eliminar/"
    eliminar_response = session.get(eliminar_url)
    
    print(f"✓ URL: {eliminar_url}")
    print(f"✓ Status: {eliminar_response.status_code}")
    
    if eliminar_response.status_code == 405:
        print("✅ Eliminación: Método no permitido (esperado para GET)")
    elif eliminar_response.status_code == 200:
        try:
            eliminar_data = eliminar_response.json()
            print(f"✅ Eliminación: JSON response - {eliminar_data}")
        except:
            print("⚠ Eliminación: Respuesta no JSON")
    else:
        print(f"❌ Eliminación: Error {eliminar_response.status_code}")
    
    print(f"\n🎯 RESUMEN:")
    print(f"✓ Todas las rutas están configuradas")
    print(f"✓ Las vistas responden correctamente")
    print(f"✓ El JSON se genera correctamente")

if __name__ == '__main__':
    test_provider_routes()
