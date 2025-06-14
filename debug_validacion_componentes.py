"""
Script para depurar el problema de validación de componentes en el formulario de insumos compuestos.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def debug_validacion_componentes():
    """Debugs la validación de componentes paso a paso"""
    
    # Configurar Chrome para ver consola
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    
    # Inicializar driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        print("📱 Abriendo página de inventario...")
        driver.get("http://127.0.0.1:8000/dashboard/inventario/")
        
        # Login
        print("🔐 Haciendo login...")
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.send_keys("admin")
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys("admin123")
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Esperar que cargue el dashboard
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "card"))
        )
        
        print("✅ Login exitoso")
        
        # Ir a la sección de insumos compuestos
        print("📋 Navegando a insumos compuestos...")
        compuestos_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#compuestos']"))
        )
        compuestos_tab.click()
        time.sleep(1)
        
        # Abrir modal de crear compuesto
        print("🆕 Abriendo modal de crear compuesto...")
        crear_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[onclick='abrirModalCrearCompuesto()']"))
        )
        crear_btn.click()
        time.sleep(1)
        
        # Llenar datos básicos
        print("📝 Llenando datos básicos...")
        nombre_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nombre"))
        )
        nombre_input.send_keys("Sushi Debug Test")
        
        descripcion_input = driver.find_element(By.ID, "descripcion")
        descripcion_input.send_keys("Prueba de debug para validación")
        
        cantidad_input = driver.find_element(By.ID, "cantidad_producida")
        cantidad_input.clear()
        cantidad_input.send_keys("10")
        
        # Agregar componente
        print("➕ Agregando componente...")
        agregar_btn = driver.find_element(By.CSS_SELECTOR, "button[onclick='agregarComponente()']")
        agregar_btn.click()
        time.sleep(1)
        
        # Verificar que se creó el componente
        componentes = driver.find_elements(By.CLASS_NAME, "componente-item")
        print(f"🔍 Componentes encontrados: {len(componentes)}")
        
        if len(componentes) > 0:
            # Seleccionar insumo en el primer componente
            print("🥢 Seleccionando insumo...")
            select_element = componentes[0].find_element(By.CSS_SELECTOR, "select[name='componente_insumo[]']")
            select = Select(select_element)
            
            # Listar opciones disponibles
            options = select.options
            print(f"📋 Opciones de insumos disponibles: {len(options)}")
            for i, option in enumerate(options[:5]):  # Mostrar primeras 5
                print(f"  {i}: {option.text}")
            
            if len(options) > 1:
                select.select_by_index(1)  # Seleccionar el primer insumo real
                time.sleep(0.5)
                
                # Llenar cantidad
                print("📊 Llenando cantidad...")
                cantidad_componente = componentes[0].find_element(By.CSS_SELECTOR, "input[name='componente_cantidad[]']")
                cantidad_componente.clear()
                cantidad_componente.send_keys("2.5")
                time.sleep(0.5)
                
                # Verificar valores antes de enviar
                print("🔍 Verificando valores del componente:")
                select_value = select_element.get_attribute('value')
                cantidad_value = cantidad_componente.get_attribute('value')
                print(f"  - Insumo seleccionado: {select_value}")
                print(f"  - Cantidad ingresada: {cantidad_value}")
                
                # Ejecutar JavaScript para ver debug en consola
                print("🔍 Ejecutando debug de JavaScript...")
                debug_script = """
                console.log('=== DEBUG MANUAL ===');
                const componentes = document.querySelectorAll('.componente-item');
                console.log('Componentes encontrados:', componentes.length);
                
                let componentesInfo = [];
                let componentesValidos = true;
                
                componentes.forEach((item, index) => {
                    const select = item.querySelector('select[name="componente_insumo[]"]');
                    const input = item.querySelector('input[name="componente_cantidad[]"]');
                    
                    const selectValue = select ? select.value : '';
                    const inputValue = input ? input.value : '';
                    const inputNumber = parseFloat(inputValue) || 0;
                    
                    console.log(`Componente ${index + 1}:`);
                    console.log('  - Select element:', select);
                    console.log('  - Select value:', selectValue);
                    console.log('  - Input element:', input);
                    console.log('  - Input value:', inputValue);
                    console.log('  - Input number:', inputNumber);
                    
                    componentesInfo.push({
                        index: index + 1,
                        insumo: selectValue,
                        cantidad: inputValue,
                        cantidadNum: inputNumber
                    });
                    
                    if (!selectValue || !inputValue || inputNumber <= 0) {
                        componentesValidos = false;
                        console.log(`  - ❌ Componente ${index + 1} INVÁLIDO`);
                    } else {
                        console.log(`  - ✅ Componente ${index + 1} VÁLIDO`);
                    }
                });
                
                console.log('Resumen componentes válidos:', componentesValidos);
                console.log('Info completa componentes:', componentesInfo);
                
                return {
                    componentesValidos: componentesValidos,
                    componentesInfo: componentesInfo
                };
                """
                
                result = driver.execute_script(debug_script)
                print(f"📊 Resultado del debug JS: {result}")
                
                # Intentar enviar formulario
                print("📤 Intentando enviar formulario...")
                submit_btn = driver.find_element(By.CSS_SELECTOR, "#formCrearCompuesto button[type='submit']")
                submit_btn.click()
                time.sleep(2)
                
                # Verificar si hay errores en consola
                print("🔍 Verificando logs de consola...")
                logs = driver.get_log('browser')
                for log in logs[-10:]:  # Últimos 10 logs
                    if log['level'] in ['SEVERE', 'WARNING']:
                        print(f"  {log['level']}: {log['message']}")
                
                print("✅ Debug completado. Revisar consola del navegador para más detalles.")
            else:
                print("❌ No hay insumos básicos disponibles")
        else:
            print("❌ No se pudo crear el componente")
        
        time.sleep(5)  # Mantener abierto para inspección manual
        
    except Exception as e:
        print(f"❌ Error durante el debug: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("🔚 Cerrando navegador...")
        input("Presiona Enter para cerrar el navegador...")
        driver.quit()

if __name__ == "__main__":
    debug_validacion_componentes()
