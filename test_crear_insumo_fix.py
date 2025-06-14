#!/usr/bin/env python3
"""
Test para verificar que la creación de nuevos insumos funciona correctamente
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

def test_crear_insumo_functionality():
    """Test para verificar que la creación de insumos funciona"""
    
    print("=== TEST: VERIFICAR CREACION DE INSUMOS ===")
    
    try:
        # Obtener datos necesarios
        unidades = UnidadMedida.objects.all()
        categorias = CategoriaInsumo.objects.all()
        
        if not unidades.exists() or not categorias.exists():
            print("❌ No hay unidades o categorías para la prueba")
            return False
        
        unidad_test = unidades.first()
        categoria_test = categorias.first()
        
        print(f"✅ Datos para prueba:")
        print(f"   - Unidad: {unidad_test.nombre} (ID: {unidad_test.id})")
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
        
        # Verificar que la página de inventario carga correctamente
        response = client.get('/dashboard/inventario/')
        if response.status_code != 200:
            print(f"❌ Error al cargar página de inventario. Status: {response.status_code}")
            return False
        
        html_content = response.content.decode('utf-8')
        print("✅ Página de inventario cargada")
        
        # Verificar que el JavaScript para crear insumos está presente
        if 'function crearNuevoInsumo()' in html_content:
            print("✅ Función crearNuevoInsumo presente en el JavaScript")
        else:
            print("❌ Función crearNuevoInsumo no encontrada")
            return False
        
        # Verificar que el event listener está presente
        if "nuevoInsumoForm.addEventListener('submit'" in html_content:
            print("✅ Event listener para el formulario presente")
        else:
            print("❌ Event listener para el formulario no encontrado")
            return False
        
        # Test 1: Crear un nuevo insumo
        print("\n🆕 PROBANDO CREACION DE INSUMO:")
        
        import time
        codigo_unico = f'TEST-{int(time.time())}'
        
        nuevo_insumo_data = {
            'codigo': codigo_unico,
            'nombre': 'Insumo Test Creación',
            'tipo': 'basico',
            'categoria': categoria_test.id,
            'unidad_medida': unidad_test.id,
            'precio_unitario': 12.50,
            'stock_actual': 50,
            'stock_minimo': 5
        }
        
        # Contar insumos antes de crear
        insumos_antes = Insumo.objects.count()
        print(f"   - Insumos antes: {insumos_antes}")
        
        create_response = client.post('/dashboard/insumos/crear/', nuevo_insumo_data)
        
        if create_response.status_code == 200:
            try:
                create_result = create_response.json()
                if create_result.get('success'):
                    insumo_id = create_result.get('insumo_id')
                    print(f"✅ Insumo creado exitosamente (ID: {insumo_id})")
                    
                    # Verificar que se agregó a la base de datos
                    insumos_despues = Insumo.objects.count()
                    print(f"   - Insumos después: {insumos_despues}")
                    
                    if insumos_despues == insumos_antes + 1:
                        print("✅ Insumo agregado correctamente a la base de datos")
                    else:
                        print("❌ El conteo de insumos no coincide")
                        return False
                    
                    # Verificar los datos del insumo creado
                    insumo_creado = Insumo.objects.get(id=insumo_id)
                    
                    verificaciones = [
                        (insumo_creado.codigo == codigo_unico, f"Código: {insumo_creado.codigo}"),
                        (insumo_creado.nombre == nuevo_insumo_data['nombre'], f"Nombre: {insumo_creado.nombre}"),
                        (insumo_creado.categoria_id == categoria_test.id, f"Categoría ID: {insumo_creado.categoria_id}"),
                        (insumo_creado.unidad_medida_id == unidad_test.id, f"Unidad ID: {insumo_creado.unidad_medida_id}"),
                        (float(insumo_creado.precio_unitario) == nuevo_insumo_data['precio_unitario'], f"Precio: {insumo_creado.precio_unitario}"),
                        (float(insumo_creado.stock_minimo) == nuevo_insumo_data['stock_minimo'], f"Stock mínimo: {insumo_creado.stock_minimo}")
                    ]
                    
                    todas_correctas = True
                    for verificacion, descripcion in verificaciones:
                        if verificacion:
                            print(f"   ✅ {descripcion}")
                        else:
                            print(f"   ❌ {descripcion}")
                            todas_correctas = False
                    
                    if todas_correctas:
                        print("✅ Todos los datos del insumo son correctos")
                        return True
                    else:
                        print("❌ Algunos datos del insumo son incorrectos")
                        return False
                        
                else:
                    print(f"❌ Error al crear insumo: {create_result.get('error')}")
                    return False
            except ValueError:
                print("❌ Respuesta de creación no es JSON válido")
                print(f"Contenido de respuesta: {create_response.content[:200]}...")
                return False
        else:
            print(f"❌ Error HTTP al crear insumo. Status: {create_response.status_code}")
            print(f"Contenido de respuesta: {create_response.content[:200]}...")
            return False
        
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_crear_insumo_functionality()
    if success:
        print("\n🎉 TEST EXITOSO: La creación de insumos funciona correctamente")
        print("✅ Formulario de nuevo insumo operativo")
        print("✅ JavaScript funcionando")
        print("✅ Datos guardados correctamente en BD")
    else:
        print("\n❌ TEST FALLIDO: Hay problemas con la creación de insumos")
    
    sys.exit(0 if success else 1)
