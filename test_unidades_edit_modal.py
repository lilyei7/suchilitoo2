#!/usr/bin/env python3
"""
Test para verificar que las unidades de medida se cargan correctamente en el modal de edición
"""

import os
import sys
import django
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import time

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from restaurant.models import Insumo, UnidadMedida, CategoriaInsumo

def test_unidades_edit_modal():
    """Test que verifica que las unidades se cargan en el modal de edición"""
    
    print("=== TEST: VERIFICAR UNIDADES EN MODAL DE EDICION ===")
    
    # Configurar Chrome en modo headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    
    try:
        # Verificar que existen unidades en la base de datos
        unidades = list(UnidadMedida.objects.all().values('id', 'nombre', 'abreviacion'))
        print(f"✅ Unidades en BD: {len(unidades)}")
        for unidad in unidades:
            print(f"   - {unidad['nombre']} ({unidad['abreviacion']})")
        
        if not unidades:
            print("❌ No hay unidades en la base de datos")
            return False
        
        # Verificar que existe al menos un insumo
        insumo = Insumo.objects.first()
        if not insumo:
            print("❌ No hay insumos en la base de datos")
            return False
        
        print(f"✅ Insumo de prueba: {insumo.nombre} (ID: {insumo.id})")
        
        # 1. Ir a la página de login
        driver.get("http://localhost:8000/accounts/login/")
        print("✅ Página de login cargada")
        
        # 2. Hacer login
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Esperar a que la página de inventario cargue
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # 3. Ir a la página de inventario
        driver.get("http://localhost:8000/dashboard/inventario/")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        print("✅ Página de inventario cargada")
        
        # 4. Buscar el botón de editar del primer insumo
        edit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[onclick*='editarInsumo']")))
        print("✅ Botón de editar encontrado")
        
        # 5. Click en editar
        edit_button.click()
        print("✅ Click en editar ejecutado")
        
        # 6. Esperar a que el modal se abra
        modal = wait.until(EC.visibility_of_element_located((By.ID, "modalEditarInsumo")))
        print("✅ Modal de edición abierto")
        
        # 7. Verificar que el dropdown de unidades tiene opciones
        unidad_select = wait.until(EC.presence_of_element_located((By.ID, "editUnidadMedida")))
        print("✅ Dropdown de unidades encontrado")
        
        # Obtener todas las opciones del select
        options = unidad_select.find_elements(By.TAG_NAME, "option")
        print(f"✅ Número de opciones en el dropdown: {len(options)}")
        
        # Verificar el contenido de las opciones
        option_texts = []
        for option in options:
            text = option.text.strip()
            value = option.get_attribute('value')
            option_texts.append(f"{text} (value: {value})")
            print(f"   - Opción: {text} (valor: {value})")
        
        # Verificar que hay más de una opción (la primera suele ser "Seleccionar...")
        if len(options) > 1:
            print("✅ El dropdown tiene múltiples opciones de unidades")
            
            # Verificar que las unidades de la BD están en las opciones
            bd_nombres = [u['nombre'] for u in unidades]
            option_nombres = [option.text.strip() for option in options[1:]]  # Excluir primera opción
            
            matches = 0
            for bd_nombre in bd_nombres:
                if bd_nombre in option_nombres:
                    matches += 1
                    print(f"   ✅ Unidad '{bd_nombre}' encontrada en el dropdown")
                else:
                    print(f"   ❌ Unidad '{bd_nombre}' NO encontrada en el dropdown")
            
            if matches == len(bd_nombres):
                print("✅ TODAS las unidades de la BD están en el dropdown")
                return True
            else:
                print(f"❌ Solo {matches} de {len(bd_nombres)} unidades están en el dropdown")
                return False
        else:
            print("❌ El dropdown solo tiene una opción (probablemente vacío)")
            return False
            
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_unidades_edit_modal()
    if success:
        print("\n🎉 TEST EXITOSO: Las unidades se cargan correctamente en el modal de edición")
    else:
        print("\n❌ TEST FALLIDO: Problema con la carga de unidades en el modal de edición")
    
    sys.exit(0 if success else 1)
