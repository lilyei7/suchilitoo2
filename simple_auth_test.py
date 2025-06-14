#!/usr/bin/env python3
"""
Simple test to verify authentication and inventory page access
"""

import requests
from bs4 import BeautifulSoup

def test_login_and_inventory():
    """Test login and access to inventory page"""
    session = requests.Session()
    
    print("=== Testing Login and Inventory Access ===\n")
      # Step 1: Get login page and CSRF token
    login_url = 'http://127.0.0.1:8000/dashboard/login/'
    try:
        login_page = session.get(login_url)
        print(f"Login page status: {login_page.status_code}")
        
        if login_page.status_code != 200:
            print("❌ Cannot access login page")
            return
            
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if not csrf_token:
            print("❌ CSRF token not found")
            return
            
        csrf_value = csrf_token['value']
        print(f"✓ CSRF token obtained: {csrf_value[:20]}...")
        
    except Exception as e:
        print(f"❌ Error getting login page: {e}")
        return
      # Step 2: Login
    login_data = {
        'username': 'admin',  # Use the actual username
        'password': 'admin123',
        'csrfmiddlewaretoken': csrf_value
    }
    
    try:
        login_response = session.post(login_url, data=login_data)
        print(f"Login response status: {login_response.status_code}")
        
        # Check if we were redirected (successful login)
        if login_response.status_code in [200, 302]:
            print("✓ Login request completed")
        else:
            print(f"❌ Login failed with status {login_response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return
    
    # Step 3: Access inventory page
    inventory_url = 'http://127.0.0.1:8000/dashboard/inventario/'
    try:
        inventory_response = session.get(inventory_url)
        print(f"Inventory page status: {inventory_response.status_code}")
        
        if inventory_response.status_code == 200:
            print("✓ Successfully accessed inventory page")
            
            # Quick check for key content
            content = inventory_response.text
              # Check if we're actually on the inventory page (not redirected to login)
            if 'username' in content and 'password' in content and 'csrfmiddlewaretoken' in content:
                print("❌ Still on login page - authentication failed")
                print("Try manually logging in at: http://127.0.0.1:8000/dashboard/login/")
                print("Username: admin")
                print("Password: admin123")
                return
            
            # Check for key inventory elements
            if 'funciones_inventario.js' in content:
                print("✓ External JavaScript file included")
            else:
                print("❌ External JavaScript file not found")
            
            if 'id="categoria"' in content or 'id="id_categoria"' in content:
                print("✓ Category select element found")
            else:
                print("❌ Category select element not found")
                
            if 'id="unidad_medida"' in content or 'id="id_unidad_medida"' in content:
                print("✓ Unit select element found")
            else:
                print("❌ Unit select element not found")
            
            # Check for function definitions
            abrirModalCategoria_count = content.count('abrirModalCategoria')
            abrirModalUnidad_count = content.count('abrirModalUnidad')
            
            print(f"abrirModalCategoria references: {abrirModalCategoria_count}")
            print(f"abrirModalUnidad references: {abrirModalUnidad_count}")
            
            if abrirModalCategoria_count > 0 and abrirModalUnidad_count > 0:
                print("✓ Modal functions are referenced")
            else:
                print("❌ Modal functions not found")
            
        else:
            print(f"❌ Cannot access inventory page: {inventory_response.status_code}")
            if inventory_response.status_code == 302:
                print("Redirected - possibly to login page")
            
    except Exception as e:
        print(f"❌ Error accessing inventory page: {e}")
    
    # Step 4: Test API endpoint
    print("\n=== Testing Form Data API ===")
    try:
        api_response = session.get('http://127.0.0.1:8000/dashboard/insumos/form-data/')
        print(f"Form data API status: {api_response.status_code}")
        
        if api_response.status_code == 200:
            data = api_response.json()
            categorias = data.get('categorias', [])
            unidades = data.get('unidades', [])
            
            print(f"✓ Categories: {len(categorias)}")
            print(f"✓ Units: {len(unidades)}")
            
            if categorias:
                print(f"  Sample categories: {[cat['nombre'] for cat in categorias[:3]]}")
            if unidades:
                print(f"  Sample units: {[unit['nombre'] for unit in unidades[:3]]}")
                
        else:
            print(f"❌ API error: {api_response.status_code}")
            
    except Exception as e:
        print(f"❌ API test error: {e}")

if __name__ == "__main__":
    test_login_and_inventory()
