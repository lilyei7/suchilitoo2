#!/usr/bin/env python3
"""
Test script to verify the inventory JavaScript fixes are working correctly
"""

import time
import requests
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_django_server():
    """Test if Django server is responding"""
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        print(f"✓ Django server is responding (Status: {response.status_code})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Django server not responding: {e}")
        return False

def test_form_data_endpoint():
    """Test the form data API endpoint"""
    try:
        response = requests.get('http://127.0.0.1:8000/dashboard/insumos/form-data/', timeout=5)
        print(f"✓ Form data endpoint responding (Status: {response.status_code})")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  - Categories found: {len(data.get('categorias', []))}")
            print(f"  - Units found: {len(data.get('unidades', []))}")
            return True
        else:
            print(f"  - Response content: {response.text[:200]}...")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Form data endpoint error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error parsing form data response: {e}")
        return False

def test_javascript_functions():
    """Test JavaScript functions using Selenium"""
    print("\n=== Testing JavaScript Functions ===")
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navigate to inventory page
        print("Opening inventory page...")
        driver.get('http://127.0.0.1:8000/dashboard/inventario/')
        
        # Wait for page to load
        time.sleep(3)
        
        # Check if external JavaScript file is loaded
        js_loaded = driver.execute_script("""
            return typeof window.abrirModalCategoria === 'function' && 
                   typeof window.abrirModalUnidad === 'function' && 
                   typeof window.cargarDatosFormulario === 'function';
        """)
        
        if js_loaded:
            print("✓ JavaScript functions are properly loaded")
        else:
            print("✗ JavaScript functions not found")
            
        # Check for JavaScript errors in console
        logs = driver.get_log('browser')
        js_errors = [log for log in logs if log['level'] == 'SEVERE']
        
        if js_errors:
            print(f"✗ Found {len(js_errors)} JavaScript errors:")
            for error in js_errors[:3]:  # Show first 3 errors
                print(f"  - {error['message']}")
        else:
            print("✓ No severe JavaScript errors found")
            
        # Test if select elements exist
        try:
            categoria_select = driver.find_element(By.ID, "id_categoria")
            unidad_select = driver.find_element(By.ID, "id_unidad_medida")
            print("✓ Category and unit select elements found")
            
            # Check if options are populated
            categoria_options = categoria_select.find_elements(By.TAG_NAME, "option")
            unidad_options = unidad_select.find_elements(By.TAG_NAME, "option")
            
            print(f"  - Category options: {len(categoria_options)}")
            print(f"  - Unit options: {len(unidad_options)}")
            
        except NoSuchElementException as e:
            print(f"✗ Select elements not found: {e}")
            
        # Test cargarDatosFormulario function
        try:
            print("Testing cargarDatosFormulario function...")
            result = driver.execute_script("return window.cargarDatosFormulario();")
            time.sleep(2)  # Wait for AJAX call
            print("✓ cargarDatosFormulario executed successfully")
        except Exception as e:
            print(f"✗ Error executing cargarDatosFormulario: {e}")
            
        driver.quit()
        return True
        
    except Exception as e:
        print(f"✗ Selenium test failed: {e}")
        return False

def main():
    print("=== Testing Inventory JavaScript Fixes ===\n")
    
    # Test 1: Django server
    if not test_django_server():
        print("Cannot proceed - Django server not running")
        return
        
    # Test 2: API endpoint
    test_form_data_endpoint()
    
    # Test 3: JavaScript functionality
    try:
        test_javascript_functions()
    except Exception as e:
        print(f"JavaScript test failed: {e}")
        print("This might be due to missing ChromeDriver. Install it with: pip install webdriver-manager")
    
    print("\n=== Test Complete ===")
    print("If all tests pass, the JavaScript fixes are working correctly!")

if __name__ == "__main__":
    main()
