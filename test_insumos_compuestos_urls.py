#!/usr/bin/env python3
"""
Test para verificar que las URLs de insumos compuestos funcionan correctamente
"""

import requests
import sys

def test_insumos_compuestos_urls():
    """Test básico de las URLs"""
    base_url = "http://127.0.0.1:8000"
    
    # URLs para probar
    urls_to_test = [
        "/dashboard/insumos-compuestos/",
        "/dashboard/api/insumos/basicos/",
        "/dashboard/api/categorias/",
        "/dashboard/api/unidades-medida/",
    ]
    
    print("🧪 Probando URLs de insumos compuestos...")
    
    for url in urls_to_test:
        try:
            print(f"\n🔍 Probando: {url}")
            response = requests.get(f"{base_url}{url}")
            
            if response.status_code == 200:
                print(f"  ✅ OK - Status: {response.status_code}")
                
                # Si es una API JSON, verificar el contenido
                if url.startswith("/dashboard/api/"):
                    try:
                        data = response.json()
                        if data.get('success'):
                            print(f"  ✅ JSON válido - success: {data['success']}")
                        else:
                            print(f"  ⚠️  JSON - success: {data.get('success', 'no especificado')}")
                    except Exception as e:
                        print(f"  ❌ Error al parsear JSON: {e}")
                
            else:
                print(f"  ❌ Error - Status: {response.status_code}")
                print(f"     Content: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Error de conexión - ¿Está corriendo el servidor?")
            return False
        except Exception as e:
            print(f"  ❌ Error inesperado: {e}")
            return False
    
    print(f"\n✅ Pruebas completadas")
    return True

if __name__ == "__main__":
    success = test_insumos_compuestos_urls()
    sys.exit(0 if success else 1)
