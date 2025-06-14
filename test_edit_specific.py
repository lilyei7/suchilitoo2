"""
Test específico para la funcionalidad de edición
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_edit_functionality():
    chrome_options = Options()
    chrome_options.add_argument("--disable-web-security")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Login
        print("1. Haciendo login...")
        driver.get("http://127.0.0.1:8000/dashboard/login/")
        
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        time.sleep(2)
        
        # Ir a inventario
        print("2. Navegando a inventario...")
        driver.get("http://127.0.0.1:8000/dashboard/inventario/")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        time.sleep(2)
        
        # Buscar primer botón de editar
        edit_buttons = driver.find_elements(By.CLASS_NAME, "btn-editar-insumo")
        if not edit_buttons:
            print("❌ No se encontraron botones de editar")
            return
        
        print("3. Haciendo clic en botón de editar...")
        first_edit_btn = edit_buttons[0]
        insumo_id = first_edit_btn.get_attribute('data-id')
        print(f"   ID del insumo: {insumo_id}")
        
        # Hacer clic usando JavaScript para evitar problemas de interacción
        driver.execute_script("arguments[0].click();", first_edit_btn)
        time.sleep(2)
        
        # Verificar que el modal se abrió
        modal = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "modalEditarInsumo"))
        )
        
        if modal.is_displayed():
            print("✅ Modal de edición se abrió correctamente")
            
            # Verificar que los campos están poblados
            nombre_field = driver.find_element(By.ID, "editNombre")
            if nombre_field.get_attribute('value'):
                print(f"✅ Campo nombre poblado: {nombre_field.get_attribute('value')}")
            else:
                print("❌ Campo nombre vacío")
            
            # Hacer un cambio pequeño
            print("4. Modificando nombre...")
            driver.execute_script("arguments[0].value = arguments[0].value + ' (Editado)';", nombre_field)
            
            # Intentar guardar
            print("5. Guardando cambios...")
            save_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Guardar Cambios')]")
            driver.execute_script("arguments[0].click();", save_button)
            
            time.sleep(3)
            
            # Verificar si hay errores en consola
            logs = driver.get_log('browser')
            errors = [log for log in logs if log['level'] == 'SEVERE']
            if errors:
                print("❌ Errores en consola:")
                for error in errors:
                    print(f"   {error['message']}")
            else:
                print("✅ No hay errores en consola")
        else:
            print("❌ Modal no está visible")
        
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    test_edit_functionality()
