"""
Test directo del endpoint de edición
"""
import requests

def test_edit_endpoint():
    # Configurar sesión
    session = requests.Session()
    
    # Hacer login primero
    login_url = "http://127.0.0.1:8000/dashboard/login/"
    login_response = session.get(login_url)
    
    # Extraer CSRF token
    import re
    csrf_token = re.search(r'name="csrfmiddlewaretoken" value="([^"]*)"', login_response.text)
    if not csrf_token:
        print("❌ No se pudo encontrar el token CSRF")
        return
    
    csrf_token = csrf_token.group(1)
    print(f"✅ Token CSRF obtenido: {csrf_token[:10]}...")
    
    # Hacer login
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    login_post = session.post(login_url, data=login_data)
    if login_post.status_code == 200 and 'login' not in login_post.url:
        print("✅ Login exitoso")
    else:
        print(f"❌ Login falló: {login_post.status_code}")
        return
    
    # Primero obtener los datos actuales del insumo
    get_url = "http://127.0.0.1:8000/dashboard/insumos/editar/1/"
    get_response = session.get(get_url)
    
    if get_response.status_code == 200:
        data = get_response.json()
        print(f"✅ Datos actuales del insumo: {data}")
    else:
        print(f"❌ Error al obtener datos: {get_response.status_code}")
        return
    
    # Ahora intentar actualizar
    update_data = {
        'nombre': 'TEST_NOMBRE_EDITADO',
        'categoria': data['categoria'],
        'unidad_medida': data['unidad_medida'],
        'stock_minimo': '10.5',
        'precio_unitario': '25.99',
        'perecedero': 'false'
    }
    
    # Necesitamos el CSRF token para el POST
    inventario_url = "http://127.0.0.1:8000/dashboard/inventario/"
    inventario_response = session.get(inventario_url)
    csrf_token = re.search(r'name="csrfmiddlewaretoken" value="([^"]*)"', inventario_response.text)
    if csrf_token:
        csrf_token = csrf_token.group(1)
    
    headers = {
        'X-CSRFToken': csrf_token,
        'Referer': inventario_url
    }
    
    print(f"📤 Enviando datos de actualización: {update_data}")
    
    update_response = session.post(get_url, data=update_data, headers=headers)
    
    print(f"📥 Respuesta del servidor: {update_response.status_code}")
    
    if update_response.status_code == 200:
        response_data = update_response.json()
        print(f"✅ Respuesta: {response_data}")
        
        if response_data.get('success'):
            print("🎉 ¡Actualización exitosa!")
        else:
            print(f"❌ Error en la actualización: {response_data.get('error')}")
    else:
        print(f"❌ Error HTTP: {update_response.status_code}")
        print(f"Contenido: {update_response.text[:500]}")

if __name__ == "__main__":
    test_edit_endpoint()
