#!/usr/bin/env python3
"""
Test final para verificar que el botón de editar funciona sin errores de JavaScript
"""

import os
import sys
import django
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Insumo

def test_edit_button_functionality():
    """Test para verificar que el botón de editar funciona sin errores JavaScript"""
    
    print("=== TEST: VERIFICAR FUNCIONAMIENTO DEL BOTON EDITAR ===")
    
    # Configurar Chrome en modo headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    
    try:
        # Verificar que existe al menos un insumo
        insumo = Insumo.objects.first()
        if not insumo:
            print("❌ No hay insumos en la base de datos")
            return False
        
        print(f"✅ Insumo de prueba: {insumo.nombre} (ID: {insumo.id})")
        
        # 1. Ir a la página de login
        driver.get("http://localhost:8000/accounts/login/")
        print("✅ Página de login cargada")
        
        # 2. Hacer login
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Esperar a que la página de inventario cargue
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # 3. Ir a la página de inventario
        driver.get("http://localhost:8000/dashboard/inventario/")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        print("✅ Página de inventario cargada")
        
        # 4. Verificar que no hay errores de JavaScript en la consola
        logs = driver.get_log('browser')
        js_errors = [log for log in logs if log['level'] == 'SEVERE']
        
        if js_errors:
            print("❌ Se encontraron errores de JavaScript:")
            for error in js_errors:
                print(f"   - {error['message']}")
            return False
        else:
            print("✅ No hay errores de JavaScript en la consola")
        
        # 5. Buscar el botón de editar del primer insumo
        edit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[onclick*='editarInsumo']")))
        print("✅ Botón de editar encontrado")
        
        # 6. Click en editar
        edit_button.click()
        print("✅ Click en editar ejecutado")
        
        # 7. Esperar a que el modal se abra
        modal = wait.until(EC.visibility_of_element_located((By.ID, "modalEditarInsumo")))
        print("✅ Modal de edición abierto correctamente")
        
        # 8. Verificar que el modal tiene datos cargados
        nombre_input = modal.find_element(By.ID, "editNombre")
        if nombre_input.get_attribute('value'):
            print(f"✅ Campo nombre poblado con: {nombre_input.get_attribute('value')}")
        else:
            print("❌ Campo nombre no está poblado")
            return False
        
        # 9. Verificar que el dropdown de unidades tiene opciones
        unidad_select = modal.find_element(By.ID, "editUnidadMedida")
        options = unidad_select.find_elements(By.TAG_NAME, "option")
        
        if len(options) > 1:  # Más de 1 porque la primera es "Seleccionar..."
            print(f"✅ Dropdown de unidades tiene {len(options)} opciones")
            for i, option in enumerate(options[:3]):  # Mostrar solo las primeras 3
                print(f"   - Opción {i+1}: {option.text}")
        else:
            print("❌ Dropdown de unidades no tiene opciones")
            return False
        
        # 10. Verificar que no hay nuevos errores después de abrir el modal
        new_logs = driver.get_log('browser')
        new_js_errors = [log for log in new_logs if log['level'] == 'SEVERE']
        
        if new_js_errors:
            print("❌ Se encontraron nuevos errores de JavaScript después de abrir el modal:")
            for error in new_js_errors:
                print(f"   - {error['message']}")
            return False
        else:
            print("✅ No hay nuevos errores de JavaScript después de abrir el modal")
        
        print("\n🎉 TODAS LAS VERIFICACIONES PASARON:")
        print("   ✅ Página carga sin errores JavaScript")
        print("   ✅ Botón de editar es clickeable")
        print("   ✅ Modal se abre correctamente")
        print("   ✅ Campos se poblan con datos")
        print("   ✅ Dropdown de unidades funciona")
        print("   ✅ No hay errores después de abrir modal")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        # Capturar errores de consola si los hay
        try:
            logs = driver.get_log('browser')
            if logs:
                print("📋 Logs de consola:")
                for log in logs:
                    print(f"   - {log['level']}: {log['message']}")
        except:
            pass
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_edit_button_functionality()
    if success:
        print("\n🎉 TEST EXITOSO: El botón de editar funciona perfectamente")
        print("✅ El error de JavaScript 'Identifier already declared' está completamente resuelto")
        print("✅ El modal de edición se abre y funciona correctamente")
        print("✅ Las unidades de medida se cargan y muestran correctamente")
    else:
        print("\n❌ TEST FALLIDO: Aún hay problemas con el botón de editar")
    
    sys.exit(0 if success else 1)
