#!/usr/bin/env python3
"""
Test de navegación del sistema web - Insumos Compuestos
Verifica que la interfaz web esté funcionando correctamente
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_web_interface():
    """Test de la interfaz web"""
    print("=== TEST DE INTERFAZ WEB - INSUMOS COMPUESTOS ===\n")
    
    # Configurar Chrome en modo headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✓ Navegador Chrome iniciado")
        
        # 1. Verificar que el servidor esté corriendo
        print("\n1. Verificando acceso al servidor...")
        driver.get("http://127.0.0.1:8001/")
        
        # Esperar a que la página cargue
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        print(f"   ✓ Página principal cargada: {driver.title}")
        
        # 2. Verificar acceso a insumos compuestos
        print("\n2. Navegando a insumos compuestos...")
        driver.get("http://127.0.0.1:8001/dashboard/insumos-compuestos/")
        
        # Verificar que la página se carga
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        
        # Verificar título de la página
        page_title = driver.find_element(By.TAG_NAME, "h1").text
        print(f"   ✓ Página de insumos compuestos cargada: {page_title}")
        
        # 3. Verificar elementos clave de la interfaz
        print("\n3. Verificando elementos de la interfaz...")
        
        # Verificar que existe el botón de crear
        try:
            create_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Nuevo Insumo Compuesto')]")
            print("   ✓ Botón 'Nuevo Insumo Compuesto' encontrado")
        except NoSuchElementException:
            print("   ⚠ Botón 'Nuevo Insumo Compuesto' no encontrado")
        
        # Verificar que existe la tabla
        try:
            table = driver.find_element(By.TAG_NAME, "table")
            print("   ✓ Tabla de insumos compuestos encontrada")
            
            # Contar filas de datos
            rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
            print(f"   ✓ Filas de datos en tabla: {len(rows)}")
            
        except NoSuchElementException:
            print("   ⚠ Tabla de insumos compuestos no encontrada")
        
        # 4. Verificar JavaScript y funcionalidades
        print("\n4. Verificando carga de JavaScript...")
        
        # Verificar que jQuery está cargado
        jquery_loaded = driver.execute_script("return typeof jQuery !== 'undefined'")
        print(f"   ✓ jQuery cargado: {'Sí' if jquery_loaded else 'No'}")
        
        # Verificar que Bootstrap está cargado
        bootstrap_loaded = driver.execute_script("return typeof bootstrap !== 'undefined'")
        print(f"   ✓ Bootstrap cargado: {'Sí' if bootstrap_loaded else 'No'}")
        
        # 5. Verificar consola sin errores
        print("\n5. Verificando errores de JavaScript...")
        logs = driver.get_log('browser')
        errors = [log for log in logs if log['level'] == 'SEVERE']
        
        if errors:
            print(f"   ⚠ Se encontraron {len(errors)} errores en la consola:")
            for error in errors[:3]:  # Mostrar solo los primeros 3
                print(f"      - {error['message']}")
        else:
            print("   ✓ No se encontraron errores graves en la consola")
        
        # 6. Test básico de navegación
        print("\n6. Probando navegación básica...")
        
        # Verificar enlaces del sidebar
        try:
            sidebar_links = driver.find_elements(By.CSS_SELECTOR, "aside a")
            print(f"   ✓ Enlaces en sidebar: {len(sidebar_links)}")
        except NoSuchElementException:
            print("   ⚠ Sidebar no encontrado")
        
        print("\n=== TEST WEB COMPLETADO ===")
        return True
        
    except TimeoutException:
        print("   ❌ Timeout: La página tardó demasiado en cargar")
        return False
    except Exception as e:
        print(f"   ❌ Error durante el test: {str(e)}")
        return False
    finally:
        try:
            driver.quit()
            print("✓ Navegador cerrado")
        except:
            pass

if __name__ == '__main__':
    # Verificar si el servidor está corriendo
    import requests
    try:
        response = requests.get("http://127.0.0.1:8001/", timeout=5)
        if response.status_code == 200:
            print("✓ Servidor Django detectado en puerto 8001")
            test_web_interface()
        else:
            print("❌ Servidor Django no responde correctamente")
    except requests.exceptions.RequestException:
        print("❌ No se puede conectar al servidor Django en puerto 8001")
        print("   Asegúrate de que el servidor esté corriendo con: python manage.py runserver 8001")
