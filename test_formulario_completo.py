#!/usr/bin/env python
import os
import sys
import django
import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from restaurant.models import Insumo

def test_formulario_completo():
    print("=== PRUEBA COMPLETA DEL FORMULARIO ===")
    
    # Crear cliente de prueba
    client = Client()
    
    # 1. Login
    print("1. Realizando login...")
    login_response = client.post('/dashboard/login/', {
        'username': 'jhayco',
        'password': 'admin123'
    })
    
    if login_response.status_code != 302:
        print(f"❌ Error en login: {login_response.status_code}")
        return False
    
    print("✅ Login exitoso")
    
    # 2. Cargar página de inventario
    print("2. Cargando página de inventario...")
    inventario_response = client.get('/dashboard/inventario/')
    
    if inventario_response.status_code != 200:
        print(f"❌ Error al cargar inventario: {inventario_response.status_code}")
        return False
    
    print("✅ Página de inventario cargada")
    
    # 3. Obtener datos del formulario
    print("3. Obteniendo datos del formulario...")
    form_data_response = client.get('/dashboard/insumos/form-data/')
    
    if form_data_response.status_code != 200:
        print(f"❌ Error al obtener datos del formulario: {form_data_response.status_code}")
        return False
    
    print("✅ Datos del formulario obtenidos")
    
    # 4. Crear insumo
    print("4. Creando nuevo insumo...")
    
    # Contar insumos antes
    insumos_antes = Insumo.objects.count()
    print(f"Insumos antes: {insumos_antes}")
    
    # Datos del nuevo insumo
    nuevo_insumo_data = {
        'codigo': 'FORMULARIO001',
        'nombre': 'Insumo desde Formulario Test',
        'categoria': '1',
        'unidad_medida': '1',
        'tipo': 'basico',
        'precio_unitario': '30.50',
        'stock_actual': '100',
        'stock_minimo': '20'
    }
    
    crear_response = client.post('/dashboard/insumos/crear/', nuevo_insumo_data)
    
    if crear_response.status_code != 200:
        print(f"❌ Error al crear insumo: {crear_response.status_code}")
        print(f"Response content: {crear_response.content}")
        return False
    
    # Verificar respuesta JSON
    try:
        import json
        response_data = json.loads(crear_response.content)
        if response_data.get('success'):
            print(f"✅ Insumo creado: {response_data.get('message')}")
        else:
            print(f"❌ Error en respuesta: {response_data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error al parsear respuesta JSON: {e}")
        return False
    
    # 5. Verificar que el insumo se guardó
    print("5. Verificando que el insumo se guardó...")
    insumos_despues = Insumo.objects.count()
    print(f"Insumos después: {insumos_despues}")
    
    if insumos_despues <= insumos_antes:
        print("❌ El insumo no se guardó en la base de datos")
        return False
    
    # Buscar el insumo específico
    try:
        insumo_creado = Insumo.objects.get(codigo='FORMULARIO001')
        print(f"✅ Insumo encontrado: {insumo_creado.codigo} - {insumo_creado.nombre}")
    except Insumo.DoesNotExist:
        print("❌ No se encontró el insumo creado")
        return False
    
    print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! El formulario funciona correctamente.")
    return True

if __name__ == "__main__":
    success = test_formulario_completo()
    if not success:
        sys.exit(1)
