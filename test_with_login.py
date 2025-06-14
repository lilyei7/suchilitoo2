"""
Test con login para verificar la funcionalidad CRUD
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_with_login():
    chrome_options = Options()
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Login primero
        print("1. Haciendo login...")
        driver.get("http://127.0.0.1:8000/dashboard/login/")
        
        # Llenar formulario de login
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        
        # Submit
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Esperar redirección
        time.sleep(2)
        
        # Ir a inventario
        print("2. Navegando a inventario...")
        driver.get("http://127.0.0.1:8000/dashboard/inventario/")
        
        # Esperar a que cargue la página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        time.sleep(2)
        
        # Verificar errores en consola
        logs = driver.get_log('browser')
        print("3. Logs del navegador:")
        for log in logs:
            if log['level'] in ['SEVERE', 'WARNING']:
                print(f"  {log['level']}: {log['message']}")
        
        # Buscar botones
        edit_buttons = driver.find_elements(By.CLASS_NAME, "btn-editar-insumo")
        delete_buttons = driver.find_elements(By.CLASS_NAME, "btn-eliminar-insumo")
        
        print(f"4. Botones encontrados:")
        print(f"   - Editar: {len(edit_buttons)}")
        print(f"   - Eliminar: {len(delete_buttons)}")
        
        # Verificar HTML de la tabla
        table = driver.find_element(By.TAG_NAME, "table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        print(f"   - Filas en tabla: {len(rows)}")
        
        # Si hay botones, probar uno
        if edit_buttons:
            print("5. Probando botón de editar...")
            first_edit_btn = edit_buttons[0]
            print(f"   - Data-id: {first_edit_btn.get_attribute('data-id')}")
            
            # Hacer clic
            driver.execute_script("arguments[0].click();", first_edit_btn)
            time.sleep(2)
            
            # Verificar modal
            try:
                modal = driver.find_element(By.ID, "modalEditarInsumo")
                is_visible = modal.is_displayed()
                print(f"   - Modal visible: {is_visible}")
            except:
                print("   - Modal no encontrado")
        
        time.sleep(3)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    test_with_login()
