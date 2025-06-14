#!/usr/bin/env python3
"""
Simple test to verify JavaScript functionality
"""

import requests
import json

def test_api_endpoints():
    """Test all relevant API endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== Testing API Endpoints ===\n")
    
    # Test form data endpoint
    try:
        response = requests.get(f"{base_url}/dashboard/insumos/form-data/")
        print(f"Form Data Endpoint: Status {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            categorias = data.get('categorias', [])
            unidades = data.get('unidades', [])
            
            print(f"✓ Categories loaded: {len(categorias)}")
            if categorias:
                print(f"  - Sample categories: {[cat['nombre'] for cat in categorias[:3]]}")
                
            print(f"✓ Units loaded: {len(unidades)}")
            if unidades:
                print(f"  - Sample units: {[unit['nombre'] for unit in unidades[:3]]}")
        else:
            print(f"✗ Error: {response.text}")
            
    except Exception as e:
        print(f"✗ API test failed: {e}")
    
    # Test main inventory page
    try:
        response = requests.get(f"{base_url}/dashboard/inventario/")
        print(f"\nInventory Page: Status {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check if external JS file is included
            if 'funciones_inventario.js' in content:
                print("✓ External JavaScript file is included")
            else:
                print("✗ External JavaScript file not found in HTML")
                
            # Check for key elements
            if 'id_categoria' in content:
                print("✓ Category select element found")
            else:
                print("✗ Category select element not found")
                
            if 'id_unidad_medida' in content:
                print("✓ Unit select element found")
            else:
                print("✗ Unit select element not found")
                
        else:
            print(f"✗ Error loading page: {response.text[:200]}")
            
    except Exception as e:
        print(f"✗ Page test failed: {e}")

def main():
    test_api_endpoints()
    
    print("\n=== Summary ===")
    print("If the API endpoints are working and the page loads correctly,")
    print("the JavaScript functions should now load categories and units properly.")
    print("\nTo verify in browser:")
    print("1. Open http://127.0.0.1:8000/dashboard/inventario/")
    print("2. Check browser console for errors (F12)")
    print("3. Try adding a new insumo to see if dropdowns populate")

if __name__ == "__main__":
    main()
