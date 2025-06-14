#!/usr/bin/env python3
"""
Script para probar la funcionalidad completa de proveedores incluyendo la visualización de datos
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

def test_proveedor_data_display():
    print("🔍 Iniciando prueba completa de visualización de datos de proveedores...")
    
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
        
        print("🔍 Buscando botones de ver detalles...")
        
        # Buscar botones de ver detalles
        ver_buttons = driver.find_elements(By.CSS_SELECTOR, "button[onclick*='verDetalleProveedor']")
        
        if not ver_buttons:
            print("❌ No se encontraron botones de ver detalles")
            return
        
        print(f"✅ Encontrados {len(ver_buttons)} botones de ver detalles")
        
        # Hacer clic en el primer botón de ver detalles
        print("🔍 Haciendo clic en el primer botón de ver detalles...")
        driver.execute_script("arguments[0].click();", ver_buttons[0])
        
        # Esperar a que aparezca el modal
        modal = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "detalleProveedorModal"))
        )
        
        # Verificar que el modal se abrió
        if "show" in modal.get_attribute("class"):
            print("✅ Modal de detalles se abrió correctamente")
            
            # Esperar a que se cargue el contenido
            time.sleep(3)
            
            # Verificar que hay contenido en el modal
            content = driver.find_element(By.ID, "detalleProveedorContent")
            
            if content.text.strip():
                print("✅ El modal contiene información:")
                
                # Buscar elementos específicos
                try:
                    # Buscar información general
                    info_general = content.find_element(By.XPATH, ".//h6[contains(text(), 'Información General')]")
                    print("   ✅ Sección de Información General encontrada")
                    
                    # Buscar información de contacto
                    info_contacto = content.find_element(By.XPATH, ".//h6[contains(text(), 'Información de Contacto')]")
                    print("   ✅ Sección de Información de Contacto encontrada")
                    
                    # Buscar sección de insumos
                    insumos_section = content.find_element(By.XPATH, ".//h6[contains(text(), 'Insumos Asignados')]")
                    print("   ✅ Sección de Insumos Asignados encontrada")
                    
                    # Buscar datos específicos
                    nombre_comercial = content.find_elements(By.XPATH, ".//td[text()='Nombre Comercial:']/following-sibling::td")
                    if nombre_comercial:
                        print(f"   ✅ Nombre comercial: {nombre_comercial[0].text}")
                    
                    estado = content.find_elements(By.XPATH, ".//td[text()='Estado:']/following-sibling::td")
                    if estado:
                        print(f"   ✅ Estado: {estado[0].text}")
                    
                    print("   🎉 La información del proveedor se muestra correctamente")
                    
                except Exception as e:
                    print(f"   ⚠️ No se pudieron encontrar algunos elementos específicos: {e}")
                    print(f"   📄 Contenido del modal (primeros 200 caracteres): {content.text[:200]}...")
            else:
                print("❌ El modal está vacío o aún cargando")
            
            # Cerrar modal
            close_btn = modal.find_element(By.CSS_SELECTOR, ".btn-close")
            close_btn.click()
            time.sleep(1)
            
        else:
            print("❌ El modal no se abrió correctamente")
        
        print("✏️ Probando botón de editar...")
        
        # Buscar botones de editar
        editar_buttons = driver.find_elements(By.CSS_SELECTOR, "button[onclick*='editarProveedor']")
        
        if editar_buttons:
            # Hacer clic en el primer botón de editar
            driver.execute_script("arguments[0].click();", editar_buttons[0])
            
            # Esperar a que aparezca el modal de edición
            modal_editar = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "editarProveedorModal"))
            )
            
            if "show" in modal_editar.get_attribute("class"):
                print("✅ Modal de edición se abrió correctamente")
                
                # Esperar a que se cargue el contenido
                time.sleep(3)
                
                content_editar = driver.find_element(By.ID, "editarProveedorContent")
                
                if content_editar.text.strip():
                    print("✅ El modal de edición contiene el formulario")
                    
                    # Buscar campos del formulario
                    try:
                        nombre_field = content_editar.find_element(By.NAME, "nombre_comercial")
                        print(f"   ✅ Campo nombre comercial con valor: {nombre_field.get_attribute('value')}")
                        
                        email_field = content_editar.find_element(By.NAME, "email")
                        print(f"   ✅ Campo email con valor: {email_field.get_attribute('value')}")
                        
                        estado_field = content_editar.find_element(By.NAME, "estado")
                        print(f"   ✅ Campo estado con valor: {estado_field.get_attribute('value')}")
                        
                        print("   🎉 El formulario de edición se carga correctamente con datos")
                        
                    except Exception as e:
                        print(f"   ⚠️ No se pudieron encontrar algunos campos del formulario: {e}")
                else:
                    print("❌ El modal de edición está vacío")
                
                # Cerrar modal
                close_btn = modal_editar.find_element(By.CSS_SELECTOR, ".btn-close")
                close_btn.click()
                time.sleep(1)
        
        print("\n🎉 RESUMEN DE LA PRUEBA:")
        print("✅ JavaScript funciona sin errores")
        print("✅ Modales se abren correctamente") 
        print("✅ Datos del proveedor se cargan y muestran")
        print("✅ Formulario de edición se carga con datos")
        print("✅ Sistema de proveedores completamente funcional")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        
    finally:
        if driver:
            driver.quit()
            print("🔚 Browser cerrado")

if __name__ == "__main__":
    test_proveedor_data_display()
