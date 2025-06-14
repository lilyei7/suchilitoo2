#!/usr/bin/env python3
"""
Test de la página de proveedores
"""

import requests
import json

def test_proveedores_page():
    """Test de la página de proveedores"""
    print("=== TEST DE PÁGINA DE PROVEEDORES ===\n")
    
    base_url = "http://127.0.0.1:8001"
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # 1. Login
    print("1. Realizando login...")
    login_response = session.get(f"{base_url}/dashboard/login/")
    csrf_token = None
    for line in login_response.text.split('\n'):
        if 'csrfmiddlewaretoken' in line and 'value=' in line:
            start = line.find('value="') + 7
            end = line.find('"', start)
            csrf_token = line[start:end]
            break
    
    login_data = {
        'username': 'admin_test',
        'password': '123456',
        'csrfmiddlewaretoken': csrf_token
    }
    
    login_result = session.post(f"{base_url}/dashboard/login/", data=login_data)
    print(f"✓ Login status: {login_result.status_code}")
    
    # 2. Acceder a proveedores
    print("\n2. Accediendo a proveedores...")
    proveedores_response = session.get(f"{base_url}/dashboard/proveedores/")
    
    print(f"✓ Status: {proveedores_response.status_code}")
    print(f"✓ Content length: {len(proveedores_response.text)} chars")
    
    if proveedores_response.status_code == 200:
        content = proveedores_response.text
        
        # Verificar elementos clave
        checks = [
            ('Gestión de Proveedores', 'Título principal'),
            ('Total Proveedores', 'Estadística total'),
            ('Activos', 'Estadística activos'),
            ('provider-card', 'Tarjetas de proveedor'),
            ('Mariscos del Pacífico', 'Proveedor ejemplo 1'),
            ('Distribuidora de Arroz', 'Proveedor ejemplo 2'),
        ]
        
        print("\n3. Verificando contenido...")
        for check, description in checks:
            if check in content:
                print(f"   ✓ {description}: Encontrado")
            else:
                print(f"   ❌ {description}: No encontrado")
        
        # Contar cards de proveedores
        card_count = content.count('provider-card')
        print(f"\n✓ Tarjetas de proveedores encontradas: {card_count}")
        
        # Verificar JavaScript
        if 'eliminarProveedor' in content:
            print("✓ Función JavaScript de eliminación presente")
        
        if 'editarProveedor' in content:
            print("✓ Función JavaScript de edición presente")
        
    else:
        print(f"❌ Error al cargar página: {proveedores_response.status_code}")
        print(f"Contenido: {proveedores_response.text[:200]}...")
    
    print(f"\n🎯 RESULTADO: {'✅ EXITOSO' if proveedores_response.status_code == 200 else '❌ FALLIDO'}")

if __name__ == '__main__':
    test_proveedores_page()
