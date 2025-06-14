import requests
import json
import os
import sys
from bs4 import BeautifulSoup

def login_y_probar_endpoint():
    """
    Script para iniciar sesión y luego probar el endpoint de form-data
    """
    print("🔍 VERIFICANDO ENDPOINT DE DATOS DEL FORMULARIO")
    print("===============================================")
    
    # URL del servidor y endpoints
    base_url = "http://127.0.0.1:8000"
    login_url = f"{base_url}/dashboard/login/"
    form_data_url = f"{base_url}/dashboard/insumos/form-data/"
    
    # Crear una sesión para mantener cookies y estado
    session = requests.Session()
    
    try:
        # Paso 1: Obtener el token CSRF de la página de login
        print("1️⃣ Obteniendo token CSRF...")
        login_page = session.get(login_url)
        
        if login_page.status_code != 200:
            print(f"❌ ERROR: No se pudo acceder a la página de login. Status: {login_page.status_code}")
            return None
        
        # Extraer el token CSRF usando BeautifulSoup
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if not csrf_input:
            print("❌ ERROR: No se encontró el token CSRF en la página de login")
            return None
        
        csrf_token = csrf_input.get('value')
        print(f"✅ Token CSRF obtenido: {csrf_token[:10]}...")
        
        # Paso 2: Iniciar sesión
        print("\n2️⃣ Iniciando sesión...")
        login_data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': 'admin',  # Cambiar por el usuario correcto
            'password': 'admin123'  # Cambiar por la contraseña correcta
        }
        
        login_response = session.post(login_url, data=login_data, headers={
            'Referer': login_url
        })
        
        # Verificar si el login fue exitoso (redireccionando a otra página)
        if login_url in login_response.url:
            print("❌ ERROR: Login fallido. Verifica usuario y contraseña.")
            return None
        
        print(f"✅ Login exitoso. Redirigido a: {login_response.url}")
        
        # Paso 3: Acceder al endpoint de datos del formulario
        print("\n3️⃣ Accediendo al endpoint de datos...")
        form_data_response = session.get(form_data_url)
        
        if form_data_response.status_code != 200:
            print(f"❌ ERROR: No se pudo acceder al endpoint. Status: {form_data_response.status_code}")
            print("Contenido:", form_data_response.text[:200] + "..." if len(form_data_response.text) > 200 else form_data_response.text)
            return None
        
        try:
            data = form_data_response.json()
            print("✅ Datos recibidos correctamente")
            
            # Analizar los datos
            categorias = data.get('categorias', [])
            unidades = data.get('unidades', [])
            
            print(f"\nCategorías: {len(categorias)}")
            for i, cat in enumerate(categorias, 1):
                print(f"  {i}. ID: {cat.get('id')}, Nombre: {cat.get('nombre')}")
            
            print(f"\nUnidades: {len(unidades)}")
            for i, uni in enumerate(unidades, 1):
                print(f"  {i}. ID: {uni.get('id')}, Nombre: {uni.get('nombre')}, Abrev: {uni.get('abreviacion')}")
            
            # Verificar si hay datos
            if not categorias:
                print("\n⚠️ ADVERTENCIA: No hay categorías en la base de datos")
            if not unidades:
                print("\n⚠️ ADVERTENCIA: No hay unidades en la base de datos")
            
            # Guardar los datos a un archivo para depuración
            with open("form_data_response.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("\nDatos guardados en form_data_response.json para referencia")
            
            return data
            
        except json.JSONDecodeError:
            print("❌ ERROR: La respuesta no es un JSON válido")
            print("Contenido:", form_data_response.text[:200] + "..." if len(form_data_response.text) > 200 else form_data_response.text)
    
    except requests.RequestException as e:
        print(f"❌ ERROR: Error de conexión: {str(e)}")
        print("Asegúrate de que el servidor Django esté ejecutándose")
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    return None

if __name__ == "__main__":
    print("Probando endpoint de datos del formulario con autenticación...")
    login_y_probar_endpoint()
