#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test específico para verificar que las categorías y unidades se cargan en el formulario
"""

import requests
import json
import re
from urllib.parse import urljoin

def test_form_data_direct():
    """Probar el endpoint get_form_data directamente"""
    print("🔍 PROBANDO CARGA DE CATEGORÍAS Y UNIDADES")
    print("=" * 50)
    
    session = requests.Session()
    base_url = 'http://127.0.0.1:8000'
    
    # Paso 1: Obtener página de login
    print("1️⃣ Obteniendo página de login...")
    login_url = urljoin(base_url, '/dashboard/login/')
    
    try:
        response = session.get(login_url)
        if response.status_code == 200:
            print("✅ Página de login obtenida")
            
            # Extraer token CSRF
            csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"✅ Token CSRF obtenido: {csrf_token[:10]}...")
            else:
                print("❌ No se pudo obtener token CSRF")
                return False
        else:
            print(f"❌ Error al obtener login: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # Paso 2: Hacer login
    print("\n2️⃣ Haciendo login...")
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    try:
        response = session.post(login_url, data=login_data)
        if response.status_code in [200, 302]:
            print("✅ Login exitoso")
        else:
            print(f"❌ Login fallido: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return False
    
    # Paso 3: Probar endpoint get_form_data
    print("\n3️⃣ Probando endpoint get_form_data...")
    endpoint_url = urljoin(base_url, '/dashboard/insumos/form-data/')
    
    try:
        response = session.get(endpoint_url)
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('content-type', 'No especificado')}")
        
        if response.status_code == 200:
            if 'application/json' in response.headers.get('content-type', ''):
                try:
                    data = response.json()
                    print("✅ Respuesta JSON válida recibida")
                    
                    # Verificar estructura
                    if 'categorias' in data and 'unidades' in data:
                        categorias = data['categorias']
                        unidades = data['unidades']
                        
                        print(f"📦 Categorías: {len(categorias)} encontradas")
                        print(f"📏 Unidades: {len(unidades)} encontradas")
                        
                        # Mostrar ejemplos
                        if categorias:
                            print("✅ Ejemplos de categorías:")
                            for cat in categorias[:3]:
                                print(f"   • ID: {cat['id']}, Nombre: {cat['nombre']}")
                        
                        if unidades:
                            print("✅ Ejemplos de unidades:")
                            for unidad in unidades[:3]:
                                print(f"   • ID: {unidad['id']}, Nombre: {unidad['nombre']} ({unidad['abreviacion']})")
                        
                        return len(categorias) > 0 and len(unidades) > 0
                    else:
                        print("❌ Estructura de respuesta incorrecta")
                        print(f"📄 Keys encontradas: {list(data.keys())}")
                        return False
                        
                except json.JSONDecodeError:
                    print("❌ Respuesta no es JSON válido")
                    print(f"📄 Contenido: {response.text[:200]}...")
                    return False
            else:
                print("❌ Respuesta no es JSON")
                print(f"📄 Contenido: {response.text[:200]}...")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Respuesta: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error en endpoint: {e}")
        return False

def test_inventory_page_functionality():
    """Probar que la página de inventario funcione correctamente"""
    print("\n4️⃣ Probando página de inventario...")
    
    session = requests.Session()
    base_url = 'http://127.0.0.1:8000'
    
    # Login rápido (reutilizar código anterior)
    login_url = urljoin(base_url, '/dashboard/login/')
    response = session.get(login_url)
    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', response.text)
    csrf_token = csrf_match.group(1) if csrf_match else None
    
    if csrf_token:
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'csrfmiddlewaretoken': csrf_token
        }
        session.post(login_url, data=login_data)
    
    # Probar página de inventario
    inventory_url = urljoin(base_url, '/dashboard/inventario/')
    
    try:
        response = session.get(inventory_url)
        
        if response.status_code == 200:
            print("✅ Página de inventario carga correctamente")
            
            html_content = response.text
            
            # Verificar elementos críticos
            checks = [
                ('id="categoria"', 'Select de categorías'),
                ('id="unidad_medida"', 'Select de unidades'),
                ('function cargarDatosFormulario()', 'Función de carga'),
                ('data-bs-target="#nuevoInsumoModal"', 'Botón modal'),
                ('NUEVO INSUMO', 'Texto del botón'),
            ]
            
            passed = 0
            for check, description in checks:
                if check in html_content:
                    print(f"✅ {description}: Presente")
                    passed += 1
                else:
                    print(f"❌ {description}: Faltante")
            
            return passed >= 4  # Al menos 4 de 5 elementos
        else:
            print(f"❌ Error al cargar página: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error al probar página: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 TEST COMPLETO DE FUNCIONALIDAD DE FORMULARIOS")
    print("=" * 60)
    
    # Test del endpoint
    endpoint_ok = test_form_data_direct()
    
    # Test de la página
    page_ok = test_inventory_page_functionality()
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL:")
    
    if endpoint_ok:
        print("✅ Endpoint get_form_data: FUNCIONAL")
    else:
        print("❌ Endpoint get_form_data: PROBLEMA")
    
    if page_ok:
        print("✅ Página de inventario: FUNCIONAL")
    else:
        print("❌ Página de inventario: PROBLEMA")
    
    if endpoint_ok and page_ok:
        print("\n🎉 ¡ÉXITO COMPLETO!")
        print("✅ Los selects de categorías y unidades deberían cargar correctamente")
        print("\n💡 PRUEBA MANUAL:")
        print("1. Abre: http://127.0.0.1:8000/dashboard/inventario/")
        print("2. Login con: admin / admin123")
        print("3. Haz clic en 'NUEVO INSUMO'")
        print("4. Verifica que los selects tengan opciones")
    else:
        print("\n⚠️  HAY PROBLEMAS QUE RESOLVER")
        print("🔍 Revisar los errores mostrados arriba")

if __name__ == "__main__":
    main()
