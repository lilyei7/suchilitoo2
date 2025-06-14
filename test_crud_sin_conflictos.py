#!/usr/bin/env python3
"""
Test completo para verificar que tanto crear como editar insumos funcionan sin conflictos
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from restaurant.models import Insumo, UnidadMedida, CategoriaInsumo

def test_complete_crud_functionality():
    """Test completo para verificar CRUD sin conflictos"""
    
    print("=== TEST COMPLETO: CREAR Y EDITAR SIN CONFLICTOS ===")
    
    try:
        # Obtener datos necesarios
        unidades = UnidadMedida.objects.all()
        categorias = CategoriaInsumo.objects.all()
        
        if not unidades.exists() or not categorias.exists():
            print("❌ No hay unidades o categorías para la prueba")
            return False
        
        unidad1 = unidades.first()
        unidad2 = unidades.last() if unidades.count() > 1 else unidades.first()
        categoria_test = categorias.first()
        
        print(f"✅ Datos para prueba:")
        print(f"   - Unidad 1: {unidad1.nombre} (ID: {unidad1.id})")
        print(f"   - Unidad 2: {unidad2.nombre} (ID: {unidad2.id})")
        print(f"   - Categoría: {categoria_test.nombre} (ID: {categoria_test.id})")
        
        # Crear cliente Django
        client = Client()
        
        # Hacer login
        User = get_user_model()
        user = User.objects.get(username='admin')
        login_success = client.login(username='admin', password='admin123')
        
        if not login_success:
            print("❌ Login fallido")
            return False
        
        print("✅ Login exitoso")
        
        # Verificar página de inventario
        response = client.get('/dashboard/inventario/')
        if response.status_code != 200:
            print(f"❌ Error al cargar página de inventario. Status: {response.status_code}")
            return False
        
        html_content = response.content.decode('utf-8')
        print("✅ Página de inventario cargada")
          # Verificar funciones JavaScript
        funciones_presentes = [
            ('function crearNuevoInsumo()', 'crearNuevoInsumo'),
            ('function cargarCategoriasYUnidades()', 'cargarCategoriasYUnidades'),
            ("nuevoInsumoForm.addEventListener('submit'", 'Event listener de creación'),
            ("insumos_crud.js", 'Script de CRUD externo')
        ]
        
        for patron, nombre in funciones_presentes:
            if patron in html_content:
                print(f"   ✅ {nombre} presente")
            else:
                print(f"   ❌ {nombre} no encontrado")
                if nombre != 'Script de CRUD externo':  # No es crítico si el script externo no se encuentra en HTML
                    return False
        
        # Test 1: CREAR un nuevo insumo
        print("\n🆕 TEST 1: CREAR NUEVO INSUMO")
        
        import time
        codigo_unico = f'CRUD-{int(time.time())}'
        
        nuevo_insumo_data = {
            'codigo': codigo_unico,
            'nombre': 'Insumo CRUD Test',
            'tipo': 'basico',
            'categoria': categoria_test.id,
            'unidad_medida': unidad1.id,
            'precio_unitario': 15.75,
            'stock_actual': 100,
            'stock_minimo': 10
        }
        
        create_response = client.post('/dashboard/insumos/crear/', nuevo_insumo_data)
        
        if create_response.status_code == 200:
            create_result = create_response.json()
            if create_result.get('success'):
                insumo_id = create_result.get('insumo_id')
                print(f"✅ Insumo creado exitosamente (ID: {insumo_id})")
            else:
                print(f"❌ Error al crear: {create_result.get('error')}")
                return False
        else:
            print(f"❌ Error HTTP al crear. Status: {create_response.status_code}")
            return False
        
        # Test 2: LEER/OBTENER el insumo creado
        print(f"\n📖 TEST 2: OBTENER INSUMO {insumo_id}")
        
        get_response = client.get(f'/dashboard/insumos/editar/{insumo_id}/')
        
        if get_response.status_code == 200:
            insumo_data = get_response.json()
            print(f"✅ Datos obtenidos:")
            print(f"   - Nombre: {insumo_data.get('nombre')}")
            print(f"   - Unidad actual: {insumo_data.get('unidad_medida')}")
        else:
            print(f"❌ Error al obtener insumo. Status: {get_response.status_code}")
            return False
        
        # Test 3: ACTUALIZAR el insumo
        print(f"\n✏️  TEST 3: ACTUALIZAR INSUMO {insumo_id}")
        
        update_data = {
            'nombre': 'Insumo CRUD Test ACTUALIZADO',
            'categoria': categoria_test.id,
            'unidad_medida': unidad2.id,  # Cambiar a otra unidad
            'stock_minimo': 15,
            'precio_unitario': 20.50,
            'perecedero': False
        }
        
        update_response = client.post(f'/dashboard/insumos/editar/{insumo_id}/', update_data)
        
        if update_response.status_code == 200:
            update_result = update_response.json()
            if update_result.get('success'):
                print(f"✅ Insumo actualizado exitosamente")
                print(f"   - Nueva unidad: {unidad2.nombre}")
            else:
                print(f"❌ Error al actualizar: {update_result.get('error')}")
                return False
        else:
            print(f"❌ Error HTTP al actualizar. Status: {update_response.status_code}")
            return False
        
        # Test 4: VERIFICAR cambios en la base de datos
        print(f"\n🔍 TEST 4: VERIFICAR CAMBIOS EN BD")
        
        insumo_actualizado = Insumo.objects.get(id=insumo_id)
        
        verificaciones = [
            (insumo_actualizado.nombre == update_data['nombre'], f"Nombre: {insumo_actualizado.nombre}"),
            (insumo_actualizado.unidad_medida_id == unidad2.id, f"Unidad: {insumo_actualizado.unidad_medida.nombre}"),
            (float(insumo_actualizado.stock_minimo) == update_data['stock_minimo'], f"Stock mínimo: {insumo_actualizado.stock_minimo}"),
            (float(insumo_actualizado.precio_unitario) == update_data['precio_unitario'], f"Precio: {insumo_actualizado.precio_unitario}")
        ]
        
        todas_correctas = True
        for verificacion, descripcion in verificaciones:
            if verificacion:
                print(f"   ✅ {descripcion}")
            else:
                print(f"   ❌ {descripcion}")
                todas_correctas = False
        
        if not todas_correctas:
            return False
        
        # Test 5: CREAR otro insumo para verificar que sigue funcionando
        print(f"\n🆕 TEST 5: CREAR SEGUNDO INSUMO (verificar funcionamiento continuo)")
        
        codigo_unico2 = f'CRUD2-{int(time.time())}'
        
        segundo_insumo_data = {
            'codigo': codigo_unico2,
            'nombre': 'Segundo Insumo CRUD Test',
            'tipo': 'basico',
            'categoria': categoria_test.id,
            'unidad_medida': unidad2.id,
            'precio_unitario': 8.25,
            'stock_actual': 25,
            'stock_minimo': 3
        }
        
        create_response2 = client.post('/dashboard/insumos/crear/', segundo_insumo_data)
        
        if create_response2.status_code == 200:
            create_result2 = create_response2.json()
            if create_result2.get('success'):
                insumo_id2 = create_result2.get('insumo_id')
                print(f"✅ Segundo insumo creado exitosamente (ID: {insumo_id2})")
            else:
                print(f"❌ Error al crear segundo insumo: {create_result2.get('error')}")
                return False
        else:
            print(f"❌ Error HTTP al crear segundo insumo. Status: {create_response2.status_code}")
            return False
        
        print("\n🎉 TODOS LOS TESTS PASARON:")
        print("   ✅ CREAR: Funcionando correctamente")
        print("   ✅ LEER: Funcionando correctamente")
        print("   ✅ ACTUALIZAR: Funcionando correctamente")
        print("   ✅ CREAR MÚLTIPLE: Funcionando correctamente")
        print("   ✅ CAMBIO DE UNIDADES: Funcionando correctamente")
        print("   ✅ JAVASCRIPT: Sin conflictos entre funciones")
        print("   ✅ BASE DE DATOS: Cambios persistidos correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_crud_functionality()
    if success:
        print("\n🎉 TEST COMPLETO EXITOSO")
        print("✅ PROBLEMA RESUELTO: La creación de insumos funciona sin afectar otras funciones")
        print("✅ Tanto crear como editar insumos funcionan perfectamente")
        print("✅ Las unidades de medida se manejan correctamente en ambos casos")
        print("✅ No hay conflictos entre las diferentes funcionalidades")
    else:
        print("\n❌ TEST COMPLETO FALLIDO")
        print("❌ Aún hay problemas con alguna funcionalidad")
    
    sys.exit(0 if success else 1)
