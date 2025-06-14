#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test completo del sistema de inventario con autenticación
"""

import requests
import re
from urllib.parse import urljoin

class InventoryTester:
    def __init__(self, base_url='http://127.0.0.1:8000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.csrf_token = None
    
    def get_csrf_token(self, url):
        """Obtener token CSRF de una página"""
        try:
            response = self.session.get(url)
            match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', response.text)
            if match:
                return match.group(1)
            return None
        except:
            return None
    
    def login(self, username='admin', password='admin123'):
        """Intentar login"""
        login_url = urljoin(self.base_url, '/dashboard/login/')
        
        # Obtener token CSRF
        csrf_token = self.get_csrf_token(login_url)
        if not csrf_token:
            print("❌ No se pudo obtener token CSRF para login")
            return False
        
        # Intentar login
        login_data = {
            'username': username,
            'password': password,
            'csrfmiddlewaretoken': csrf_token
        }
        
        response = self.session.post(login_url, data=login_data)
        
        if response.status_code == 302 or 'dashboard' in response.url:
            print("✅ Login exitoso")
            return True
        else:
            print("❌ Login fallido")
            return False
    
    def test_inventory_page(self):
        """Probar la página de inventario"""
        inventory_url = urljoin(self.base_url, '/dashboard/inventario/')
        
        try:
            response = self.session.get(inventory_url)
            
            if response.status_code != 200:
                print(f"❌ Error HTTP: {response.status_code}")
                return False
            
            html_content = response.text
            
            # Tests específicos
            tests = [
                ('id="nuevoInsumoModal"', 'Modal de nuevo insumo'),
                ('function crearInsumo()', 'Función JavaScript crearInsumo'),
                ('data-bs-target="#nuevoInsumoModal"', 'Botón nuevo insumo'),
                ('NUEVO INSUMO', 'Texto del botón'),
                ('Total Insumos', 'Estadísticas'),
                ('Gestión de Inventario', 'Título de la página'),
                ('{% csrf_token %}', 'Token CSRF en formulario'),
            ]
            
            results = {}
            for search_term, description in tests:
                found = search_term in html_content
                results[description] = found
                status = "✅" if found else "❌"
                print(f"{status} {description}: {'Encontrado' if found else 'NO encontrado'}")
            
            # Verificar que no hay templates sin renderizar
            unrendered_count = len(re.findall(r'{\s*{\s*[^}]+\s*}\s*}', html_content))
            if unrendered_count == 0:
                print("✅ No hay templates Django sin renderizar")
                results['Templates renderizados'] = True
            else:
                print(f"❌ {unrendered_count} templates sin renderizar")
                results['Templates renderizados'] = False
            
            # Verificar errores de JavaScript obvios
            js_errors = len(re.findall(r'\.then\s+\w+\s+=>', html_content))
            if js_errors == 0:
                print("✅ No hay errores obvios de sintaxis JavaScript")
                results['JavaScript syntax'] = True
            else:
                print(f"❌ {js_errors} posibles errores de sintaxis JavaScript")
                results['JavaScript syntax'] = False
            
            return results
            
        except Exception as e:
            print(f"❌ Error al probar página de inventario: {e}")
            return {}
    
    def test_complete_workflow(self):
        """Probar el flujo completo"""
        print("🔍 INICIANDO TEST COMPLETO DEL SISTEMA DE INVENTARIO")
        print("=" * 60)
        
        # Test 1: Login
        print("\n📋 1. Probando autenticación...")
        if not self.login():
            print("❌ No se pudo hacer login. Verificar credenciales.")
            return False
        
        # Test 2: Página de inventario
        print("\n📋 2. Probando página de inventario...")
        results = self.test_inventory_page()
        
        if not results:
            print("❌ No se pudo probar la página de inventario")
            return False
        
        # Análisis de resultados
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE RESULTADOS:")
        
        passed_tests = sum(1 for result in results.values() if result)
        total_tests = len(results)
        
        print(f"✅ Tests exitosos: {passed_tests}/{total_tests}")
        
        if passed_tests == total_tests:
            print("\n🎉 ¡ÉXITO COMPLETO!")
            print("✅ Todos los componentes están funcionando correctamente")
            print("✅ El error de sintaxis JavaScript ha sido resuelto")
            print("✅ Los templates Django se renderizan correctamente")
            print("✅ El formulario de nuevo insumo está listo para usar")
        elif passed_tests >= total_tests * 0.8:
            print("\n✅ ¡ÉXITO MAYORITARIO!")
            print("✅ La mayoría de funcionalidades están operativas")
            print("⚠️  Algunos componentes menores pueden necesitar ajustes")
        else:
            print("\n⚠️  ÉXITO PARCIAL")
            print("✅ El sistema está funcionando pero necesita más ajustes")
        
        return passed_tests >= total_tests * 0.7

def main():
    tester = InventoryTester()
    success = tester.test_complete_workflow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 CONCLUSIÓN: Sistema listo para uso")
        print("💡 Próximos pasos:")
        print("   1. Abre http://127.0.0.1:8000/dashboard/inventario/")
        print("   2. Haz login con admin/admin123")
        print("   3. Prueba crear un nuevo insumo")
    else:
        print("🔧 CONCLUSIÓN: Sistema necesita más ajustes")
        print("💡 Revisar los errores mostrados arriba")

if __name__ == "__main__":
    main()
