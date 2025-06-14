#!/usr/bin/env python3
"""
Script para probar las funciones de proveedores y verificar que no hay errores de JavaScript
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

def test_proveedores_functions():
    print("🔍 Iniciando prueba de funciones de proveedores...")
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("http://127.0.0.1:8000/")
        
        print("📝 Haciendo login...")
        
        # Login
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_input = driver.find_element(By.NAME, "password")
        
        username_input.send_keys("admin")
        password_input.send_keys("admin123")
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        print("🚚 Navegando a la página de proveedores...")
        time.sleep(2)
        
        # Ir a proveedores
        driver.get("http://127.0.0.1:8000/dashboard/proveedores/")
        
        # Esperar a que la página se cargue completamente
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        time.sleep(3)
        
        print("🔍 Verificando errores de JavaScript en consola...")
        
        # Obtener logs de la consola
        logs = driver.get_log('browser')
        js_errors = [log for log in logs if log['level'] == 'SEVERE']
        
        if js_errors:
            print("❌ Errores de JavaScript encontrados:")
            for error in js_errors:
                print(f"   - {error['message']}")
        else:
            print("✅ No se encontraron errores de JavaScript críticos")
        
        print("🎯 Probando disponibilidad de funciones...")
        
        # Verificar que las funciones están disponibles
        functions_to_check = [
            'verDetalleProveedor',
            'editarProveedor', 
            'eliminarProveedor'
        ]
        
        for func_name in functions_to_check:
            try:
                result = driver.execute_script(f"return typeof window.{func_name}")
                if result == 'function':
                    print(f"✅ {func_name}: Disponible como función global")
                else:
                    print(f"❌ {func_name}: No disponible (tipo: {result})")
            except Exception as e:
                print(f"❌ Error verificando {func_name}: {e}")
        
        print("🔧 Probando botones de acción...")
        
        # Intentar encontrar botones de acción
        try:
            ver_buttons = driver.find_elements(By.CSS_SELECTOR, "button[onclick*='verDetalleProveedor']")
            editar_buttons = driver.find_elements(By.CSS_SELECTOR, "button[onclick*='editarProveedor']")
            eliminar_buttons = driver.find_elements(By.CSS_SELECTOR, "button[onclick*='eliminarProveedor']")
            
            print(f"📊 Botones encontrados:")
            print(f"   - Ver detalles: {len(ver_buttons)}")
            print(f"   - Editar: {len(editar_buttons)}")
            print(f"   - Eliminar: {len(eliminar_buttons)}")
            
            # Si hay botones, probar uno de cada tipo
            if ver_buttons:
                print("🔍 Probando botón 'Ver detalles'...")
                try:
                    driver.execute_script("arguments[0].click();", ver_buttons[0])
                    time.sleep(2)
                    
                    # Verificar si se abrió el modal
                    modal = driver.find_element(By.ID, "detalleProveedorModal")
                    if "show" in modal.get_attribute("class"):
                        print("✅ Modal de detalles se abrió correctamente")
                        # Cerrar modal
                        close_btn = modal.find_element(By.CSS_SELECTOR, ".btn-close")
                        close_btn.click()
                        time.sleep(1)
                    else:
                        print("❌ Modal de detalles no se abrió")
                except Exception as e:
                    print(f"❌ Error probando botón ver detalles: {e}")
            
            if editar_buttons:
                print("✏️ Probando botón 'Editar'...")
                try:
                    driver.execute_script("arguments[0].click();", editar_buttons[0])
                    time.sleep(2)
                    
                    # Verificar si se abrió el modal
                    modal = driver.find_element(By.ID, "editarProveedorModal")
                    if "show" in modal.get_attribute("class"):
                        print("✅ Modal de edición se abrió correctamente")
                        # Cerrar modal
                        close_btn = modal.find_element(By.CSS_SELECTOR, ".btn-close")
                        close_btn.click()
                        time.sleep(1)
                    else:
                        print("❌ Modal de edición no se abrió")
                except Exception as e:
                    print(f"❌ Error probando botón editar: {e}")
                    
        except Exception as e:
            print(f"❌ Error buscando botones: {e}")
        
        # Verificar logs finales
        final_logs = driver.get_log('browser')
        new_errors = [log for log in final_logs if log['level'] == 'SEVERE' and log not in js_errors]
        
        if new_errors:
            print("\n⚠️ Nuevos errores después de las pruebas:")
            for error in new_errors:
                print(f"   - {error['message']}")
        else:
            print("\n✅ No se generaron nuevos errores durante las pruebas")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        
    finally:
        if driver:
            driver.quit()
            print("🔚 Browser cerrado")

if __name__ == "__main__":
    test_proveedores_functions()
