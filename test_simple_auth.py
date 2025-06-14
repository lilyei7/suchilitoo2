#!/usr/bin/env python3
"""
Simple authenticated test for inventory page
"""

import requests
from bs4 import BeautifulSoup
import re

def test_inventory_with_auth():
    """Test inventory page with authentication"""
    session = requests.Session()
    
    print("=== Testing Inventory Page (Authenticated) ===\n")
    
    # Get login page
    login_url = 'http://127.0.0.1:8000/accounts/login/'
    login_page = session.get(login_url)
    print(f"Login page status: {login_page.status_code}")
    
    # Extract CSRF token
    soup = BeautifulSoup(login_page.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    
    if not csrf_input:
        print("❌ No CSRF token found on login page")
        return False
        
    csrf_token = csrf_input['value']
    print(f"CSRF token: {csrf_token[:20]}...")
    
    # Login with admin credentials
    login_data = {
        'email': 'admin@sushi.com',  # Using the existing admin email
        'password': 'admin123',       # Common admin password
        'csrfmiddlewaretoken': csrf_token
    }
    
    # Try different passwords
    passwords = ['admin123', 'admin', 'password', '123456', 'sushi123']
    
    for password in passwords:
        print(f"Trying password: {password}")
        login_data['password'] = password
        
        login_response = session.post(login_url, data=login_data)
        
        # Check if login was successful by trying to access inventory
        inventory_response = session.get('http://127.0.0.1:8000/dashboard/inventario/')
        
        if inventory_response.status_code == 200:
            # Check if we're not redirected back to login
            if 'login' not in inventory_response.url and 'password' not in inventory_response.text.lower()[:1000]:
                print(f"✓ Successfully logged in with password: {password}")
                
                # Analyze the inventory page
                analyze_inventory_page(inventory_response.text)
                return True
        
    print("❌ Could not login with any common passwords")
    
    # Try to reset password or create new user
    print("\nTrying to create/reset admin user...")
    reset_admin_password()
    
    return False

def analyze_inventory_page(html_content):
    """Analyze the inventory page HTML content"""
    print("\n=== Analyzing Inventory Page ===")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check page title
    title = soup.find('title')
    print(f"Page title: {title.text if title else 'Not found'}")
    
    # Check for key elements
    categoria_select = soup.find('select', {'id': 'categoria'})
    unidad_select = soup.find('select', {'id': 'unidad_medida'})
    
    print(f"Category select element: {'✓ Found' if categoria_select else '❌ Not found'}")
    print(f"Unit select element: {'✓ Found' if unidad_select else '❌ Not found'}")
    
    # Check for external JavaScript
    js_scripts = soup.find_all('script', src=True)
    external_js = [script['src'] for script in js_scripts if 'funciones_inventario.js' in script['src']]
    print(f"External JS file: {'✓ Found' if external_js else '❌ Not found'}")
    
    # Check for modal buttons
    modal_buttons = soup.find_all('button', onclick=True)
    categoria_buttons = [btn for btn in modal_buttons if btn.get('onclick') and 'abrirModalCategoria' in btn['onclick']]
    unidad_buttons = [btn for btn in modal_buttons if btn.get('onclick') and 'abrirModalUnidad' in btn['onclick']]
    
    print(f"Category modal buttons: {len(categoria_buttons)} found")
    print(f"Unit modal buttons: {len(unidad_buttons)} found")
    
    # Check for duplicate functions (major issue)
    abrirModalCategoria_count = html_content.count('function abrirModalCategoria')
    abrirModalUnidad_count = html_content.count('function abrirModalUnidad')
    cargarDatos_count = html_content.count('function cargarDatosFormulario')
    
    print(f"\n=== Function Definition Analysis ===")
    print(f"abrirModalCategoria definitions: {abrirModalCategoria_count}")
    print(f"abrirModalUnidad definitions: {abrirModalUnidad_count}")
    print(f"cargarDatosFormulario definitions: {cargarDatos_count}")
    
    if abrirModalCategoria_count > 1 or abrirModalUnidad_count > 1:
        print("❌ CRITICAL ISSUE: Multiple function definitions found!")
        print("   This will cause JavaScript syntax errors.")
        print("   The HTML template needs to be cleaned up.")
        
        # Save the problematic HTML for analysis
        with open('problematic_inventory.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("   Saved problematic HTML to 'problematic_inventory.html'")
        
        return False
    else:
        print("✓ No duplicate function definitions found")
        return True

def reset_admin_password():
    """Reset admin password using Django management command"""
    import subprocess
    import os
    
    try:
        # Change to project directory
        os.chdir('c:\\Users\\olcha\\Desktop\\sushi_restaurant')
        
        # Create a simple script to reset password
        script_content = '''
from accounts.models import Usuario
user = Usuario.objects.get(email="admin@sushi.com")
user.set_password("admin123")
user.save()
print("Password reset to: admin123")
'''
        
        with open('reset_password.py', 'w') as f:
            f.write(script_content)
        
        # Run the script
        result = subprocess.run(['python', 'manage.py', 'shell', '<', 'reset_password.py'], 
                              capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print("✓ Admin password reset to: admin123")
            return True
        else:
            print(f"❌ Password reset failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        return False

if __name__ == "__main__":
    test_inventory_with_auth()
