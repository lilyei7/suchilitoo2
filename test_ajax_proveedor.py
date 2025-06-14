#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple del formulario de proveedores AJAX
"""

import os
import django
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_restaurant.settings')
django.setup()

def test_ajax_form():
    """Test del formulario AJAX de proveedores"""
    print("🧪 Iniciando test del formulario AJAX...")
    
    # Configurar Chrome para test automatizado
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        # Inicializar el navegador
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        print("🌐 Navegando a la página de proveedores...")
        driver.get("http://127.0.0.1:8000/dashboard/proveedores/")
        
        # Hacer login si es necesario
        if "login" in driver.current_url:
            print("🔐 Haciendo login...")
            username_field = driver.find_element(By.NAME, "username")
            password_field = driver.find_element(By.NAME, "password")
            
            username_field.send_keys("admin")
            password_field.send_keys("admin123")
            
            login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_btn.click()
            
            wait.until(lambda d: "proveedores" in d.current_url)
        
        print("✅ En página de proveedores")
        
        # Hacer clic en el botón "Nuevo Proveedor"
        nuevo_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-bs-target='#nuevoProveedorModal']")))
        driver.execute_script("arguments[0].click();", nuevo_btn)
        
        print("🔄 Abriendo modal...")
        
        # Esperar a que el modal sea visible
        modal = wait.until(EC.visibility_of_element_located((By.ID, "nuevoProveedorModal")))
        
        print("📝 Llenando formulario...")
        
        # Llenar datos del formulario
        nombre_field = driver.find_element(By.ID, "nombre_comercial")
        nombre_field.clear()
        nombre_field.send_keys("Test AJAX Provider")
        
        email_field = driver.find_element(By.ID, "email")
        email_field.clear()
        email_field.send_keys("test@ajax.com")
        
        telefono_field = driver.find_element(By.ID, "telefono")
        telefono_field.clear()
        telefono_field.send_keys("5551234567")
        
        # Obtener URL actual para verificar que no cambie
        current_url = driver.current_url
        print(f"📍 URL actual: {current_url}")
        
        # Enviar formulario
        submit_btn = driver.find_element(By.CSS_SELECTOR, "#formNuevoProveedor button[type='submit']")
        
        print("🚀 Enviando formulario...")
        driver.execute_script("arguments[0].click();", submit_btn)
        
        # Esperar un momento para que se procese
        time.sleep(3)
        
        # Verificar que la URL no haya cambiado (no hubo redirect)
        new_url = driver.current_url
        print(f"📍 URL después del envío: {new_url}")
        
        if current_url == new_url:
            print("✅ ÉXITO: El formulario se envió via AJAX (no hubo redirect)")
            
            # Buscar el toast de éxito
            try:
                toast = driver.find_element(By.CSS_SELECTOR, ".toast")
                if toast and "éxito" in toast.text:
                    print("✅ Toast de éxito encontrado")
                else:
                    print("⚠️  Toast encontrado pero sin mensaje de éxito")
            except:
                print("⚠️  No se encontró toast (puede ser normal si se cerró rápido)")
        else:
            print("❌ ERROR: El formulario hizo redirect, no usó AJAX")
            print(f"   Cambió de: {current_url}")
            print(f"           a: {new_url}")
        
        # Verificar si el modal se cerró
        try:
            modal_style = modal.get_attribute("style")
            if "display: none" in modal_style or not modal.is_displayed():
                print("✅ Modal se cerró correctamente")
            else:
                print("⚠️  Modal aún visible")
        except:
            print("✅ Modal se cerró (elemento no encontrado)")
        
        print("🔄 Test completado")
        
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    test_ajax_form()
