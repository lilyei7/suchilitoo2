#!/usr/bin/env python3
"""
Test directo del endpoint de eliminación
"""

import requests
import json

def test_eliminar_endpoint():
    """Test directo del endpoint de eliminación"""
    print("=== TEST DIRECTO DEL ENDPOINT DE ELIMINACIÓN ===\n")
    
    base_url = "http://127.0.0.1:8001"
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # 1. Obtener token CSRF desde la página de login
    print("1. Obteniendo token CSRF...")
    login_response = session.get(f"{base_url}/dashboard/login/")
    
    if login_response.status_code == 200:
        print("✓ Página de login accesible")
        
        # Extraer token CSRF del HTML
        csrf_token = None
        for line in login_response.text.split('\n'):
            if 'csrfmiddlewaretoken' in line and 'value=' in line:
                start = line.find('value="') + 7
                end = line.find('"', start)
                csrf_token = line[start:end]
                break
        
        if csrf_token:
            print(f"✓ Token CSRF obtenido: {csrf_token[:20]}...")
        else:
            print("❌ No se pudo obtener el token CSRF")
            return
    else:
        print(f"❌ Error al acceder a login: {login_response.status_code}")
        return
    
    # 2. Realizar login
    print("\n2. Realizando login...")
    login_data = {
        'username': 'admin_test',
        'password': '123456',
        'csrfmiddlewaretoken': csrf_token
    }
    
    login_result = session.post(f"{base_url}/dashboard/login/", data=login_data)
    
    if login_result.status_code == 302:  # Redirect después de login exitoso
        print("✓ Login exitoso (redirect detectado)")
    else:
        print(f"⚠ Login resultado: {login_result.status_code}")
    
    # 3. Acceder a la página de insumos compuestos
    print("\n3. Accediendo a insumos compuestos...")
    compuestos_response = session.get(f"{base_url}/dashboard/insumos-compuestos/")
    
    if compuestos_response.status_code == 200:
        print("✓ Página de insumos compuestos accesible")
        print(f"✓ Contenido HTML: {len(compuestos_response.text)} caracteres")
        
        # Verificar si contiene la tabla
        if 'table' in compuestos_response.text.lower():
            print("✓ Tabla encontrada en la página")
        else:
            print("⚠ No se encontró tabla en la página")
            
    else:
        print(f"❌ Error al acceder a insumos compuestos: {compuestos_response.status_code}")
        print("❌ Posible problema de autenticación")
        return
    
    # 4. Test del endpoint de eliminación
    print("\n4. Probando endpoint de eliminación...")
    
    # ID del insumo que creamos para test
    insumo_id = 26
    
    # Obtener nuevo token CSRF de la página
    csrf_lines = [line for line in compuestos_response.text.split('\n') if 'csrfmiddlewaretoken' in line]
    if csrf_lines:
        csrf_token = csrf_lines[0].split('value="')[1].split('"')[0]
        print(f"✓ Nuevo token CSRF: {csrf_token[:20]}...")
    
    # Intentar eliminación
    delete_url = f"{base_url}/dashboard/insumos-compuestos/eliminar/{insumo_id}/"
    delete_data = {
        'confirm': 'true',
        'csrfmiddlewaretoken': csrf_token
    }
    
    headers = {
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest'  # Simular AJAX
    }
    
    delete_response = session.post(delete_url, data=delete_data, headers=headers)
    
    print(f"URL de eliminación: {delete_url}")
    print(f"Status code: {delete_response.status_code}")
    print(f"Content-Type: {delete_response.headers.get('content-type', 'N/A')}")
    
    if delete_response.status_code == 200:
        try:
            result_data = delete_response.json()
            print(f"✓ Respuesta JSON: {result_data}")
            
            if result_data.get('success'):
                print("✅ Eliminación exitosa!")
            else:
                print(f"❌ Error en eliminación: {result_data.get('message')}")
                
        except json.JSONDecodeError:
            print("⚠ Respuesta no es JSON válido")
            print(f"Contenido: {delete_response.text[:200]}...")
            
    else:
        print(f"❌ Error en eliminación: Status {delete_response.status_code}")
        print(f"Contenido: {delete_response.text[:200]}...")

    # 5. Verificar estado después de eliminación
    print("\n5. Verificando estado después de eliminación...")
    
    # Verificar en base de datos
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
    django.setup()
    
    from restaurant.models import Insumo
    
    try:
        insumo = Insumo.objects.get(id=insumo_id)
        print(f"⚠ Insumo aún existe en BD: {insumo.nombre}")
    except Insumo.DoesNotExist:
        print("✅ Insumo eliminado correctamente de la BD")

if __name__ == '__main__':
    test_eliminar_endpoint()
