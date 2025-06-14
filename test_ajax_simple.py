#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple del endpoint de proveedores
"""

import os
import django
import sys
import requests

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_restaurant.settings')
django.setup()

def test_proveedor_endpoint():
    """Test del endpoint de crear proveedor"""
    print("🧪 Probando endpoint de crear proveedor...")
    
    # URL del endpoint
    url = "http://127.0.0.1:8000/dashboard/crear-proveedor/"
    
    # Primero hacer login para obtener las cookies de sesión
    session = requests.Session()
    
    try:
        # Obtener el formulario de login para el CSRF token
        login_page = session.get("http://127.0.0.1:8000/accounts/login/")
        if login_page.status_code != 200:
            print(f"❌ Error accediendo a página de login: {login_page.status_code}")
            return
        
        # Extraer CSRF token del HTML
        csrf_token = None
        for line in login_page.text.split('\n'):
            if 'csrfmiddlewaretoken' in line and 'value=' in line:
                csrf_token = line.split('value="')[1].split('"')[0]
                break
        
        if not csrf_token:
            print("❌ No se pudo obtener CSRF token")
            return
        
        print(f"🔑 CSRF token obtenido: {csrf_token[:10]}...")
        
        # Hacer login
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'csrfmiddlewaretoken': csrf_token
        }
        
        login_response = session.post("http://127.0.0.1:8000/accounts/login/", data=login_data)
        
        if login_response.status_code not in [200, 302]:
            print(f"❌ Error en login: {login_response.status_code}")
            return
        
        print("✅ Login exitoso")
        
        # Obtener página de proveedores para el nuevo CSRF token
        proveedores_page = session.get("http://127.0.0.1:8000/dashboard/proveedores/")
        if proveedores_page.status_code != 200:
            print(f"❌ Error accediendo a proveedores: {proveedores_page.status_code}")
            return
        
        # Extraer nuevo CSRF token
        csrf_token = None
        for line in proveedores_page.text.split('\n'):
            if 'csrfmiddlewaretoken' in line and 'value=' in line:
                csrf_token = line.split('value="')[1].split('"')[0]
                break
        
        if not csrf_token:
            print("❌ No se pudo obtener CSRF token de proveedores")
            return
        
        print(f"🔑 Nuevo CSRF token: {csrf_token[:10]}...")
        
        # Datos del proveedor de prueba
        data = {
            'nombre_comercial': 'Test Provider AJAX',
            'razon_social': 'Test Provider S.A.',
            'rfc': 'TEST123456ABC',
            'persona_contacto': 'Juan Test',
            'telefono': '5551234567',
            'email': 'test@ajax.com',
            'direccion': 'Calle Test 123',
            'ciudad_estado': 'Test City',
            'categoria_productos': 'ingredientes',
            'forma_pago_preferida': 'transferencia',
            'dias_credito': '30',
            'notas_adicionales': 'Proveedor de prueba AJAX',
            'csrfmiddlewaretoken': csrf_token
        }
        
        # Hacer request AJAX
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        print("🚀 Enviando datos via AJAX...")
        response = session.post(url, data=data, headers=headers)
        
        print(f"📡 Código de respuesta: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        # Verificar si es JSON
        try:
            json_response = response.json()
            print("✅ Respuesta JSON recibida:")
            print(f"   Success: {json_response.get('success', 'N/A')}")
            print(f"   Message: {json_response.get('message', 'N/A')}")
            
            if json_response.get('success'):
                print("🎉 ¡PROVEEDOR CREADO EXITOSAMENTE VIA AJAX!")
            else:
                print("⚠️  Error en la creación:")
                if 'errors' in json_response:
                    for field, error in json_response['errors'].items():
                        print(f"     {field}: {error}")
        except:
            print("❌ La respuesta NO es JSON:")
            print(f"   Contenido: {response.text[:200]}...")
            
        # Verificar redirección
        if response.status_code == 302:
            print(f"❌ Hubo redirección a: {response.headers.get('Location', 'N/A')}")
            print("   Esto indica que NO se usó AJAX correctamente")
        elif response.status_code == 200:
            print("✅ No hubo redirección - respuesta directa")
            
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_proveedor_endpoint()
