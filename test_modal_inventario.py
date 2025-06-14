#!/usr/bin/env python3
"""
Script para probar el modal de edición de inventario
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_restaurant.settings')
django.setup()

from django.test import Client
from django.contrib.auth import authenticate
from restaurant.models import Insumo, CategoriaInsumo, UnidadMedida
import json

def test_modal_inventario():
    print("=== PRUEBA DEL MODAL DE INVENTARIO ===")
    
    # Crear cliente de prueba
    client = Client()
    
    # Intentar hacer login (usaremos las credenciales del admin)
    login_successful = client.login(username='admin', password='admin123')
    if not login_successful:
        print("❌ No se pudo hacer login con admin/admin123")
        return
    
    print("✅ Login exitoso")
    
    # Obtener el primer insumo disponible
    try:
        insumo = Insumo.objects.first()
        if not insumo:
            print("❌ No hay insumos en la base de datos")
            return
        
        print(f"📦 Probando con insumo: {insumo.nombre} (ID: {insumo.id})")
        
        # Hacer petición GET al endpoint de edición (que devuelve los datos del insumo)
        response = client.get(f'/dashboard/insumos/editar/{insumo.id}/')
        
        print(f"📡 Status de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("📄 Datos JSON recibidos:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar que los campos necesarios estén presentes
            campos_requeridos = [
                'id', 'nombre', 'categoria', 'categoria_nombre', 
                'unidad_medida', 'unidad_medida_nombre', 'stock_minimo', 
                'precio_unitario'
            ]
            
            campos_faltantes = []
            for campo in campos_requeridos:
                if campo not in data:
                    campos_faltantes.append(campo)
            
            if campos_faltantes:
                print(f"❌ Campos faltantes: {campos_faltantes}")
            else:
                print("✅ Todos los campos requeridos están presentes")
                
                # Verificar específicamente los campos que estaban causando "undefined"
                if data.get('categoria_nombre'):
                    print(f"✅ Categoría nombre: {data['categoria_nombre']}")
                else:
                    print(f"❌ Categoría nombre está vacío o undefined")
                
                if data.get('unidad_medida_nombre'):
                    print(f"✅ Unidad medida nombre: {data['unidad_medida_nombre']}")
                else:
                    print(f"❌ Unidad medida nombre está vacío o undefined")
        else:
            print(f"❌ Error en la petición: {response.status_code}")
            print(f"Contenido: {response.content.decode()}")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

def check_data_integrity():
    print("\n=== VERIFICACIÓN DE INTEGRIDAD DE DATOS ===")
    
    # Verificar insumos sin categoría o unidad
    insumos_sin_categoria = Insumo.objects.filter(categoria__isnull=True)
    insumos_sin_unidad = Insumo.objects.filter(unidad_medida__isnull=True)
    
    print(f"📦 Total insumos: {Insumo.objects.count()}")
    print(f"🏷️ Total categorías: {CategoriaInsumo.objects.count()}")
    print(f"📏 Total unidades: {UnidadMedida.objects.count()}")
    
    if insumos_sin_categoria.exists():
        print(f"⚠️ Insumos sin categoría: {insumos_sin_categoria.count()}")
        for insumo in insumos_sin_categoria[:3]:
            print(f"  - {insumo.nombre} (ID: {insumo.id})")
    else:
        print("✅ Todos los insumos tienen categoría")
    
    if insumos_sin_unidad.exists():
        print(f"⚠️ Insumos sin unidad de medida: {insumos_sin_unidad.count()}")
        for insumo in insumos_sin_unidad[:3]:
            print(f"  - {insumo.nombre} (ID: {insumo.id})")
    else:
        print("✅ Todos los insumos tienen unidad de medida")

if __name__ == '__main__':
    check_data_integrity()
    test_modal_inventario()
    print("\n=== PRUEBA COMPLETADA ===")
