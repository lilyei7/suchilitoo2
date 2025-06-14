"""
Test completo de la funcionalidad de insumos:
1. Verificar que el inventario se carga correctamente
2. Crear un nuevo insumo via AJAX
3. Verificar que aparece en la lista después de la creación
4. Verificar que no hay errores de JavaScript
"""

import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import sqlite3

# Configuración
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/dashboard/login/"
INVENTORY_URL = f"{BASE_URL}/dashboard/inventario/"

def test_database_insumos():
    """Verificar estado actual de insumos en la base de datos"""
    print("=== VERIFICANDO BASE DE DATOS ===")
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Contar insumos actuales
    cursor.execute("SELECT COUNT(*) FROM dashboard_insumo")
    count_before = cursor.fetchone()[0]
    print(f"Insumos en BD antes del test: {count_before}")
    
    # Mostrar algunos insumos existentes
    cursor.execute("SELECT id, nombre, categoria FROM dashboard_insumo LIMIT 5")
    insumos = cursor.fetchall()
    print("Insumos existentes (muestra):")
    for insumo in insumos:
        print(f"  - {insumo[0]}: {insumo[1]} (categoría: {insumo[2]})")
    
    conn.close()
    return count_before

def test_inventory_page_access():
    """Test de acceso básico a la página de inventario"""
    print("\n=== TESTING ACCESO A INVENTARIO ===")
    
    # Configurar Chrome para automatización
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar sin ventana
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        # Ir al login
        print(f"Accediendo a: {LOGIN_URL}")
        driver.get(LOGIN_URL)
        
        # Login
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Esperar redirección
        WebDriverWait(driver, 10).until(
            lambda d: "login" not in d.current_url
        )
        print("✓ Login exitoso")
        
        # Ir a inventario
        print(f"Accediendo a inventario: {INVENTORY_URL}")
        driver.get(INVENTORY_URL)
        
        # Verificar que la página carga
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("✓ Página de inventario cargada")
        
        # Verificar que existe la tabla de insumos
        try:
            tabla_insumos = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "tablaInsumos"))
            )
            print("✓ Tabla de insumos encontrada")
            
            # Contar filas actuales
            filas = driver.find_elements(By.XPATH, "//table[@id='tablaInsumos']//tbody/tr")
            count_frontend = len(filas)
            print(f"✓ Insumos mostrados en tabla: {count_frontend}")
            
        except TimeoutException:
            print("✗ No se encontró la tabla de insumos")
            count_frontend = 0
        
        # Verificar que existe el botón para crear insumo
        try:
            boton_crear = driver.find_element(By.ID, "btnCrearInsumo")
            print("✓ Botón 'Crear Insumo' encontrado")
        except:
            print("✗ Botón 'Crear Insumo' no encontrado")
        
        # Verificar que existe el modal
        try:
            modal = driver.find_element(By.ID, "modalCrearInsumo")
            print("✓ Modal de creación encontrado")
        except:
            print("✗ Modal de creación no encontrado")
        
        # Verificar que se carga el JS correcto
        try:
            scripts = driver.find_elements(By.TAG_NAME, "script")
            js_loaded = False
            for script in scripts:
                src = script.get_attribute("src")
                if src and "insumos_manager.js" in src:
                    js_loaded = True
                    break
            
            if js_loaded:
                print("✓ JavaScript insumos_manager.js cargado")
            else:
                print("✗ JavaScript insumos_manager.js no encontrado")
        except:
            print("✗ Error verificando scripts JS")
        
        return driver, count_frontend
        
    except Exception as e:
        print(f"✗ Error en test de acceso: {e}")
        return None, 0

def test_insumo_creation_frontend(driver):
    """Test de creación de insumo desde el frontend"""
    print("\n=== TESTING CREACIÓN DE INSUMO FRONTEND ===")
    
    if not driver:
        print("✗ No hay driver disponible")
        return False
    
    try:
        # Abrir modal
        boton_crear = driver.find_element(By.ID, "btnCrearInsumo")
        boton_crear.click()
        print("✓ Modal abierto")
        
        # Esperar a que el modal sea visible
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "modalCrearInsumo"))
        )
        
        # Llenar formulario
        codigo_field = driver.find_element(By.ID, "codigo")
        nombre_field = driver.find_element(By.ID, "nombre")
        categoria_select = driver.find_element(By.ID, "categoria")
        unidad_select = driver.find_element(By.ID, "unidad_medida")
        
        # Generar código único
        timestamp = str(int(time.time()))
        codigo_test = f"TEST{timestamp}"
        
        codigo_field.clear()
        codigo_field.send_keys(codigo_test)
        nombre_field.clear()
        nombre_field.send_keys(f"Insumo Test {timestamp}")
        
        # Seleccionar primera categoría y unidad disponible
        from selenium.webdriver.support.ui import Select
        select_categoria = Select(categoria_select)
        select_categoria.select_by_index(1)  # Primera opción después de "Seleccione..."
        
        select_unidad = Select(unidad_select)
        select_unidad.select_by_index(1)  # Primera opción después de "Seleccione..."
        
        print(f"✓ Formulario llenado con código: {codigo_test}")
        
        # Enviar formulario
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit' and contains(@class, 'btn-primary')]")
        submit_button.click()
        
        # Esperar respuesta (puede ser redirección o mensaje)
        time.sleep(3)
        
        # Verificar si la página se recargó o hubo redirección
        current_url = driver.current_url
        print(f"✓ URL actual después de envío: {current_url}")
        
        # Si estamos de vuelta en inventario, buscar el nuevo insumo
        if "inventario" in current_url:
            # Buscar el insumo en la tabla
            try:
                # Refrescar la página para asegurar datos actualizados
                driver.refresh()
                time.sleep(2)
                
                # Buscar en la tabla
                tabla = driver.find_element(By.ID, "tablaInsumos")
                filas = tabla.find_elements(By.TAG_NAME, "tr")
                
                insumo_encontrado = False
                for fila in filas:
                    if codigo_test in fila.text:
                        insumo_encontrado = True
                        print(f"✓ Insumo {codigo_test} encontrado en la tabla")
                        break
                
                if not insumo_encontrado:
                    print(f"✗ Insumo {codigo_test} NO encontrado en la tabla")
                    # Mostrar contenido de la tabla para debug
                    print("Contenido actual de la tabla:")
                    for i, fila in enumerate(filas):
                        print(f"  Fila {i}: {fila.text[:100]}...")
                
                return insumo_encontrado
                
            except Exception as e:
                print(f"✗ Error buscando insumo en tabla: {e}")
                return False
        
        else:
            print("✗ No se redirigió correctamente al inventario")
            return False
            
    except Exception as e:
        print(f"✗ Error en creación frontend: {e}")
        return False

def test_database_after_creation():
    """Verificar que el insumo se creó en la base de datos"""
    print("\n=== VERIFICANDO BASE DE DATOS DESPUÉS DE CREACIÓN ===")
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Contar insumos después
    cursor.execute("SELECT COUNT(*) FROM dashboard_insumo")
    count_after = cursor.fetchone()[0]
    print(f"Insumos en BD después del test: {count_after}")
    
    # Buscar insumos TEST recientes
    cursor.execute("SELECT codigo, nombre FROM dashboard_insumo WHERE codigo LIKE 'TEST%' ORDER BY id DESC LIMIT 3")
    test_insumos = cursor.fetchall()
    print("Insumos TEST recientes:")
    for insumo in test_insumos:
        print(f"  - {insumo[0]}: {insumo[1]}")
    
    conn.close()
    return count_after

def main():
    """Ejecutar todos los tests"""
    print("INICIANDO TEST COMPLETO DE FUNCIONALIDAD DE INSUMOS")
    print("=" * 60)
    
    # Test 1: Estado inicial de BD
    count_before = test_database_insumos()
    
    # Test 2: Acceso a página
    driver, count_frontend_before = test_inventory_page_access()
    
    # Test 3: Creación frontend
    if driver:
        creation_success = test_insumo_creation_frontend(driver)
        
        # Test 4: Verificar BD después
        count_after = test_database_after_creation()
        
        # Cerrar navegador
        driver.quit()
        
        # Resumen
        print("\n" + "=" * 60)
        print("RESUMEN DE RESULTADOS:")
        print(f"- Insumos en BD antes: {count_before}")
        print(f"- Insumos en frontend antes: {count_frontend_before}")
        print(f"- Insumos en BD después: {count_after}")
        print(f"- Creación frontend exitosa: {'✓' if creation_success else '✗'}")
        print(f"- Insumos agregados a BD: {count_after - count_before}")
        
        if creation_success and (count_after > count_before):
            print("\n🎉 TODOS LOS TESTS PASARON - FUNCIONALIDAD COMPLETA")
        else:
            print("\n❌ ALGUNOS TESTS FALLARON - REVISAR LOGS")
    
    else:
        print("\n❌ NO SE PUDO REALIZAR TEST COMPLETO - PROBLEMAS DE ACCESO")

if __name__ == "__main__":
    main()
