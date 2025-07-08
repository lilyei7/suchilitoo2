#!/usr/bin/env python3
"""
Test de API del editor de croquis en vivo
"""
import requests
import json

def test_api_croquis():
    print("🔍 TEST DE API CROQUIS EN VIVO")
    print("=" * 40)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: API de mesas
    print("\n1. TESTING API DE MESAS:")
    for sucursal_id in [1, 2, 3]:
        url = f"{base_url}/dashboard/api/croquis/mesas/{sucursal_id}/"
        print(f"   📡 GET {url}")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Success: {data.get('success', False)}")
                    print(f"   Mesas: {len(data.get('mesas', []))}")
                    
                    if data.get('mesas'):
                        print(f"   Primera mesa: {data['mesas'][0]}")
                except json.JSONDecodeError:
                    print(f"   ❌ Error decodificando JSON")
                    print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
                    print(f"   Content: {response.text[:200]}...")
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
                print(f"   Content: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Error de conexión - ¿Está el servidor corriendo?")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test 2: API de guardar (solo estructura, no enviamos datos)
    print("\n2. TESTING API DE GUARDAR (estructura):")
    url = f"{base_url}/dashboard/api/croquis/guardar/"
    print(f"   📡 URL: {url}")
    print("   (No enviamos datos - solo verificamos que el endpoint existe)")
    
    try:
        # Intentar sin CSRF para ver qué error obtenemos
        response = requests.post(url, 
                               json={"test": "structure"}, 
                               timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 403:
            print("   ✅ Error 403 esperado (CSRF protection activo)")
        elif response.status_code == 405:
            print("   ⚠️ Método no permitido")
        else:
            print(f"   Respuesta: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Error de conexión - ¿Está el servidor corriendo?")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 40)
    print("RECOMENDACIONES:")
    print("1. Verificar que el servidor Django esté corriendo en :8000")
    print("2. Verificar que no haya errores en los logs del servidor")
    print("3. Revisar la consola del navegador para errores JavaScript")

if __name__ == '__main__':
    test_api_croquis()
