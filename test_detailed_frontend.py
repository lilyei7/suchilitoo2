"""
Simulación detallada del problema de frontend
Reproduce exactamente las condiciones del navegador
"""

import requests
import json
import re

BASE_URL = "http://127.0.0.1:8000"
session = requests.Session()

def get_csrf_token_from_login():
    """Obtener token CSRF de la página de login"""
    response = session.get(f"{BASE_URL}/dashboard/login/")
    csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
    return csrf_match.group(1) if csrf_match else None

def login():
    """Login completo"""
    csrf_token = get_csrf_token_from_login()
    if not csrf_token:
        print("❌ No se pudo obtener CSRF token")
        return False
    
    login_data = {
        'username': 'admin',
        'password': 'admin123', 
        'csrfmiddlewaretoken': csrf_token
    }
    
    response = session.post(f"{BASE_URL}/dashboard/login/", data=login_data)
    return response.status_code == 200 and '/dashboard/' in response.url

def get_csrf_token_from_page():
    """Obtener CSRF token de la página de proveedores"""
    response = session.get(f"{BASE_URL}/dashboard/proveedores/")
    csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
    return csrf_match.group(1) if csrf_match else None

def test_detailed_endpoints():
    """Prueba detallada de endpoints"""
    print("\n🔍 SIMULACIÓN DETALLADA DE FRONTEND")
    
    # Obtener página de proveedores
    response = session.get(f"{BASE_URL}/dashboard/proveedores/")
    if response.status_code != 200:
        print("❌ Error al cargar página de proveedores")
        return
    
    # Extraer ID de proveedor y CSRF token
    proveedor_match = re.search(r'onclick="verDetalleProveedor\((\d+)\)"', response.text)
    csrf_token = get_csrf_token_from_page()
    
    if not proveedor_match:
        print("❌ No se encontró proveedor en la página")
        return
    
    proveedor_id = proveedor_match.group(1)
    print(f"📌 Proveedor ID: {proveedor_id}")
    print(f"📌 CSRF Token: {csrf_token[:20]}..." if csrf_token else "❌ Sin CSRF token")
    
    # Simular headers exactos del navegador
    browser_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': f'{BASE_URL}/dashboard/proveedores/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # Test 1: Ver detalles (simulando fetch desde JavaScript)
    print(f"\n1. 🧪 VER DETALLES (simulando browser fetch)")
    url = f"{BASE_URL}/dashboard/proveedor/{proveedor_id}/detalle/"
    
    response = session.get(url, headers=browser_headers)
    print(f"   URL: {url}")
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type')}")
    print(f"   Content-Length: {len(response.text)}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   ✅ JSON válido")
            print(f"   Success: {data.get('success')}")
            print(f"   Proveedor: {data.get('proveedor', {}).get('nombre_comercial', 'N/A')}")
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON inválido: {e}")
            print(f"   Inicio del contenido: {response.text[:200]}")
    else:
        print(f"   ❌ Error HTTP: {response.status_code}")
        print(f"   Contenido: {response.text[:200]}")
    
    # Test 2: Editar (GET)
    print(f"\n2. 🧪 EDITAR (GET - simulando browser fetch)")
    url = f"{BASE_URL}/dashboard/proveedor/{proveedor_id}/editar/"
    
    response = session.get(url, headers=browser_headers)
    print(f"   URL: {url}")
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type')}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   ✅ JSON válido")
            print(f"   Success: {data.get('success')}")
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON inválido: {e}")
            print(f"   Inicio del contenido: {response.text[:200]}")
    
    # Test 3: Eliminar (POST)
    print(f"\n3. 🧪 ELIMINAR (POST - simulando browser fetch)")
    url = f"{BASE_URL}/dashboard/proveedor/{proveedor_id}/eliminar/"
    
    delete_headers = browser_headers.copy()
    delete_headers.update({
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-CSRFToken': csrf_token
    })
    
    # NO enviar datos para no eliminar realmente, solo probar la ruta
    print("   (Solo probando acceso, sin eliminar)")
    response = session.get(url, headers=browser_headers)  # GET para probar
    
    print(f"   URL: {url}")
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type')}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   ✅ JSON válido")
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON inválido: {e}")
            print(f"   Inicio del contenido: {response.text[:200]}")

def main():
    print("🔬 SIMULACIÓN DETALLADA DE FRONTEND")
    print("=" * 50)
    
    if login():
        print("✅ Login exitoso")
        test_detailed_endpoints()
    else:
        print("❌ Login falló")

if __name__ == "__main__":
    main()
