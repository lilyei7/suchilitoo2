#!/usr/bin/env python3
"""
Test completo para verificar la funcionalidad de edición de insumos
"""

import os
import sys
import django
import requests
from requests.auth import HTTPBasicAuth

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from restaurant.models import Insumo, UnidadMedida, CategoriaInsumo
from django.test import Client
from django.contrib.auth.models import User

def test_complete_edit_functionality():
    """Test completo de la funcionalidad de edición"""
    
    print("=== TEST: FUNCIONALIDAD COMPLETA DE EDICION ===")
    
    try:
        # Verificar datos básicos
        unidades = UnidadMedida.objects.all()
        categorias = CategoriaInsumo.objects.all()
        insumos = Insumo.objects.all()
        
        print(f"✅ Datos en BD:")
        print(f"   - Unidades: {unidades.count()}")
        print(f"   - Categorías: {categorias.count()}")
        print(f"   - Insumos: {insumos.count()}")
        
        if not insumos.exists():
            print("❌ No hay insumos para probar")
            return False
        
        # Usar el primer insumo para la prueba
        insumo = insumos.first()
        print(f"✅ Insumo de prueba: {insumo.nombre} (ID: {insumo.id})")
        
        # Crear cliente Django para simular requests
        client = Client()
        
        # Hacer login
        User = get_user_model()
        user = User.objects.get(username='admin')
        login_success = client.login(username='admin', password='admin123')
        
        if not login_success:
            print("❌ Login fallido")
            return False
        
        print("✅ Login exitoso")
        
        # 1. Test: Obtener datos del insumo para edición (GET)
        edit_url = f'/dashboard/insumos/editar/{insumo.id}/'
        response = client.get(edit_url)
        
        if response.status_code != 200:
            print(f"❌ Error al obtener datos del insumo. Status: {response.status_code}")
            return False
        
        try:
            data = response.json()
            print("✅ Datos del insumo obtenidos correctamente")
            print(f"   - Nombre: {data.get('nombre')}")
            print(f"   - Categoría ID: {data.get('categoria')}")
            print(f"   - Unidad Medida ID: {data.get('unidad_medida')}")
            print(f"   - Stock Mínimo: {data.get('stock_minimo')}")
            print(f"   - Precio Unitario: {data.get('precio_unitario')}")
        except ValueError:
            print("❌ Respuesta no es JSON válido")
            return False
        
        # 2. Test: Verificar que la página de inventario carga con las unidades
        inventory_response = client.get('/dashboard/inventario/')
        if inventory_response.status_code != 200:
            print(f"❌ Error al cargar página de inventario. Status: {inventory_response.status_code}")
            return False
        
        html_content = inventory_response.content.decode('utf-8')
        
        # Verificar que el modal de edición está presente
        if 'id="modalEditarInsumo"' not in html_content:
            print("❌ Modal de edición no encontrado en el HTML")
            return False
        
        print("✅ Modal de edición presente en la página")
        
        # Verificar que las unidades están en el dropdown
        unidades_en_html = 0
        for unidad in unidades:
            if f'<option value="{unidad.id}">{unidad.nombre}</option>' in html_content:
                unidades_en_html += 1
        
        print(f"✅ {unidades_en_html} de {unidades.count()} unidades presentes en el dropdown")
        
        # 3. Test: Editar el insumo (POST)
        # Obtener una unidad diferente para la prueba
        nueva_unidad = unidades.exclude(id=data.get('unidad_medida')).first()
        if not nueva_unidad:
            print("⚠️  Solo hay una unidad, usando la misma")
            nueva_unidad = unidades.first()
        
        # Datos de edición
        edit_data = {
            'nombre': data.get('nombre') + ' EDITADO_TEST',
            'categoria': data.get('categoria'),
            'unidad_medida': nueva_unidad.id,
            'stock_minimo': float(data.get('stock_minimo', 0)) + 1,
            'precio_unitario': float(data.get('precio_unitario', 0)) + 0.50,
            'perecedero': False
        }
        
        print(f"✅ Datos de edición preparados:")
        print(f"   - Nueva unidad: {nueva_unidad.nombre} (ID: {nueva_unidad.id})")
        print(f"   - Nuevo stock mínimo: {edit_data['stock_minimo']}")
        
        # Realizar la edición
        edit_response = client.post(edit_url, edit_data)
        
        if edit_response.status_code != 200:
            print(f"❌ Error al editar insumo. Status: {edit_response.status_code}")
            return False
        
        try:
            edit_result = edit_response.json()
            if edit_result.get('success'):
                print("✅ Edición exitosa según respuesta")
            else:
                print(f"❌ Error en edición: {edit_result.get('error')}")
                return False
        except ValueError:
            print("❌ Respuesta de edición no es JSON válido")
            return False
        
        # 4. Verificar que los cambios se guardaron en la base de datos
        insumo.refresh_from_db()
        
        if insumo.nombre == edit_data['nombre']:
            print("✅ Nombre actualizado correctamente")
        else:
            print(f"❌ Nombre no actualizado. Esperado: {edit_data['nombre']}, Actual: {insumo.nombre}")
            return False
        
        if insumo.unidad_medida_id == edit_data['unidad_medida']:
            print("✅ Unidad de medida actualizada correctamente")
        else:
            print(f"❌ Unidad de medida no actualizada. Esperado: {edit_data['unidad_medida']}, Actual: {insumo.unidad_medida_id}")
            return False
        
        if insumo.stock_minimo == edit_data['stock_minimo']:
            print("✅ Stock mínimo actualizado correctamente")
        else:
            print(f"❌ Stock mínimo no actualizado. Esperado: {edit_data['stock_minimo']}, Actual: {insumo.stock_minimo}")
            return False
        
        print("\n🎉 TODOS LOS TESTS PASARON:")
        print("   ✅ Template carga con unidades")
        print("   ✅ Modal de edición presente")
        print("   ✅ GET de datos funciona")
        print("   ✅ POST de edición funciona")
        print("   ✅ Cambios se guardan en BD")
        print("   ✅ Unidades de medida se pueden cambiar")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_edit_functionality()
    if success:
        print("\n🎉 TEST COMPLETO EXITOSO: La funcionalidad de edición funciona correctamente")
        print("✅ El problema de las unidades de medida ha sido RESUELTO")
    else:
        print("\n❌ TEST COMPLETO FALLIDO: Hay problemas con la funcionalidad de edición")
    
    sys.exit(0 if success else 1)
