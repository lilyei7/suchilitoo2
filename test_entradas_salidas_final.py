#!/usr/bin/env python
"""
Test final para verificar que toda la funcionalidad de entradas_salidas funcione correctamente
"""
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from accounts.models import Usuario, Sucursal, Rol
from dashboard.models import Proveedor, Insumo

User = get_user_model()

def test_entradas_salidas_complete():
    print("=== TEST COMPLETO ENTRADAS Y SALIDAS ===")
    
    client = Client()
    
    # Test 1: Acceso sin login (debe redirigir)
    print("\n1. Test acceso sin login:")
    response = client.get('/dashboard/entradas-salidas/')
    if response.status_code == 302:
        print("   ✓ Redirige correctamente al login")
    else:
        print(f"   ✗ Error: Status {response.status_code}")
    
    # Test 2: Login y acceso con usuario admin
    print("\n2. Test con usuario admin:")
    admin_user = Usuario.objects.filter(is_superuser=True).first()
    if admin_user:
        client.force_login(admin_user)
        response = client.get('/dashboard/entradas-salidas/')
        
        if response.status_code == 200:
            print("   ✓ Página carga correctamente")
            context = response.context
            if context:
                print(f"   ✓ Sucursales: {context['sucursales'].count()}")
                print(f"   ✓ Proveedores: {context['proveedores'].count()}")
                print(f"   ✓ Es admin: {context.get('is_admin', False)}")
                print(f"   ✓ Sucursal fija: {context.get('user_sucursal')}")
            else:
                print("   ⚠ Sin contexto disponible")
        else:
            print(f"   ✗ Error: Status {response.status_code}")
    else:
        print("   ✗ No hay usuarios admin")
    
    # Test 3: Endpoint de obtener insumos
    print("\n3. Test endpoint obtener-insumos:")
    sucursal = Sucursal.objects.first()
    proveedor = Proveedor.objects.filter(estado='activo').first() if sucursal else None
    
    if sucursal and proveedor:
        url = f'/dashboard/entradas-salidas/obtener-insumos?sucursal_id={sucursal.id}&proveedor_id={proveedor.id}'
        response = client.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Endpoint funciona: {data.get('success')}")
            print(f"   ✓ Insumos encontrados: {len(data.get('insumos', []))}")
            
            # Mostrar algunos insumos
            for insumo in data.get('insumos', [])[:2]:
                print(f"     * {insumo['codigo']} - {insumo['nombre']}")
        else:
            print(f"   ✗ Error: Status {response.status_code}")
    else:
        print("   ⚠ No hay sucursales o proveedores disponibles")
    
    # Test 4: Test con usuario gerente
    print("\n4. Test con usuario gerente:")
    gerente = Usuario.objects.filter(rol__nombre='gerente', sucursal__isnull=False).first()
    if gerente:
        client.force_login(gerente)
        response = client.get('/dashboard/entradas-salidas/')
        
        if response.status_code == 200:
            print("   ✓ Página carga correctamente")
            context = response.context
            if context:
                print(f"   ✓ Sucursales: {context['sucursales'].count()}")
                print(f"   ✓ Proveedores: {context['proveedores'].count()}")
                print(f"   ✓ Es admin: {context.get('is_admin', False)}")
                print(f"   ✓ Sucursal fija: {context.get('user_sucursal')}")
                
                # Verificar que solo ve su sucursal
                sucursales_list = list(context['sucursales'])
                if len(sucursales_list) == 1 and sucursales_list[0] == gerente.sucursal:
                    print(f"   ✓ Solo ve su sucursal: {sucursales_list[0].nombre}")
                else:
                    print(f"   ⚠ Ve {len(sucursales_list)} sucursales")
        else:
            print(f"   ✗ Error: Status {response.status_code}")
    else:
        print("   ⚠ No hay gerentes con sucursal asignada")
    
    # Test 5: Template tags funcionando
    print("\n5. Test template tags:")
    from django.template import Template, Context
    
    template_content = '''
{% load permission_tags %}
- can_create('inventario'): {{ user|can_create:'inventario' }}
- has_feature('ver_costos'): {{ user|has_feature:'ver_costos' }}
    '''
    
    try:
        template = Template(template_content)
        context = Context({'user': admin_user})
        result = template.render(context)
        print("   ✓ Template tags funcionan correctamente")
        print(f"   Resultado: {result.strip()}")
    except Exception as e:
        print(f"   ✗ Error en template tags: {e}")
    
    print("\n=== TEST COMPLETO FINALIZADO ===")

if __name__ == '__main__':
    test_entradas_salidas_complete()
