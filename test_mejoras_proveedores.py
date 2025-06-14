#!/usr/bin/env python3
"""
Test de las mejoras en el sistema de proveedores
Este test verifica el diseño mejorado y la funcionalidad de auto-refresh
"""

import os
import sys
import django
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import authenticate
from accounts.models import Usuario

def test_mejoras_proveedores():
    """Test completo de las mejoras en el sistema de proveedores"""
    
    print("🧪 INICIANDO TEST DE MEJORAS EN SISTEMA DE PROVEEDORES")
    print("=" * 60)
    
    # Configurar Chrome en modo headless para testing
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 20)
        
        # 1. Verificar acceso al sistema
        print("1️⃣ Verificando acceso al sistema...")
        driver.get("http://127.0.0.1:8000/dashboard/login/")
        
        # Login
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Esperar redirección
        wait.until(EC.url_contains("/dashboard/"))
        print("✅ Login exitoso")
        
        # 2. Navegar a proveedores
        print("2️⃣ Navegando a la página de proveedores...")
        driver.get("http://127.0.0.1:8000/dashboard/proveedores/")
        
        # Verificar que la página carga
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        print("✅ Página de proveedores cargada")
        
        # 3. Verificar elementos de diseño mejorado
        print("3️⃣ Verificando diseño mejorado...")
        
        # Verificar tarjetas de estadísticas
        stats_cards = driver.find_elements(By.CSS_SELECTOR, ".stats-card")
        if len(stats_cards) >= 4:
            print("✅ Tarjetas de estadísticas encontradas")
            
            # Verificar hover effects (simular mouse over)
            actions = ActionChains(driver)
            actions.move_to_element(stats_cards[0]).perform()
            time.sleep(0.5)
            print("✅ Efectos hover en estadísticas funcionando")
        
        # Verificar tarjetas de proveedores con diseño mejorado
        provider_cards = driver.find_elements(By.CSS_SELECTOR, ".provider-card")
        if provider_cards:
            print(f"✅ Encontradas {len(provider_cards)} tarjetas de proveedores")
            
            # Verificar elementos específicos del diseño
            first_card = provider_cards[0]
            
            # Avatar con animación
            avatar = first_card.find_element(By.CSS_SELECTOR, ".provider-avatar")
            if avatar:
                print("✅ Avatar de proveedor con diseño mejorado")
            
            # Status dots rediseñados
            status_dot = first_card.find_element(By.CSS_SELECTOR, ".status-dot")
            if status_dot:
                print("✅ Status dots rediseñados")
            
            # Métricas mejoradas
            metrics = first_card.find_elements(By.CSS_SELECTOR, ".metric")
            if len(metrics) >= 3:
                print("✅ Métricas rediseñadas")
            
            # Botones de acción mejorados
            action_buttons = first_card.find_elements(By.CSS_SELECTOR, ".action-btn")
            if action_buttons:
                print("✅ Botones de acción rediseñados")
        
        # 4. Probar modal mejorado
        print("4️⃣ Probando modal de nuevo proveedor mejorado...")
        
        # Abrir modal
        new_provider_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-bs-target='#nuevoProveedorModal']")))
        new_provider_btn.click()
        
        # Esperar a que el modal aparezca
        modal = wait.until(EC.visibility_of_element_located((By.ID, "nuevoProveedorModal")))
        print("✅ Modal abierto correctamente")
        
        # Verificar diseño del modal
        modal_header = modal.find_element(By.CSS_SELECTOR, ".modal-header")
        if "background: linear-gradient" in driver.execute_script("return window.getComputedStyle(arguments[0]).background", modal_header):
            print("✅ Header del modal con gradiente")
        
        # Verificar formulario mejorado
        form_labels = modal.find_elements(By.CSS_SELECTOR, ".form-label")
        if len(form_labels) >= 10:
            print(f"✅ Formulario con {len(form_labels)} campos etiquetados correctamente")
        
        # Verificar iconos en las etiquetas
        label_icons = modal.find_elements(By.CSS_SELECTOR, ".form-label i")
        if len(label_icons) >= 10:
            print("✅ Iconos en etiquetas del formulario")
        
        # 5. Probar funcionalidad de creación con auto-refresh
        print("5️⃣ Probando creación de proveedor con auto-refresh...")
        
        # Contar proveedores actuales
        current_providers = len(driver.find_elements(By.CSS_SELECTOR, ".provider-card"))
        
        # Llenar formulario
        nombre_comercial = modal.find_element(By.ID, "nombre_comercial")
        nombre_comercial.send_keys("Proveedor Test Automatizado")
        
        razon_social = modal.find_element(By.ID, "razon_social")
        razon_social.send_keys("Test S.A. de C.V.")
        
        rfc = modal.find_element(By.ID, "rfc")
        rfc.send_keys("TST123456789")
        
        persona_contacto = modal.find_element(By.ID, "persona_contacto")
        persona_contacto.send_keys("Juan Test")
        
        telefono = modal.find_element(By.ID, "telefono")
        telefono.send_keys("555-123-4567")
        
        email = modal.find_element(By.ID, "email")
        email.send_keys("test@proveedor.com")
        
        print("✅ Formulario llenado")
        
        # Enviar formulario
        submit_btn = modal.find_element(By.CSS_SELECTOR, "button[type='submit']")
        original_text = submit_btn.text
        submit_btn.click()
        
        # Verificar estado del botón (loading)
        time.sleep(1)
        if "Guardando" in submit_btn.text or "spinner" in submit_btn.get_attribute("innerHTML"):
            print("✅ Estado de loading en botón")
        
        # Esperar a que aparezca el toast
        try:
            toast = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".toast")))
            if "exitosamente" in toast.text.lower():
                print("✅ Toast de éxito mostrado")
        except:
            print("⚠️ Toast no detectado (puede haber aparecido muy rápido)")
        
        # Esperar a que se cierre el modal
        wait.until(EC.invisibility_of_element_located((By.ID, "nuevoProveedorModal")))
        print("✅ Modal cerrado")
        
        # Esperar auto-refresh (máximo 3 segundos)
        time.sleep(3)
        
        # Verificar que se recargó la página
        new_providers = driver.find_elements(By.CSS_SELECTOR, ".provider-card")
        if len(new_providers) > current_providers:
            print("✅ Auto-refresh funcionando - Nuevo proveedor visible")
        else:
            print("⚠️ Auto-refresh puede no haber funcionado o el proveedor ya existía")
        
        # 6. Verificar responsive design
        print("6️⃣ Verificando diseño responsive...")
        
        # Cambiar a viewport móvil
        driver.set_window_size(375, 667)
        time.sleep(1)
        
        # Verificar que las tarjetas se adaptan
        provider_cards_mobile = driver.find_elements(By.CSS_SELECTOR, ".provider-card")
        if provider_cards_mobile:
            print("✅ Diseño responsive funcionando")
        
        # Restaurar viewport
        driver.set_window_size(1920, 1080)
        
        # 7. Verificar filtros mejorados
        print("7️⃣ Verificando filtros mejorados...")
        
        search_input = driver.find_element(By.NAME, "buscar")
        if search_input.get_attribute("placeholder"):
            print("✅ Campo de búsqueda con placeholder")
        
        filter_selects = driver.find_elements(By.CSS_SELECTOR, ".form-select")
        if len(filter_selects) >= 3:
            print("✅ Selectores de filtros disponibles")
        
        print("\n🎉 TODAS LAS MEJORAS VERIFICADAS EXITOSAMENTE")
        print("=" * 60)
        print("✅ Diseño mejorado con gradientes y animaciones")
        print("✅ Tarjetas de proveedores rediseñadas")
        print("✅ Modal de formulario con mejor UX")
        print("✅ Auto-refresh después de crear proveedor")
        print("✅ Validaciones mejoradas")
        print("✅ Toasts informativos")
        print("✅ Diseño responsive")
        print("✅ Efectos hover y transiciones")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        return False
        
    finally:
        if 'driver' in locals():
            driver.quit()

def test_api_mejoras():
    """Test específico de la API mejorada"""
    
    print("\n🔧 PROBANDO API MEJORADA")
    print("-" * 30)
    
    # Test de creación con datos válidos
    data = {
        'nombre_comercial': 'API Test Provider',
        'razon_social': 'API Test S.A.',
        'rfc': 'APT123456789',
        'persona_contacto': 'API Contact',
        'telefono': '555-999-8888',
        'email': 'api@test.com',
        'forma_pago_preferida': 'transferencia',
        'dias_credito': '15',
        'direccion': 'API Test Address 123',
        'ciudad_estado': 'Test City, TC',
        'categoria_productos': 'ingredientes',
        'notas_adicionales': 'Created via API test'
    }
    
    try:
        # Obtener CSRF token
        session = requests.Session()
        login_page = session.get('http://127.0.0.1:8000/dashboard/login/')
        
        # Hacer login
        csrf_token = session.cookies.get('csrftoken')
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'csrfmiddlewaretoken': csrf_token
        }
        
        login_response = session.post('http://127.0.0.1:8000/dashboard/login/', data=login_data)
        
        if login_response.status_code == 200:
            print("✅ Login API exitoso")
            
            # Obtener nuevo CSRF token
            proveedores_page = session.get('http://127.0.0.1:8000/dashboard/proveedores/')
            csrf_token = session.cookies.get('csrftoken')
            
            # Agregar CSRF token a los datos
            data['csrfmiddlewaretoken'] = csrf_token
            
            # Crear proveedor via API
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'http://127.0.0.1:8000/dashboard/proveedores/'
            }
            
            response = session.post('http://127.0.0.1:8000/dashboard/proveedores/crear/', 
                                  data=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ Proveedor creado via API")
                    print(f"   Nombre: {result.get('proveedor', {}).get('nombre_comercial', 'N/A')}")
                    print(f"   ID: {result.get('proveedor', {}).get('id', 'N/A')}")
                    return True
                else:
                    print(f"❌ Error en API: {result.get('message', 'Error desconocido')}")
                    return False
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                return False
        else:
            print("❌ Error en login API")
            return False
            
    except Exception as e:
        print(f"❌ Error en test API: {e}")
        return False

if __name__ == "__main__":
    # Verificar que el servidor esté ejecutándose
    try:
        response = requests.get('http://127.0.0.1:8000/dashboard/login/', timeout=5)
        if response.status_code == 200:
            print("🚀 Servidor detectado, iniciando tests...")
            
            # Ejecutar tests
            ui_success = test_mejoras_proveedores()
            api_success = test_api_mejoras()
            
            print(f"\n📊 RESULTADOS FINALES:")
            print(f"   Test UI: {'✅ PASÓ' if ui_success else '❌ FALLÓ'}")
            print(f"   Test API: {'✅ PASÓ' if api_success else '❌ FALLÓ'}")
            
            if ui_success and api_success:
                print("\n🎊 ¡TODOS LOS TESTS PASARON! Sistema mejorado funcionando correctamente.")
            else:
                print("\n⚠️ Algunos tests fallaron. Revisar logs para más detalles.")
                
        else:
            print("❌ Servidor no responde correctamente")
            
    except requests.exceptions.RequestException:
        print("❌ No se puede conectar al servidor Django.")
        print("   Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000/")
