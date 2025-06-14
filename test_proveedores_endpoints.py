"""
Script para diagnosticar y probar los endpoints de proveedores
Verifica que las rutas respondan correctamente y no den errores 404 o JSON inválido
"""

import requests
import json
import sys

# Configuración
BASE_URL = "http://127.0.0.1:8000"
SESSION = requests.Session()

def login():
    """Iniciar sesión para obtener acceso autenticado"""
    login_url = f"{BASE_URL}/dashboard/login/"
    
    # Primero obtener la página de login para el token CSRF
    response = SESSION.get(login_url)
    if response.status_code != 200:
        print(f"❌ Error al acceder a página de login: {response.status_code}")
        return False
    
    # Extraer token CSRF
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if not csrf_token:
        print("❌ No se encontró token CSRF")
        return False
    
    # Datos de login
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrfmiddlewaretoken': csrf_token['value']
    }
    
    # Intentar login
    response = SESSION.post(login_url, data=login_data)
    if response.status_code == 200 and '/dashboard/' in response.url:
        print("✅ Login exitoso")
        return True
    else:
        print(f"❌ Login fallido: {response.status_code}, URL: {response.url}")
        return False

def test_proveedor_endpoints():
    """Probar los endpoints de proveedores"""
    print("\n🔍 PROBANDO ENDPOINTS DE PROVEEDORES...")
    
    # Primero verificar que existan proveedores
    print("\n1. Verificando lista de proveedores...")
    response = SESSION.get(f"{BASE_URL}/dashboard/proveedores/")
    if response.status_code != 200:
        print(f"❌ Error al acceder a lista de proveedores: {response.status_code}")
        return False
    
    print("✅ Lista de proveedores accesible")
      # Buscar ID de un proveedor en la página
    content = response.text
    import re
    # Buscar en los botones onclick
    proveedor_ids = re.findall(r'onclick="verDetalleProveedor\((\d+)\)"', content)
    
    if not proveedor_ids:
        print("❌ No se encontraron proveedores en la página")
        print("   Contenido de la página (primeros 500 caracteres):")
        print(content[:500])
        return False
    
    proveedor_id = proveedor_ids[0]
    print(f"✅ Encontrado proveedor con ID: {proveedor_id}")
    
    # Probar endpoint de detalle
    print(f"\n2. Probando endpoint de detalle...")
    detalle_url = f"{BASE_URL}/dashboard/proveedor/{proveedor_id}/detalle/"
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    
    response = SESSION.get(detalle_url, headers=headers)
    print(f"   URL: {detalle_url}")
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if data.get('success'):
                print("✅ Endpoint de detalle funciona correctamente")
                print(f"   Proveedor: {data['proveedor']['nombre_comercial']}")
            else:
                print(f"❌ Endpoint devuelve error: {data.get('message', 'Sin mensaje')}")
        except json.JSONDecodeError as e:
            print(f"❌ Respuesta no es JSON válido: {e}")
            print(f"   Contenido: {response.text[:200]}...")
    else:
        print(f"❌ Error {response.status_code} en endpoint de detalle")
        print(f"   Contenido: {response.text[:200]}...")
    
    # Probar endpoint de edición (GET)
    print(f"\n3. Probando endpoint de edición (GET)...")
    editar_url = f"{BASE_URL}/dashboard/proveedor/{proveedor_id}/editar/"
    
    response = SESSION.get(editar_url, headers=headers)
    print(f"   URL: {editar_url}")
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("✅ Endpoint de edición (GET) funciona correctamente")
        except json.JSONDecodeError as e:
            print(f"❌ Respuesta no es JSON válido: {e}")
            print(f"   Contenido: {response.text[:200]}...")
    else:
        print(f"❌ Error {response.status_code} en endpoint de edición")
        print(f"   Contenido: {response.text[:200]}...")
    
    # Probar endpoint de eliminación (GET - no debería eliminar)
    print(f"\n4. Probando endpoint de eliminación (GET)...")
    eliminar_url = f"{BASE_URL}/dashboard/proveedor/{proveedor_id}/eliminar/"
    
    response = SESSION.get(eliminar_url, headers=headers)
    print(f"   URL: {eliminar_url}")
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("✅ Endpoint de eliminación responde (como debe)")
            if not data.get('success'):
                print(f"   Mensaje: {data.get('message', 'Sin mensaje')}")
        except json.JSONDecodeError as e:
            print(f"❌ Respuesta no es JSON válido: {e}")
            print(f"   Contenido: {response.text[:200]}...")
    else:
        print(f"❌ Error {response.status_code} en endpoint de eliminación")
        print(f"   Contenido: {response.text[:200]}...")
    
    return True

def main():
    """Función principal"""
    print("🧪 DIAGNÓSTICO DE ENDPOINTS DE PROVEEDORES")
    print("=" * 50)
    
    try:
        # Instalar dependencia si no está disponible
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            print("📦 Instalando BeautifulSoup...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
            from bs4 import BeautifulSoup
        
        # Hacer login
        if not login():
            return
        
        # Probar endpoints
        if test_proveedor_endpoints():
            print("\n✅ DIAGNÓSTICO COMPLETADO")
        else:
            print("\n❌ DIAGNÓSTICO FALLÓ")
            
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
