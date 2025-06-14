#!/usr/bin/env python3
"""
Script para probar el endpoint de insumos disponibles para proveedores
"""
import os
import django
import requests

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from dashboard.models import Proveedor

def test_insumos_disponibles():
    print("🧪 Probando endpoint de insumos disponibles...")
    
    # Obtener el primer proveedor
    proveedor = Proveedor.objects.first()
    if not proveedor:
        print("❌ No hay proveedores en la base de datos")
        return
    
    print(f"📋 Probando con proveedor: {proveedor.nombre_comercial} (ID: {proveedor.id})")
    
    # URL del endpoint
    url = f'http://127.0.0.1:8000/dashboard/api/insumos-disponibles/?proveedor_id={proveedor.id}'
    
    # Headers para simular solicitud AJAX
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json',
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
                    print(f"  - insumos presente: {'insumos' in data}")
                    
                    if data.get('success') and 'insumos' in data:
                        insumos = data.get('insumos', [])
                        print(f"  - Total insumos disponibles: {len(insumos)}")
                        
                        if insumos:
                            print("  - Primeros 3 insumos:")
                            for i, insumo in enumerate(insumos[:3], 1):
                                print(f"    {i}. {insumo.get('nombre')} ({insumo.get('categoria')})")
                        else:
                            print("  - No hay insumos disponibles para este proveedor")
                        
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
    test_insumos_disponibles()
