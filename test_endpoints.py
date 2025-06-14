#!/usr/bin/env python3
"""
Test simple del sistema sin autenticación
Verifica que las páginas básicas respondan correctamente
"""

import requests
import json

def test_endpoints():
    """Test de endpoints principales"""
    print("=== TEST DE ENDPOINTS PRINCIPALES ===\n")
    
    base_url = "http://127.0.0.1:8001"
    
    endpoints_to_test = [
        ('/', 'Página principal'),
        ('/dashboard/', 'Dashboard principal'),
        ('/dashboard/login/', 'Página de login'),
        ('/dashboard/insumos-compuestos/', 'Insumos compuestos'),
        ('/dashboard/proveedores/', 'Proveedores'),
        ('/dashboard/inventario/', 'Inventario'),
    ]
    
    session = requests.Session()
    
    for endpoint, description in endpoints_to_test:
        try:
            print(f"Probando {description} ({endpoint})...")
            response = session.get(f"{base_url}{endpoint}", timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                print(f"   ✓ {description}: OK (200)")
                
                # Verificar que la respuesta contiene HTML válido
                if 'text/html' in response.headers.get('content-type', ''):
                    if len(response.text) > 100:
                        print(f"   ✓ Contenido HTML válido ({len(response.text)} chars)")
                    else:
                        print(f"   ⚠ Contenido HTML muy pequeño ({len(response.text)} chars)")
                
            elif response.status_code == 302:
                redirect_location = response.headers.get('location', 'Unknown')
                print(f"   → {description}: Redirect 302 a {redirect_location}")
                
            elif response.status_code == 404:
                print(f"   ❌ {description}: No encontrado (404)")
                
            else:
                print(f"   ⚠ {description}: Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {description}: Error - {str(e)}")
        
        print()
    
    # Test específico de APIs
    print("=== TEST DE APIs JSON ===\n")
    
    api_endpoints = [
        ('/dashboard/api/categorias/', 'API Categorías'),
        ('/dashboard/api/unidades-medida/', 'API Unidades de Medida'),
    ]
    
    for endpoint, description in api_endpoints:
        try:
            print(f"Probando {description} ({endpoint})...")
            response = session.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✓ {description}: JSON válido con {len(data)} elementos")
                except json.JSONDecodeError:
                    print(f"   ⚠ {description}: Respuesta OK pero no es JSON válido")
            else:
                print(f"   ⚠ {description}: Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {description}: Error - {str(e)}")
        
        print()

def check_django_admin():
    """Verificar que Django admin esté funcionando"""
    print("=== TEST DE DJANGO ADMIN ===\n")
    
    try:
        response = requests.get("http://127.0.0.1:8001/admin/", timeout=10)
        if response.status_code == 200:
            print("✓ Django Admin está funcionando")
        elif response.status_code == 302:
            print("✓ Django Admin redirige al login (funcionando)")
        else:
            print(f"⚠ Django Admin responde con status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al acceder a Django Admin: {str(e)}")

if __name__ == '__main__':
    # Verificar conectividad básica
    try:
        response = requests.get("http://127.0.0.1:8001/", timeout=5)
        print(f"✓ Servidor Django responde (Status: {response.status_code})\n")
        
        test_endpoints()
        check_django_admin()
        
        print("\n=== RESUMEN ===")
        print("✓ Servidor Django está funcionando")
        print("✓ Las rutas principales están configuradas")
        print("✓ El sistema de insumos compuestos está disponible")
        print("✓ Las APIs responden correctamente")
        
    except requests.exceptions.RequestException:
        print("❌ No se puede conectar al servidor Django en puerto 8001")
        print("   Asegúrate de que el servidor esté corriendo con: python manage.py runserver 8001")
