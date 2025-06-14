import requests
import os
import time
from bs4 import BeautifulSoup

def login_and_check_inventory():    # URL del servidor local
    base_url = "http://127.0.0.1:8000"
    login_url = f"{base_url}/dashboard/login/"
    inventario_url = f"{base_url}/dashboard/inventario/"
    
    # Crear una sesión para mantener las cookies
    session = requests.Session()
    
    try:
        # Primero, obtener el CSRF token de la página de login
        login_response = session.get(login_url)
        if login_response.status_code != 200:
            print(f"❌ No se pudo acceder a {login_url}")
            print(f"Código de estado: {login_response.status_code}")
            return
            
        # Extraer el CSRF token
        soup = BeautifulSoup(login_response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if not csrf_input:
            print("❌ No se pudo encontrar el token CSRF en la página de login")
            return
            
        csrf_token = csrf_input['value']
        
        # Datos para el login
        login_data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': 'admin',  # Cambiar por un usuario válido
            'password': 'admin123'  # Cambiar por la contraseña correcta
        }
        
        # Realizar el login
        login_post = session.post(login_url, data=login_data, headers={
            'Referer': login_url
        })
        
        # Verificar redirección tras el login
        if login_post.url == login_url:  # Si sigue en la página de login, falló
            print("❌ Login fallido. Verifica las credenciales.")
            return
        
        print("✅ Login exitoso")
        
        # Ahora acceder a la página de inventario
        inventario_response = session.get(inventario_url)
        
        # Guardar el contenido HTML de la página de inventario
        html_file_path = os.path.join(os.path.dirname(__file__), "inventario_page_authenticated.html")
        with open(html_file_path, "w", encoding="utf-8") as f:
            f.write(inventario_response.text)
        
        print(f"✅ HTML de inventario guardado en: {html_file_path}")
        
        # Verificar si los scripts JavaScript están presentes
        content = inventario_response.text
        
        # Buscar funciones JavaScript críticas
        js_functions = [
            ('function cargarDatosFormulario()', 'Función de carga de datos'),
            ('function abrirModalCategoria()', 'Función para abrir modal de categoría'),
            ('function abrirModalUnidad()', 'Función para abrir modal de unidad')
        ]
        
        print("\n🔍 VERIFICANDO FUNCIONES JAVASCRIPT:")
        for function_pattern, description in js_functions:
            if function_pattern in content:
                print(f"✅ {description}: ENCONTRADA")
            else:
                print(f"❌ {description}: NO ENCONTRADA")
        
        # Verificar etiquetas de script
        script_open = content.count('<script>')
        script_close = content.count('</script>')
        
        print(f"\n📊 Etiquetas <script>: {script_open}")
        print(f"📊 Etiquetas </script>: {script_close}")
        
        if script_open == script_close:
            print("✅ Etiquetas de script correctamente balanceadas")
        else:
            print(f"❌ Etiquetas de script desbalanceadas")
        
        # Buscar todas las etiquetas script en el HTML
        soup = BeautifulSoup(content, 'html.parser')
        scripts = soup.find_all('script')
        
        print(f"\n📊 Total de etiquetas script encontradas por BeautifulSoup: {len(scripts)}")
        
        # Verificar si extra_js está siendo incluido correctamente
        if "{% block extra_js %}" in content or "{% endblock %}" in content:
            print("❌ Las etiquetas de Django template siguen presentes en el HTML renderizado")
        else:
            print("✅ Las etiquetas de Django template se están renderizando correctamente")
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {str(e)}")

if __name__ == "__main__":
    # Esperar a que el servidor esté listo
    print("Esperando a que el servidor Django esté listo...")
    time.sleep(2)
    login_and_check_inventory()
