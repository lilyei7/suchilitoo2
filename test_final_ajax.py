#!/usr/bin/env python3
"""
Script para hacer una prueba final rápida del sistema de asignación de insumos
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from restaurant.models import Insumo
from dashboard.models import Proveedor, ProveedorInsumo
import json

User = get_user_model()

def test_ajax_assignment():
    print("🔍 PRUEBA FINAL - ASIGNACIÓN AJAX")
    print("="*50)
    
    # Datos de prueba
    insumo = Insumo.objects.first()
    proveedor = Proveedor.objects.first()
    
    if not insumo or not proveedor:
        print("❌ No hay datos disponibles")
        return False
    
    print(f"📋 Probando con:")
    print(f"   Insumo: {insumo.nombre}")
    print(f"   Proveedor: {proveedor.nombre_comercial}")
    
    # Crear cliente autenticado
    user, _ = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@test.com'}
    )
    
    client = Client()
    client.force_login(user)
    
    # Limpiar relación existente
    ProveedorInsumo.objects.filter(proveedor=proveedor, insumo=insumo).delete()
    
    # Datos para la asignación
    data = {
        'insumo_id': str(insumo.id),
        'precio_unitario': '35.99',
        'cantidad_minima': '2',
        'tiempo_entrega_dias': '3',
        'observaciones': 'Prueba AJAX automatizada'
    }
    
    print(f"📤 Enviando asignación vía AJAX...")
    
    try:
        # Simular petición AJAX
        response = client.post(
            f'/dashboard/proveedor/{proveedor.id}/asignar-insumo/', 
            data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # Simular AJAX
        )
        
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = json.loads(response.content.decode('utf-8'))
            print(f"📥 Respuesta JSON: {response_data}")
            
            if response_data.get('success'):
                print("✅ ¡ÉXITO! Asignación AJAX funciona correctamente")
                
                # Verificar que se creó en BD
                relacion = ProveedorInsumo.objects.filter(
                    proveedor=proveedor, 
                    insumo=insumo
                ).first()
                
                if relacion:
                    print(f"✅ Verificado en BD: Precio ${relacion.precio_unitario}")
                    return True
                else:
                    print("❌ No se encontró en BD")
                    return False
            else:
                print(f"❌ Error en lógica: {response_data.get('message')}")
                return False
        else:
            print(f"❌ Status incorrecto: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

def test_detail_endpoint():
    print("\n🔍 PRUEBA - ENDPOINT DE DETALLES")
    print("="*50)
    
    proveedor = Proveedor.objects.first()
    if not proveedor:
        print("❌ No hay proveedores")
        return False
    
    client = Client()
    user, _ = User.objects.get_or_create(username='test_user')
    client.force_login(user)
    
    try:
        response = client.get(f'/dashboard/proveedor/{proveedor.id}/detalle/')
        
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content.decode('utf-8'))
            print(f"📥 Proveedor: {data.get('proveedor', {}).get('nombre_comercial')}")
            print(f"📥 Insumos: {len(data.get('insumos', []))}")
            print("✅ Endpoint de detalles funciona")
            return True
        else:
            print(f"❌ Status incorrecto: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

def main():
    print("🚀 PRUEBAS FINALES DEL SISTEMA DE ASIGNACIÓN")
    print("="*60)
    
    success1 = test_ajax_assignment()
    success2 = test_detail_endpoint()
    
    print(f"\n🎯 RESULTADOS FINALES:")
    print(f"   Asignación AJAX: {'✅ OK' if success1 else '❌ FAIL'}")
    print(f"   Detalles del proveedor: {'✅ OK' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print(f"\n🎉 ¡TODO LISTO! El sistema funciona perfectamente.")
        print(f"   Ahora puedes probar desde el navegador:")
        print(f"   1. Ve a http://localhost:8000/dashboard/")
        print(f"   2. Navega a Proveedores")
        print(f"   3. Haz clic en 'Ver Detalles' de cualquier proveedor")
        print(f"   4. Haz clic en 'Asignar Insumo'")
        print(f"   5. La página se actualizará automáticamente sin redireccionar")
    else:
        print(f"\n❌ Hay problemas que revisar")

if __name__ == '__main__':
    main()
