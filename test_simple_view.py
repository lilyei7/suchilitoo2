#!/usr/bin/env python3
"""
Script simplificado para probar la vista de asignar_insumo_proveedor
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

def main():
    print("🔍 PRUEBA SIMPLIFICADA DE asignar_insumo_proveedor")
    print("="*60)
    
    # Obtener datos existentes
    insumo = Insumo.objects.filter(nombre__icontains="TEST").first()
    proveedor = Proveedor.objects.filter(nombre_comercial__icontains="TEST").first()
    
    if not insumo:
        insumo = Insumo.objects.first()
    if not proveedor:
        proveedor = Proveedor.objects.first()
    
    if not insumo or not proveedor:
        print("❌ No hay datos disponibles")
        return
    
    print(f"📋 Usando:")
    print(f"   Insumo: {insumo.id} - {insumo.nombre}")
    print(f"   Proveedor: {proveedor.id} - {proveedor.nombre_comercial}")
    
    # Crear usuario y cliente
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@test.com', 'first_name': 'Test'}
    )
    
    client = Client()
    client.force_login(user)
    
    # Datos de prueba
    data = {
        'insumo_id': str(insumo.id),
        'precio_unitario': '25.50',
        'cantidad_minima': '1',
        'tiempo_entrega_dias': '2',
        'observaciones': 'Prueba simplificada'
    }
    
    # Limpiar relaciones existentes
    ProveedorInsumo.objects.filter(proveedor=proveedor, insumo=insumo).delete()
    
    print(f"📤 POST a /dashboard/proveedor/{proveedor.id}/asignar-insumo/")
    
    try:
        response = client.post(f'/dashboard/proveedor/{proveedor.id}/asignar-insumo/', data)
        
        print(f"📥 Status: {response.status_code}")
        content = response.content.decode('utf-8')
        print(f"📥 Content: {content}")
        
        if response.status_code == 200:
            try:
                response_data = json.loads(content)
                print(f"✅ JSON válido: {response_data}")
                if response_data.get('success'):
                    print("🎉 ¡ÉXITO! La asignación funcionó correctamente")
                else:
                    print(f"❌ Error en la lógica: {response_data.get('message')}")
            except json.JSONDecodeError:
                print("❌ Respuesta no es JSON válido")
        else:
            print(f"❌ Status code incorrecto: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
