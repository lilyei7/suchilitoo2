"""
Test simple para verificar la funcionalidad de editar y eliminar insumos
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_insumos_crud():
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Ir a la página de inventario
        print("Accediendo a la página...")
        driver.get("http://127.0.0.1:8000/dashboard/inventario/")
        
        # Esperar a que la página cargue
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Verificar si hay errores de JavaScript en la consola
        logs = driver.get_log('browser')
        print("Logs del navegador:")
        for log in logs:
            print(f"  {log['level']}: {log['message']}")
        
        # Buscar botones de editar
        edit_buttons = driver.find_elements(By.CLASS_NAME, "btn-editar-insumo")
        print(f"Botones de editar encontrados: {len(edit_buttons)}")
        
        # Buscar botones de eliminar
        delete_buttons = driver.find_elements(By.CLASS_NAME, "btn-eliminar-insumo")
        print(f"Botones de eliminar encontrados: {len(delete_buttons)}")
        
        if edit_buttons:
            print("Haciendo clic en el primer botón de editar...")
            edit_buttons[0].click()
            time.sleep(2)
            
            # Verificar si se abre el modal
            try:
                modal = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "modalEditarInsumo"))
                )
                print("✓ Modal de edición se abrió correctamente")
            except:
                print("✗ Modal de edición no se abrió")
        
        time.sleep(3)
        
    except Exception as e:
        print(f"Error durante el test: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_insumos_crud()
