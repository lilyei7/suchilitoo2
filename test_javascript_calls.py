"""
Script para simular las llamadas JavaScript que están fallando
Prueba los endpoints exactamente como los llama el frontend
"""

import requests
import json

# Configuración
BASE_URL = "http://127.0.0.1:8000"
SESSION = requests.Session()

def login():
    """Iniciar sesión"""
    login_url = f"{BASE_URL}/dashboard/login/"
    
    response = SESSION.get(login_url)
    if response.status_code != 200:
        print(f"❌ Error al acceder a página de login: {response.status_code}")
        return False
    
    # Extraer token CSRF
    import re
    csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
    if not csrf_match:
        print("❌ No se encontró token CSRF")
        return False
    
    csrf_token = csrf_match.group(1)
    
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    response = SESSION.post(login_url, data=login_data)
    if response.status_code == 200 and '/dashboard/' in response.url:
        print("✅ Login exitoso")
        return True
    else:
        print(f"❌ Login fallido: {response.status_code}")
        return False

def test_javascript_calls():
    """Probar las llamadas exactas que hace el JavaScript"""
    print("\n🔍 PROBANDO LLAMADAS JAVASCRIPT...")
    
    # Obtener la página de proveedores
    response = SESSION.get(f"{BASE_URL}/dashboard/proveedores/")
    if response.status_code != 200:
        print(f"❌ Error al acceder a proveedores")
        return False
    
    # Buscar ID de proveedor
    import re
    proveedor_ids = re.findall(r'onclick="verDetalleProveedor\((\d+)\)"', response.text)
    if not proveedor_ids:
        print("❌ No se encontraron proveedores")
        return False
    
    proveedor_id = proveedor_ids[0]
    print(f"✅ Usando proveedor ID: {proveedor_id}")
    
    # Test 1: Ver detalles (sin header AJAX) - debería fallar
    print(f"\n1. Probando VER DETALLES (sin header AJAX)...")
    response = SESSION.get(f"{BASE_URL}/dashboard/proveedor/{proveedor_id}/detalle/")
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
    
    if 'text/html' in response.headers.get('content-type', ''):
        print("❌ Devuelve HTML (causa el error de 'Unexpected token <')")
        print(f"   Contenido: {response.text[:100]}...")
    elif 'application/json' in response.headers.get('content-type', ''):
        print("✅ Devuelve JSON correctamente")
        try:
            data = response.json()
            print(f"   Success: {data.get('success', 'N/A')}")
        except:
            print("❌ JSON inválido")
    
    # Test 2: Ver detalles (con header AJAX) - debería funcionar
    print(f"\n2. Probando VER DETALLES (con header AJAX)...")
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    response = SESSION.get(f"{BASE_URL}/dashboard/proveedor/{proveedor_id}/detalle/", headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
    
    if 'application/json' in response.headers.get('content-type', ''):
        print("✅ Devuelve JSON correctamente")
        try:
            data = response.json()
            print(f"   Success: {data.get('success', 'N/A')}")
            print(f"   Proveedor: {data.get('proveedor', {}).get('nombre_comercial', 'N/A')}")
        except:
            print("❌ JSON inválido")
    else:
        print("❌ No devuelve JSON")
    
    # Test 3: Editar (con header AJAX)
    print(f"\n3. Probando EDITAR (GET con header AJAX)...")
    response = SESSION.get(f"{BASE_URL}/dashboard/proveedor/{proveedor_id}/editar/", headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
    
    if 'application/json' in response.headers.get('content-type', ''):
        print("✅ Devuelve JSON correctamente")
        try:
            data = response.json()
            print(f"   Success: {data.get('success', 'N/A')}")
        except:
            print("❌ JSON inválido")
    else:
        print("❌ No devuelve JSON")
    
    # Test 4: Eliminar (GET - no debería eliminar, solo informar)
    print(f"\n4. Probando ELIMINAR (GET con header AJAX)...")
    response = SESSION.get(f"{BASE_URL}/dashboard/proveedor/{proveedor_id}/eliminar/", headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
    
    if 'application/json' in response.headers.get('content-type', ''):
        print("✅ Devuelve JSON correctamente")
        try:
            data = response.json()
            print(f"   Success: {data.get('success', 'N/A')}")
            print(f"   Message: {data.get('message', 'N/A')}")
        except:
            print("❌ JSON inválido")
    else:
        print("❌ No devuelve JSON")
    
    return True

def main():
    """Función principal"""
    print("🧪 DIAGNÓSTICO DE LLAMADAS JAVASCRIPT")
    print("=" * 50)
    
    try:
        if not login():
            return
        
        test_javascript_calls()
        print("\n✅ DIAGNÓSTICO COMPLETADO")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()
