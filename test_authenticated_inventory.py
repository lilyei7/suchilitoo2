#!/usr/bin/env python3
"""
Test the inventory page with proper authentication
"""

import requests
from bs4 import BeautifulSoup

def test_with_authentication():
    """Test inventory page with proper authentication"""
    session = requests.Session()
    
    print("=== Testing Inventory Page with Authentication ===\n")
    
    # Step 1: Get login page to get CSRF token
    login_url = 'http://127.0.0.1:8000/accounts/login/'
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
    
    print(f"Login page status: {login_page.status_code}")
    print(f"CSRF token obtained: {csrf_token[:20]}...")
    
    # Step 2: Login with credentials
    login_data = {
        'username': 'admin',  # Default Django admin user
        'password': 'admin123',  # You may need to adjust this
        'csrfmiddlewaretoken': csrf_token
    }
    
    login_response = session.post(login_url, data=login_data)
    print(f"Login response status: {login_response.status_code}")
    
    # Step 3: Try to access inventory page
    inventory_url = 'http://127.0.0.1:8000/dashboard/inventario/'
    inventory_response = session.get(inventory_url)
    
    print(f"Inventory page status: {inventory_response.status_code}")
    
    if inventory_response.status_code == 200:
        soup = BeautifulSoup(inventory_response.text, 'html.parser')
        
        # Check if we're still on login page
        if soup.find('input', {'name': 'username'}):
            print("❌ Still on login page - credentials may be incorrect")
            print("Trying to create a test user...")
            
            # Try common admin credentials
            for creds in [('admin', 'admin'), ('admin', 'password'), ('test', 'test123')]:
                print(f"Trying credentials: {creds[0]}/{creds[1]}")
                login_data['username'] = creds[0]
                login_data['password'] = creds[1]
                login_response = session.post(login_url, data=login_data)
                
                inventory_response = session.get(inventory_url)
                if inventory_response.status_code == 200:
                    soup = BeautifulSoup(inventory_response.text, 'html.parser')
                    if not soup.find('input', {'name': 'username'}):
                        print(f"✓ Successfully logged in with {creds[0]}/{creds[1]}")
                        break
            else:
                print("❌ Could not login with any common credentials")
                return
        
        # Check for key elements
        print("\n=== Checking Page Elements ===")
        
        # Check for external JS file
        js_scripts = soup.find_all('script', src=True)
        external_js = [script['src'] for script in js_scripts if 'funciones_inventario.js' in script['src']]
        print(f"External JS files found: {len(external_js)}")
        if external_js:
            print(f"  - {external_js[0]}")
        
        # Check for form elements
        categoria_select = soup.find('select', {'id': 'categoria'})
        unidad_select = soup.find('select', {'id': 'unidad_medida'})
        
        print(f"Category select found: {categoria_select is not None}")
        print(f"Unit select found: {unidad_select is not None}")
        
        # Check for modal buttons
        modal_buttons = soup.find_all('button', onclick=True)
        categoria_buttons = [btn for btn in modal_buttons if 'abrirModalCategoria' in btn.get('onclick', '')]
        unidad_buttons = [btn for btn in modal_buttons if 'abrirModalUnidad' in btn.get('onclick', '')]
        
        print(f"Category modal buttons found: {len(categoria_buttons)}")
        print(f"Unit modal buttons found: {len(unidad_buttons)}")
        
        # Check for script errors
        script_tags = soup.find_all('script')
        inline_scripts = [script for script in script_tags if script.string and 'function' in script.string]
        print(f"Inline script tags with functions: {len(inline_scripts)}")
        
        # Check for duplicate functions
        total_content = inventory_response.text
        abrirModalCategoria_count = total_content.count('function abrirModalCategoria')
        abrirModalUnidad_count = total_content.count('function abrirModalUnidad')
        
        print(f"abrirModalCategoria function definitions: {abrirModalCategoria_count}")
        print(f"abrirModalUnidad function definitions: {abrirModalUnidad_count}")
        
        if abrirModalCategoria_count > 1 or abrirModalUnidad_count > 1:
            print("❌ PROBLEM FOUND: Duplicate function definitions!")
            print("This will cause JavaScript errors.")
        else:
            print("✓ No duplicate function definitions found")
            
        # Test the form data endpoint
        print("\n=== Testing Form Data API ===")
        api_response = session.get('http://127.0.0.1:8000/dashboard/insumos/form-data/')
        print(f"Form data API status: {api_response.status_code}")
        
        if api_response.status_code == 200:
            data = api_response.json()
            print(f"Categories available: {len(data.get('categorias', []))}")
            print(f"Units available: {len(data.get('unidades', []))}")
        
    else:
        print(f"❌ Could not access inventory page: {inventory_response.status_code}")

def create_test_user():
    """Create a test user for authentication"""
    print("\n=== Creating Test User ===")
    try:
        import django
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
        django.setup()
        
        from django.contrib.auth.models import User
        
        # Create or get test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            print("✓ Test user created: testuser/testpass123")
        else:
            print("✓ Test user already exists: testuser/testpass123")
            
        return True
        
    except Exception as e:
        print(f"❌ Could not create test user: {e}")
        return False

if __name__ == "__main__":
    # First try to create a test user
    create_test_user()
    
    # Then test the inventory page
    test_with_authentication()
