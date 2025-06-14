#!/usr/bin/env python3
"""
Debug de las respuestas de las APIs
"""

import requests

def debug_api_responses():
    """Debug what the APIs are returning"""
    base_url = "http://127.0.0.1:8000"
    
    apis = [
        "/dashboard/api/insumos/basicos/",
        "/dashboard/api/categorias/",
        "/dashboard/api/unidades-medida/",
    ]
    
    for api in apis:
        print(f"\n{'='*50}")
        print(f"API: {api}")
        print('='*50)
        
        try:
            response = requests.get(f"{base_url}{api}")
            print(f"Status Code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'Not specified')}")
            print(f"Content Length: {len(response.text)}")
            print("\nFirst 500 characters:")
            print(response.text[:500])
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_api_responses()
