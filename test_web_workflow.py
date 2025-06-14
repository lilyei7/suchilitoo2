#!/usr/bin/env python
import os
import sys
import django
import requests

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from accounts.models import Usuario

def test_complete_workflow():
    print("=== PRUEBA COMPLETA DEL WORKFLOW DE CREACIÓN DE INSUMO ===")
    
    # Usar requests para simular navegador real
    session = requests.Session()
    base_url = 'http://127.0.0.1:8000'
    
    # 1. Obtener página de login para obtener CSRF token
    print("1. Obteniendo página de login...")
    login_page = session.get(f'{base_url}/dashboard/login/')
    print(f"Status: {login_page.status_code}")
    
    if login_page.status_code != 200:
        print("❌ Error al cargar página de login")
        return
    
    # Extraer CSRF token del HTML
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    
    if not csrf_token:
        print("❌ No se encontró token CSRF en la página de login")
        return
    
    csrf_value = csrf_token['value']
    print(f"✅ Token CSRF obtenido: {csrf_value[:20]}...")
    
    # 2. Hacer login
    print("2. Haciendo login...")
    login_data = {
        'username': 'jhayco',
        'password': 'admin123',
        'csrfmiddlewaretoken': csrf_value
    }
    
    login_response = session.post(f'{base_url}/dashboard/login/', data=login_data)
    print(f"Status login: {login_response.status_code}")
    print(f"URL final: {login_response.url}")
    
    if '/dashboard/' not in login_response.url:
        print("❌ Login falló")
        return
    
    print("✅ Login exitoso")
    
    # 3. Obtener página de inventario
    print("3. Cargando página de inventario...")
    inventario_page = session.get(f'{base_url}/dashboard/inventario/')
    print(f"Status inventario: {inventario_page.status_code}")
    
    if inventario_page.status_code != 200:
        print("❌ Error al cargar página de inventario")
        return
    
    # Extraer nuevo CSRF token de la página de inventario
    soup = BeautifulSoup(inventario_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    
    if csrf_token:
        csrf_value = csrf_token['value']
        print(f"✅ Nuevo token CSRF obtenido: {csrf_value[:20]}...")
    
    print("✅ Página de inventario cargada")
    
    # 4. Probar creación de insumo
    print("4. Creando insumo...")
    insumo_data = {
        'codigo': 'WEB001',
        'nombre': 'Insumo desde Web',
        'categoria': '1',
        'unidad_medida': '1',
        'tipo': 'basico',
        'precio_unitario': '25.75',
        'stock_actual': '75',
        'stock_minimo': '15',
        'csrfmiddlewaretoken': csrf_value
    }
    
    headers = {
        'X-CSRFToken': csrf_value,
        'Referer': f'{base_url}/dashboard/inventario/'
    }
    
    create_response = session.post(f'{base_url}/dashboard/insumos/crear/', 
                                 data=insumo_data, headers=headers)
    print(f"Status crear insumo: {create_response.status_code}")
    
    if create_response.status_code == 200:
        try:
            response_data = create_response.json()
            print(f"Response data: {response_data}")
            
            if response_data.get('success'):
                print("✅ Insumo creado exitosamente desde navegador simulado")
            else:
                print(f"❌ Error en respuesta: {response_data.get('error')}")
        except Exception as e:
            print(f"❌ Error al parsear respuesta JSON: {e}")
            print(f"Contenido: {create_response.text[:200]}...")
    else:
        print(f"❌ Error HTTP: {create_response.status_code}")
        print(f"Contenido: {create_response.text[:200]}...")

if __name__ == "__main__":
    # Verificar que BeautifulSoup esté disponible
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("Instalando BeautifulSoup...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
        from bs4 import BeautifulSoup
    
    test_complete_workflow()
