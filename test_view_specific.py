#!/usr/bin/env python3
"""
Script para probar específicamente la vista de asignar_insumo_proveedor
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from restaurant.models import Insumo, CategoriaInsumo, UnidadMedida
from dashboard.models import Proveedor, ProveedorInsumo
import json

User = get_user_model()

def test_view_simple():
    """Prueba simple de la vista"""
    print("🔍 PRUEBA SIMPLE DE LA VISTA asignar_insumo_proveedor")
    print("="*60)
    
    # Obtener datos existentes
    insumo = Insumo.objects.filter(nombre__icontains="TEST").first()
    proveedor = Proveedor.objects.filter(nombre_comercial__icontains="TEST").first()
    
    if not insumo or not proveedor:
        print("❌ No se encontraron datos de prueba")
        return False
    
    print(f"📋 Usando:")
    print(f"   Insumo: {insumo.id} - {insumo.nombre}")
    print(f"   Proveedor: {proveedor.id} - {proveedor.nombre_comercial}")
    
    # Crear cliente de prueba
    client = Client()
    
    # Preparar datos
    data = {        'insumo_id': str(insumo.id),
        'precio_unitario': '25.50',
        'cantidad_minima': '1',
        'tiempo_entrega_dias': '2',
        'observaciones': 'Prueba con Client de Django'
    }
    
    print(f"📤 Enviando POST a /dashboard/proveedor/{proveedor.id}/asignar-insumo/")
    print(f"   Datos: {data}")
    
    # Limpiar relaciones existentes
    ProveedorInsumo.objects.filter(proveedor=proveedor, insumo=insumo).delete()
    
    try:
        response = client.post(f'/dashboard/proveedor/{proveedor.id}/asignar-insumo/', data)
        
        print(f"\n📥 Respuesta:")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.get('Content-Type', 'Sin especificar')}")
        print(f"   Content (raw): {response.content}")
        
        if response.status_code == 200:
            try:
                response_data = json.loads(response.content.decode('utf-8'))
                print(f"   JSON válido: {response_data}")
                return response_data.get('success', False)
            except json.JSONDecodeError as e:
                print(f"   ❌ No es JSON válido: {e}")
                print(f"   Content decoded: {response.content.decode('utf-8')}")
                return False
        else:
            print(f"   ❌ Status code no es 200")
            return False
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_view_with_auth():
    """Prueba con autenticación"""
    print("\n🔍 PRUEBA CON AUTENTICACIÓN")
    print("="*60)
    
    # Crear un usuario de prueba
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    print(f"📋 Usuario: {user.username}")
    
    # Obtener datos existentes
    insumo = Insumo.objects.filter(nombre__icontains="TEST").first()
    proveedor = Proveedor.objects.filter(nombre_comercial__icontains="TEST").first()
    
    if not insumo or not proveedor:
        print("❌ No se encontraron datos de prueba")
        return False
    
    # Crear cliente y hacer login
    client = Client()
    client.force_login(user)
    
    # Preparar datos
    data = {
        'insumo_id': str(insumo.id),
        'precio_unitario': '30.00',
        'cantidad_minima': '2',
        'tiempo_entrega_dias': '3',
        'observaciones': 'Prueba con autenticación'
    }
      print(f"📤 Enviando POST autenticado a /dashboard/proveedor/{proveedor.id}/asignar-insumo/")
    
    # Limpiar relaciones existentes
    ProveedorInsumo.objects.filter(proveedor=proveedor, insumo=insumo).delete()
    
    try:
        response = client.post(f'/dashboard/proveedor/{proveedor.id}/asignar-insumo/', data)
        
        print(f"\n📥 Respuesta autenticada:")
        print(f"   Status: {response.status_code}")
        print(f"   Content: {response.content.decode('utf-8')}")
        
        if response.status_code == 200:
            try:
                response_data = json.loads(response.content.decode('utf-8'))
                print(f"   ✅ JSON válido: {response_data}")
                return response_data.get('success', False)
            except json.JSONDecodeError as e:
                print(f"   ❌ No es JSON válido: {e}")
                return False
        else:
            print(f"   ❌ Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la prueba con auth: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    try:
        # Probar sin autenticación
        success1 = test_view_simple()
        
        # Probar con autenticación
        success2 = test_view_with_auth()
        
        print(f"\n🎯 RESULTADOS:")
        print(f"   Sin autenticación: {'✅ OK' if success1 else '❌ FAIL'}")
        print(f"   Con autenticación: {'✅ OK' if success2 else '❌ FAIL'}")
        
        if success1 or success2:
            print(f"\n🎉 Al menos una prueba funcionó - el problema de FK está resuelto!")
        else:
            print(f"\n❌ Ambas pruebas fallaron - revisar la vista")
            
    except Exception as e:
        print(f"💥 ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
