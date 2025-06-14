"""
Test simple para verificar la edición de insumos
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_edit_simple():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Comentar para ver la ventana
    
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
        time.sleep(3)
        
        # Buscar primer botón de editar
        edit_buttons = driver.find_elements(By.CLASS_NAME, "btn-editar-insumo")
        print(f"3. Botones de editar encontrados: {len(edit_buttons)}")
        
        if edit_buttons:
            print("4. Haciendo clic en primer botón de editar...")
            first_btn = edit_buttons[0]
            insumo_id = first_btn.get_attribute('data-id')
            print(f"   ID del insumo: {insumo_id}")
            
            # Hacer clic usando JavaScript para evitar problemas
            driver.execute_script("arguments[0].click();", first_btn)
            time.sleep(2)
            
            # Verificar que el modal se abrió
            try:
                modal = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.ID, "modalEditarInsumo"))
                )
                print("✅ Modal de edición se abrió correctamente")
                
                # Verificar que el botón Guardar Cambios esté presente
                save_button = driver.find_element(By.ID, "btnGuardarEdicion")
                print(f"✅ Botón Guardar encontrado: {save_button.text}")
                
                # Modificar el nombre
                nombre_field = driver.find_element(By.ID, "editNombre")
                original_name = nombre_field.get_attribute('value')
                new_name = f"{original_name}_editado_{int(time.time())}"
                
                print(f"5. Cambiando nombre de '{original_name}' a '{new_name}'")
                nombre_field.clear()
                nombre_field.send_keys(new_name)
                time.sleep(1)
                
                # Hacer clic en guardar usando JavaScript
                print("6. Guardando cambios...")
                driver.execute_script("arguments[0].click();", save_button)
                time.sleep(5)  # Esperar más tiempo para que se procese
                
                # Verificar si hay alertas de éxito
                print("7. Verificando resultado...")
                
                # Verificar logs del navegador
                logs = driver.get_log('browser')
                for log in logs:
                    if log['level'] in ['SEVERE', 'WARNING']:
                        print(f"   Log: {log['level']}: {log['message']}")
                
                print("✅ Prueba completada")
                
            except Exception as modal_error:
                print(f"❌ Error con el modal: {modal_error}")
        else:
            print("❌ No se encontraron botones de editar")
        
        # Mantener ventana abierta para inspección manual
        print("8. Manteniendo ventana abierta por 10 segundos...")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    test_edit_simple()
