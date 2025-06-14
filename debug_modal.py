#!/usr/bin/env python3
"""
Script para hacer debug específico de la apertura de modales
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def debug_modal_opening():
    print("🔍 Debug de apertura de modales...")
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("http://127.0.0.1:8000/dashboard/proveedores/")
        
        # Login si es necesario
        if "login" in driver.current_url:
            username_input = driver.find_element(By.NAME, "username")
            password_input = driver.find_element(By.NAME, "password")
            username_input.send_keys("admin")
            password_input.send_keys("admin123")
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            driver.get("http://127.0.0.1:8000/dashboard/proveedores/")
        
        time.sleep(3)
        
        print("📊 Estado inicial:")
        print(f"   URL actual: {driver.current_url}")
        
        # Verificar que las funciones existen
        verDetalleExists = driver.execute_script("return typeof window.verDetalleProveedor === 'function'")
        print(f"   verDetalleProveedor existe: {verDetalleExists}")
        
        # Buscar botones
        ver_buttons = driver.find_elements(By.CSS_SELECTOR, "button[onclick*='verDetalleProveedor']")
        print(f"   Botones de ver encontrados: {len(ver_buttons)}")
        
        if ver_buttons:
            # Obtener el onclick del primer botón
            onclick = ver_buttons[0].get_attribute("onclick")
            print(f"   Onclick del primer botón: {onclick}")
            
            # Verificar que el modal existe
            modal_exists = driver.find_elements(By.ID, "detalleProveedorModal")
            print(f"   Modal de detalle existe: {len(modal_exists) > 0}")
            
            if modal_exists:
                modal_classes = modal_exists[0].get_attribute("class")
                print(f"   Clases del modal antes del clic: {modal_classes}")
            
            print("🖱️ Haciendo clic en el botón...")
            driver.execute_script("arguments[0].click();", ver_buttons[0])
            
            time.sleep(2)
            
            # Verificar estado después del clic
            if modal_exists:
                modal_classes_after = modal_exists[0].get_attribute("class")
                print(f"   Clases del modal después del clic: {modal_classes_after}")
                
                # Verificar contenido del modal
                content = driver.find_element(By.ID, "detalleProveedorContent")
                content_text = content.text.strip()
                print(f"   Contenido del modal (primeros 100 chars): {content_text[:100]}...")
            
            # Verificar errores en consola
            logs = driver.get_log('browser')
            errors = [log for log in logs if log['level'] == 'SEVERE']
            if errors:
                print("❌ Errores en consola:")
                for error in errors[-3:]:  # Últimos 3 errores
                    print(f"   - {error['message']}")
            else:
                print("✅ No hay errores en consola")
        
    except Exception as e:
        print(f"❌ Error durante debug: {e}")
        
    finally:
        if driver:
            time.sleep(5)  # Pausa para poder ver el estado
            driver.quit()

if __name__ == "__main__":
    debug_modal_opening()
