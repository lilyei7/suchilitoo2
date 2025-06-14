"""
Prueba rápida de las funcionalidades de asignación de insumos a proveedores
"""

import requests
import json
import re

BASE_URL = "http://127.0.0.1:8000"
session = requests.Session()

def login():
    """Login rápido"""
    response = session.get(f"{BASE_URL}/dashboard/login/")
    csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
    if not csrf_match:
        return False
    
    csrf_token = csrf_match.group(1)
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    response = session.post(f"{BASE_URL}/dashboard/login/", data=login_data)
    return response.status_code == 200 and '/dashboard/' in response.url

def test_insumos_endpoints():
    """Probar endpoints de insumos"""
    print("🔍 PROBANDO ENDPOINTS DE INSUMOS...")
    
    # Headers para AJAX
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    
    # Test 1: Obtener insumos disponibles
    print("\n1. Probando /dashboard/proveedores/insumos-disponibles/")
    response = session.get(f"{BASE_URL}/dashboard/proveedores/insumos-disponibles/?proveedor_id=42", headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   ✅ JSON válido")
            print(f"   Success: {data.get('success')}")
            print(f"   Insumos disponibles: {len(data.get('insumos', []))}")
            if data.get('insumos'):
                print(f"   Primer insumo: {data['insumos'][0]['nombre']}")
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON inválido: {e}")
            print(f"   Contenido: {response.text[:200]}")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Contenido: {response.text[:200]}")
    
    # Test 2: Endpoint de asignar insumo (solo verificar que existe)
    print("\n2. Verificando /dashboard/proveedor/42/asignar-insumo/")
    # Obtener CSRF token
    csrf_response = session.get(f"{BASE_URL}/dashboard/proveedores/")
    csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', csrf_response.text)
    csrf_token = csrf_match.group(1) if csrf_match else None
    
    if csrf_token:
        test_headers = headers.copy()
        test_headers['X-CSRFToken'] = csrf_token
        
        # Solo hacer un POST vacío para ver si la ruta existe
        response = session.post(f"{BASE_URL}/dashboard/proveedor/42/asignar-insumo/", 
                              headers=test_headers, data={})
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Endpoint existe y responde JSON")
                print(f"   Message: {data.get('message', 'N/A')}")
            except:
                print(f"   ⚠️ Endpoint existe pero respuesta no es JSON")
        else:
            print(f"   ❌ Error: {response.status_code}")
    else:
        print("   ❌ No se pudo obtener CSRF token")

def main():
    print("🧪 PRUEBA DE ENDPOINTS DE INSUMOS")
    print("=" * 40)
    
    if login():
        print("✅ Login exitoso")
        test_insumos_endpoints()
        print("\n✅ Pruebas completadas")
    else:
        print("❌ Login falló")

if __name__ == "__main__":
    main()
