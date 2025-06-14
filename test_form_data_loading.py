#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar específicamente la carga de categorías y unidades en el formulario
"""

import requests
import json
from urllib.parse import urljoin

class FormDataTester:
    def __init__(self, base_url='http://127.0.0.1:8000'):
        self.base_url = base_url
        self.session = requests.Session()
    
    def login(self, username='admin', password='admin123'):
        """Login en el sistema"""
        login_url = urljoin(self.base_url, '/dashboard/login/')
        
        # Obtener página de login para el token CSRF
        response = self.session.get(login_url)
        if 'csrfmiddlewaretoken' in response.text:
            import re
            csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
            else:
                print("❌ No se pudo obtener token CSRF")
                return False
        else:
            print("❌ No se encontró formulario de login")
            return False
        
        # Intentar login
        login_data = {
            'username': username,
            'password': password,
            'csrfmiddlewaretoken': csrf_token
        }
        
        response = self.session.post(login_url, data=login_data)
        
        if response.status_code in [200, 302] and 'dashboard' in response.url:
            print("✅ Login exitoso")
            return True
        else:
            print(f"❌ Login fallido - Status: {response.status_code}")
            return False
    
    def test_form_data_endpoint(self):
        """Probar el endpoint get_form_data"""
        print("\n📋 Probando endpoint get_form_data...")
        
        endpoint_url = urljoin(self.base_url, '/dashboard/insumos/form-data/')
        
        try:
            response = self.session.get(endpoint_url)
            print(f"📊 Status HTTP: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Verificar estructura de respuesta
                    if 'categorias' in data and 'unidades' in data:
                        print("✅ Estructura de respuesta correcta")
                        
                        # Verificar categorías
                        categorias = data['categorias']
                        print(f"📦 Categorías encontradas: {len(categorias)}")
                        
                        if categorias:
                            print("✅ Categorías disponibles:")
                            for cat in categorias[:3]:  # Mostrar solo las primeras 3
                                print(f"   • {cat.get('nombre', 'Sin nombre')} (ID: {cat.get('id', 'N/A')})")
                            if len(categorias) > 3:
                                print(f"   • ... y {len(categorias) - 3} más")
                        else:
                            print("⚠️  No hay categorías en la base de datos")
                        
                        # Verificar unidades
                        unidades = data['unidades']
                        print(f"📏 Unidades encontradas: {len(unidades)}")
                        
                        if unidades:
                            print("✅ Unidades disponibles:")
                            for unidad in unidades[:3]:  # Mostrar solo las primeras 3
                                nombre = unidad.get('nombre', 'Sin nombre')
                                abrev = unidad.get('abreviacion', 'N/A')
                                print(f"   • {nombre} ({abrev}) (ID: {unidad.get('id', 'N/A')})")
                            if len(unidades) > 3:
                                print(f"   • ... y {len(unidades) - 3} más")
                        else:
                            print("⚠️  No hay unidades en la base de datos")
                        
                        return len(categorias) > 0 and len(unidades) > 0
                    else:
                        print("❌ Estructura de respuesta incorrecta")
                        print(f"📄 Respuesta recibida: {data}")
                        return False
                        
                except json.JSONDecodeError:
                    print("❌ La respuesta no es JSON válido")
                    print(f"📄 Contenido: {response.text[:200]}...")
                    return False
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                print(f"📄 Respuesta: {response.text[:200]}...")
                return False
                
        except Exception as e:
            print(f"❌ Error al conectar con el endpoint: {e}")
            return False
    
    def test_inventory_page_loading(self):
        """Probar que la página de inventario carga correctamente"""
        print("\n🌐 Probando carga de página de inventario...")
        
        inventory_url = urljoin(self.base_url, '/dashboard/inventario/')
        
        try:
            response = self.session.get(inventory_url)
            
            if response.status_code == 200:
                print("✅ Página de inventario carga correctamente")
                
                # Verificar que contenga los elementos necesarios
                html_content = response.text
                
                checks = [
                    ('id="categoria"', 'Select de categorías'),
                    ('id="unidad_medida"', 'Select de unidades'),
                    ('function cargarDatosFormulario()', 'Función de carga de datos'),
                    ('{% url "dashboard:get_form_data" %}', 'URL del endpoint'),
                ]
                
                all_good = True
                for check, description in checks:
                    if check in html_content:
                        print(f"✅ {description}: Presente")
                    else:
                        print(f"❌ {description}: Faltante")
                        all_good = False
                
                return all_good
            else:
                print(f"❌ Error al cargar página: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error al cargar página: {e}")
            return False
    
    def run_complete_test(self):
        """Ejecutar prueba completa"""
        print("🔍 PRUEBA DE CARGA DE CATEGORÍAS Y UNIDADES")
        print("=" * 60)
        
        # Test 1: Login
        if not self.login():
            print("\n❌ No se pudo hacer login - Abortando pruebas")
            return False
        
        # Test 2: Endpoint de datos
        endpoint_ok = self.test_form_data_endpoint()
        
        # Test 3: Página de inventario
        page_ok = self.test_inventory_page_loading()
        
        # Resultado final
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE RESULTADOS:")
        
        if endpoint_ok:
            print("✅ Endpoint get_form_data: FUNCIONAL")
        else:
            print("❌ Endpoint get_form_data: PROBLEMA")
        
        if page_ok:
            print("✅ Página de inventario: FUNCIONAL")
        else:
            print("❌ Página de inventario: PROBLEMA")
        
        if endpoint_ok and page_ok:
            print("\n🎉 ¡ÉXITO! Los selects deberían cargar correctamente")
            print("💡 Prueba manual:")
            print("   1. Abre http://127.0.0.1:8000/dashboard/inventario/")
            print("   2. Haz clic en 'NUEVO INSUMO'")
            print("   3. Verifica que los selects de categoría y unidad tengan opciones")
        else:
            print("\n⚠️  HAY PROBLEMAS - Revisar errores mostrados arriba")
        
        return endpoint_ok and page_ok

def main():
    tester = FormDataTester()
    tester.run_complete_test()

if __name__ == "__main__":
    main()
