"""
Test integral para verificar edición y eliminación
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_comprehensive():
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
        
        # Verificar logs de JavaScript
        logs = driver.get_log('browser')
        print("3. Logs de JavaScript:")
        for log in logs:
            if 'insumos_crud.js' in log['message'] or 'editarInsumo' in log['message']:
                print(f"   {log['level']}: {log['message']}")
        
        # Buscar primer botón de editar
        edit_buttons = driver.find_elements(By.CLASS_NAME, "btn-editar-insumo")
        print(f"4. Botones de editar encontrados: {len(edit_buttons)}")
        
        if edit_buttons:
            print("5. Haciendo clic en primer botón de editar...")
            first_btn = edit_buttons[0]
            insumo_id = first_btn.get_attribute('data-id')
            print(f"   ID del insumo: {insumo_id}")
            
            # Verificar que las funciones JavaScript están definidas
            js_check = driver.execute_script("""
                return {
                    editarInsumo: typeof editarInsumo !== 'undefined',
                    guardarEdicionInsumo: typeof guardarEdicionInsumo !== 'undefined',
                    eliminarInsumo: typeof eliminarInsumo !== 'undefined',
                    bootstrap: typeof bootstrap !== 'undefined',
                    Swal: typeof Swal !== 'undefined'
                };
            """)
            print(f"   Funciones JavaScript disponibles: {js_check}")
            
            # Hacer clic usando JavaScript
            driver.execute_script("editarInsumo(arguments[0]);", insumo_id)
            time.sleep(2)
            
            # Verificar que el modal se abrió
            try:
                modal = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.ID, "modalEditarInsumo"))
                )
                print("✅ Modal de edición se abrió correctamente")
                
                # Verificar que los campos están poblados
                nombre_field = driver.find_element(By.ID, "editNombre")
                original_name = nombre_field.get_attribute('value')
                print(f"   Nombre actual: {original_name}")
                
                # Cambiar el nombre
                new_name = f"EDITADO_SELENIUM_{int(time.time())}"
                print(f"6. Cambiando nombre a: {new_name}")
                
                driver.execute_script("arguments[0].value = arguments[1];", nombre_field, new_name)
                time.sleep(1)
                
                # Guardar usando JavaScript directamente
                print("7. Guardando usando JavaScript...")
                driver.execute_script("guardarEdicionInsumo();")
                
                # Esperar y verificar los logs
                time.sleep(5)
                
                logs = driver.get_log('browser')
                print("8. Logs después del guardado:")
                for log in logs:
                    if any(keyword in log['message'] for keyword in ['GUARDADO', 'fetch', 'response', 'error', 'success']):
                        print(f"   {log['level']}: {log['message']}")
                
                print("✅ Proceso completado")
                
            except Exception as modal_error:
                print(f"❌ Error con el modal: {modal_error}")
        else:
            print("❌ No se encontraron botones de editar")
        
        # Mantener ventana abierta
        print("9. Manteniendo ventana abierta por 15 segundos para inspección...")
        time.sleep(15)
        
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    test_comprehensive()
