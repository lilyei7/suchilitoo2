#!/usr/bin/env python3
"""
Script para probar el endpoint de form-data y verificar que funciona correctamente
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

import requests

def test_form_data_endpoint():
    print("🧪 Probando endpoint de form-data...")
    
    url = 'http://127.0.0.1:8000/dashboard/api/form-data/'
    
    try:
        print(f"🔗 Haciendo solicitud a: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📨 Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
        
        if response.status_code == 200:
            print("✅ Respuesta exitosa!")
            
            # Verificar si es JSON
            if 'application/json' in response.headers.get('Content-Type', ''):
                try:
                    data = response.json()
                    print(f"🎯 JSON válido recibido")
                    print(f"  - categorias presente: {'categorias' in data}")
                    print(f"  - unidades presente: {'unidades' in data}")
                    
                    if 'categorias' in data:
                        print(f"  - Total categorías: {len(data['categorias'])}")
                        if data['categorias']:
                            print(f"  - Primera categoría: {data['categorias'][0]}")
                    
                    if 'unidades' in data:
                        print(f"  - Total unidades: {len(data['unidades'])}")
                        if data['unidades']:
                            print(f"  - Primera unidad: {data['unidades'][0]}")
                    
                    print("🎉 El endpoint de form-data está funcionando correctamente!")
                        
                except ValueError as e:
                    print(f"❌ Error parseando JSON: {e}")
                    print(f"Contenido recibido: {response.text[:500]}...")
            else:
                print("❌ La respuesta no es JSON")
                print(f"Contenido recibido: {response.text[:500]}...")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Contenido: {response.text[:500]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está el servidor Django ejecutándose?")
    except requests.exceptions.Timeout:
        print("❌ Timeout en la solicitud")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == '__main__':
    test_form_data_endpoint()
