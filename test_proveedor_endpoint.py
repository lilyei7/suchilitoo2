#!/usr/bin/env python3
"""
Script para probar el endpoint de detalle de proveedor
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

import requests
from dashboard.models import Proveedor

def test_proveedor_detalle():
    print("🧪 Probando endpoint de detalle de proveedor...")
    
    # Obtener el primer proveedor
    proveedor = Proveedor.objects.first()
    if not proveedor:
        print("❌ No hay proveedores en la base de datos")
        return
    
    print(f"📋 Probando con proveedor: {proveedor.nombre_comercial} (ID: {proveedor.id})")
    
    # URL del endpoint
    url = f'http://127.0.0.1:8000/dashboard/proveedor/{proveedor.id}/detalle/'
    
    # Headers para simular solicitud AJAX
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Test Script)'
    }
    
    try:
        print(f"🔗 Haciendo solicitud a: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📨 Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
        
        if response.status_code == 200:
            print("✅ Respuesta exitosa!")
            
            # Verificar si es JSON
            if 'application/json' in response.headers.get('Content-Type', ''):
                try:
                    data = response.json()
                    print(f"🎯 JSON válido recibido")
                    print(f"  - success: {data.get('success', 'No especificado')}")
                    print(f"  - proveedor presente: {'proveedor' in data}")
                    print(f"  - html presente: {'html' in data}")
                    print(f"  - insumos presente: {'insumos' in data}")
                    
                    if data.get('success') and 'html' in data:
                        html_length = len(data['html']) if data['html'] else 0
                        print(f"  - HTML length: {html_length} caracteres")
                        print("🎉 El endpoint está funcionando correctamente!")
                    else:
                        print("⚠️ El JSON no contiene los campos esperados")
                        print(f"Contenido: {data}")
                        
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
    test_proveedor_detalle()
