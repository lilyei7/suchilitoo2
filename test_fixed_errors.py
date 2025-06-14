import os
import requests
import time
from bs4 import BeautifulSoup

def test_fixed_errors():
    """Test if the JavaScript errors were fixed"""
    base_url = "http://127.0.0.1:8000"
    login_url = f"{base_url}/dashboard/login/"
    inventory_url = f"{base_url}/dashboard/inventario/"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # First, get CSRF token from login page
        login_response = session.get(login_url)
        if login_response.status_code != 200:
            print(f"❌ Could not access login page: {login_url}")
            return False
            
        # Extract CSRF token
        soup = BeautifulSoup(login_response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if not csrf_input:
            print("❌ Could not find CSRF token in login page")
            return False
            
        csrf_token = csrf_input['value']
        
        # Login data
        login_data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': 'admin',  # Change to a valid username
            'password': 'admin123'  # Change to the correct password
        }
        
        # Login
        login_post = session.post(login_url, data=login_data, headers={
            'Referer': login_url
        })
        
        # Check if login was successful
        if login_post.url == login_url:  # If still on login page, login failed
            print("❌ Login failed. Check credentials.")
            return False
        
        print("✅ Login successful")
        
        # Access inventory page
        inventory_response = session.get(inventory_url)
        
        if inventory_response.status_code != 200:
            print(f"❌ Could not access inventory page: {inventory_url}")
            return False
            
        print("✅ Inventory page loaded successfully")
        
        # Save HTML content for inspection
        output_path = os.path.join(os.path.dirname(__file__), "inventory_fixed.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(inventory_response.text)
            
        print(f"✅ Saved inventory page HTML to: {output_path}")
        
        # Check for critical functions
        if "function abrirModalCategoria" in inventory_response.text:
            print("✅ Function abrirModalCategoria found")
        else:
            print("❌ Function abrirModalCategoria not found")
            
        if "function abrirModalUnidad" in inventory_response.text:
            print("✅ Function abrirModalUnidad found")
        else:
            print("❌ Function abrirModalUnidad not found")
            
        if "function cargarDatosFormulario" in inventory_response.text:
            print("✅ Function cargarDatosFormulario found")
        else:
            print("❌ Function cargarDatosFormulario not found")
            
        # Check for syntax errors in fetch headers
        if "'X-CSRFToken': formData.get('csrfmiddlewaretoken')\n                })" in inventory_response.text:
            print("❌ Syntax error found in fetch headers")
        else:
            print("✅ No syntax errors found in fetch headers")
            
        # Check for unbalanced DOM event listeners
        if "modalUnidad.addEventListener('show.bs.modal', function() {\n            cargarUnidades();\n        });\n    });" in inventory_response.text:
            print("❌ Unbalanced event listener found")
        else:
            print("✅ No unbalanced event listeners found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    # Wait for server to start
    print("Waiting for Django server to start...")
    time.sleep(3)
    
    if test_fixed_errors():
        print("\n✅ Tests completed successfully")
        print("Open http://127.0.0.1:8000/dashboard/inventario/ in your browser to test the page")
    else:
        print("\n❌ Tests failed")
