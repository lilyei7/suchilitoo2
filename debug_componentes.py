#!/usr/bin/env python3
"""
Script para debuggear el problema de validación de componentes
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Insumo, CategoriaInsumo, UnidadMedida
from accounts.models import Usuario
from django.test import Client
import json

def test_debug_componentes():
    """Test específico para debuggear el problema de componentes"""
    
    print("🔍 DEBUGGEANDO PROBLEMA DE VALIDACIÓN DE COMPONENTES")
    print("=" * 60)
    
    # Setup
    client = Client()
    admin_user = Usuario.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No hay usuario admin disponible")
        return
    
    client.force_login(admin_user)
    
    # Obtener datos necesarios
    categoria = CategoriaInsumo.objects.first()
    unidad = UnidadMedida.objects.first()
    insumos_basicos = Insumo.objects.filter(tipo='basico', activo=True)[:2]
    
    if not all([categoria, unidad, insumos_basicos.count() >= 2]):
        print("❌ No hay datos suficientes")
        return
    
    insumo1 = insumos_basicos[0]
    insumo2 = insumos_basicos[1]
    
    print(f"📋 DATOS DE PRUEBA:")
    print(f"   Categoría: {categoria.nombre} (ID: {categoria.id})")
    print(f"   Unidad: {unidad.nombre} (ID: {unidad.id})")
    print(f"   Insumo 1: {insumo1.nombre} (ID: {insumo1.id})")
    print(f"   Insumo 2: {insumo2.nombre} (ID: {insumo2.id})")
    
    # Test 1: Formato correcto con arrays
    print(f"\n🧪 TEST 1: Formato con arrays []")
    
    post_data_1 = {
        'nombre': 'Test Debug 1',
        'categoria_id': categoria.id,
        'unidad_medida_id': unidad.id,
        'cantidad_producida': '1.0',
        'descripcion': 'Test de debug',
        'componente_insumo[]': [insumo1.id, insumo2.id],
        'componente_cantidad[]': ['0.5', '0.3']
    }
    
    print(f"   Enviando: {post_data_1}")
    
    response = client.post('/dashboard/insumos-compuestos/crear/', 
                          post_data_1, 
                          HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Message: {data.get('message')}")
        if data.get('success'):
            print(f"   ✅ ÉXITO - Código generado: {data.get('insumo', {}).get('codigo')}")
        else:
            print(f"   ❌ FALLÓ - Reason: {data.get('message')}")
    else:
        print(f"   ❌ ERROR HTTP: {response.content.decode()}")
    
    # Test 2: Formato alternativo sin arrays
    print(f"\n🧪 TEST 2: Formato sin arrays []")
    
    post_data_2 = {
        'nombre': 'Test Debug 2',
        'categoria_id': categoria.id,
        'unidad_medida_id': unidad.id,
        'cantidad_producida': '1.0',
        'descripcion': 'Test de debug 2',
        'componente_insumo': [insumo1.id, insumo2.id],
        'componente_cantidad': ['0.5', '0.3']
    }
    
    print(f"   Enviando: {post_data_2}")
    
    response = client.post('/dashboard/insumos-compuestos/crear/', 
                          post_data_2, 
                          HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Message: {data.get('message')}")
        if data.get('success'):
            print(f"   ✅ ÉXITO - Código generado: {data.get('insumo', {}).get('codigo')}")
        else:
            print(f"   ❌ FALLÓ - Reason: {data.get('message')}")
    else:
        print(f"   ❌ ERROR HTTP: {response.content.decode()}")
    
    # Test 3: Simular datos como FormData
    print(f"\n🧪 TEST 3: Simulando FormData real")
    
    # Esto simula cómo Django recibe los datos cuando se envían vía FormData
    from django.http import QueryDict
    
    formdata_simulation = QueryDict(mutable=True)
    formdata_simulation['nombre'] = 'Test Debug 3'
    formdata_simulation['categoria_id'] = str(categoria.id)
    formdata_simulation['unidad_medida_id'] = str(unidad.id)
    formdata_simulation['cantidad_producida'] = '1.0'
    formdata_simulation['descripcion'] = 'Test FormData'
    formdata_simulation.appendlist('componente_insumo[]', str(insumo1.id))
    formdata_simulation.appendlist('componente_insumo[]', str(insumo2.id))
    formdata_simulation.appendlist('componente_cantidad[]', '0.5')
    formdata_simulation.appendlist('componente_cantidad[]', '0.3')
    
    print(f"   FormData simulado:")
    for key in formdata_simulation.keys():
        values = formdata_simulation.getlist(key)
        print(f"     {key}: {values}")
    
    # Test directo de la vista
    from django.test import RequestFactory
    from dashboard.views import crear_insumo_compuesto
    from django.contrib.auth.models import AnonymousUser
    
    factory = RequestFactory()
    request = factory.post('/dashboard/insumos-compuestos/crear/', formdata_simulation)
    request.user = admin_user
    request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
    
    response = crear_insumo_compuesto(request)
    print(f"   Status directo: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = json.loads(response.content.decode())
            print(f"   Success directo: {data.get('success')}")
            print(f"   Message directo: {data.get('message')}")
        except:
            print(f"   Response no es JSON: {response.content.decode()}")
    
    print(f"\n" + "=" * 60)
    print(f"💡 RECOMENDACIONES:")
    print(f"   1. Verificar que el formulario use name='componente_insumo[]'")
    print(f"   2. Verificar que JavaScript envíe los datos correctamente")
    print(f"   3. Revisar logs del servidor para ver datos POST recibidos")
    print(f"   4. Usar herramientas de desarrollo del navegador para verificar FormData")

if __name__ == '__main__':
    test_debug_componentes()
