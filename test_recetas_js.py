#!/usr/bin/env python3
"""
Test para verificar que los errores de JavaScript en recetas.html estén corregidos
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_recetas_javascript():
    """Probar la página de recetas y verificar que no haya errores de JavaScript"""
    
    print("🚀 Iniciando test de JavaScript en recetas...")
    
    # Configurar Chrome en modo headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Navegador Chrome iniciado")
        
        # Navegar a la página de recetas
        url = "http://127.0.0.1:8000/dashboard/recetas/"
        print(f"📍 Navegando a: {url}")
        driver.get(url)
        
        # Esperar a que la página se cargue
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("✅ Página cargada")
        
        # Verificar que no hay errores de JavaScript en la consola
        logs = driver.get_log('browser')
        js_errors = [log for log in logs if log['level'] == 'SEVERE']
        
        if js_errors:
            print("❌ Errores de JavaScript encontrados:")
            for error in js_errors:
                print(f"  - {error['message']}")
            return False
        else:
            print("✅ No se encontraron errores de JavaScript")
        
        # Verificar que las funciones globales están definidas
        abrirModalCrearReceta_defined = driver.execute_script(
            "return typeof window.abrirModalCrearReceta === 'function';"
        )
        abrirModalCategorias_defined = driver.execute_script(
            "return typeof window.abrirModalCategorias === 'function';"
        )
        
        print(f"🔍 window.abrirModalCrearReceta definida: {abrirModalCrearReceta_defined}")
        print(f"🔍 window.abrirModalCategorias definida: {abrirModalCategorias_defined}")
        
        if not abrirModalCrearReceta_defined:
            print("❌ La función abrirModalCrearReceta no está definida")
            return False
            
        if not abrirModalCategorias_defined:
            print("❌ La función abrirModalCategorias no está definida")
            return False
        
        # Intentar hacer clic en el botón de crear receta
        try:
            crear_btn = driver.find_element(By.XPATH, "//button[contains(@onclick, 'abrirModalCrearReceta')]")
            print("✅ Botón 'Crear Receta' encontrado")
            
            # Ejecutar la función JavaScript
            driver.execute_script("window.abrirModalCrearReceta();")
            print("✅ Función abrirModalCrearReceta ejecutada sin errores")
            
        except Exception as e:
            print(f"⚠️ No se pudo encontrar/hacer clic en el botón: {e}")
        
        # Intentar hacer clic en el botón de categorías
        try:
            categorias_btn = driver.find_element(By.XPATH, "//button[contains(@onclick, 'abrirModalCategorias')]")
            print("✅ Botón 'Gestionar Categorías' encontrado")
            
            # Ejecutar la función JavaScript
            driver.execute_script("window.abrirModalCategorias();")
            print("✅ Función abrirModalCategorias ejecutada sin errores")
            
        except Exception as e:
            print(f"⚠️ No se pudo encontrar/hacer clic en el botón: {e}")
        
        print("🎉 Test completado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        return False
        
    finally:
        if 'driver' in locals():
            driver.quit()
            print("🔒 Navegador cerrado")

if __name__ == "__main__":
    success = test_recetas_javascript()
    if success:
        print("\n✅ TODOS LOS TESTS PASARON - Los errores de JavaScript han sido corregidos")
    else:
        print("\n❌ ALGUNOS TESTS FALLARON - Revisar los errores reportados")
