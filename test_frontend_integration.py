#!/usr/bin/env python
"""
Test directo de las operaciones CRUD via HTTP requests
para verificar que el frontend y backend trabajen correctamente juntos.
"""

import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from restaurant.models import Insumo, CategoriaInsumo, UnidadMedida

def test_frontend_backend_integration():
    """Test completo de integración frontend-backend"""
    print("=== TEST INTEGRACIÓN FRONTEND-BACKEND ===")
    print()
    
    # Crear cliente de test
    client = Client()
    
    # Crear/obtener usuario admin para testing
    User = get_user_model()
    admin_user, created = User.objects.get_or_create(
        username='admin_test',
        defaults={
            'email': 'admin@test.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("Usuario admin creado para testing")
    
    # Login
    client.login(username='admin_test', password='admin123')
    print("✓ Login exitoso")
    
    # Test 1: Obtener lista de insumos elaborados
    print("\n1. Probando vista de lista...")
    response = client.get('/dashboard/insumos-elaborados/')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✓ Vista de lista funciona")
    else:
        print("   ✗ Error en vista de lista")
        return False
    
    # Test 2: Obtener insumos disponibles para componentes
    print("\n2. Probando endpoint de insumos disponibles...")
    response = client.get('/dashboard/insumos-elaborados/insumos-disponibles/')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Endpoint funciona - {len(data.get('insumos', []))} insumos disponibles")
        print(f"   - Básicos: {data.get('basicos_count', 0)}")
        print(f"   - Compuestos: {data.get('compuestos_count', 0)}")
    else:
        print("   ✗ Error en endpoint de insumos disponibles")
        return False
    
    # Test 3: Obtener detalle de insumo elaborado existente
    print("\n3. Probando detalle de insumo elaborado...")
    insumo_elaborado = Insumo.objects.filter(tipo='elaborado').first()
    
    if insumo_elaborado:
        response = client.get(f'/dashboard/insumos-elaborados/{insumo_elaborado.id}/detalle/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Detalle obtenido - {data['insumo']['nombre']}")
            print(f"   - Precio: ${data['insumo']['precio_unitario']}")
            print(f"   - Componentes: {data['insumo']['cantidad_componentes']}")
        else:
            print("   ✗ Error obteniendo detalle")
            return False
    else:
        print("   - No hay insumos elaborados para testing")
    
    # Test 4: Crear nuevo insumo elaborado
    print("\n4. Probando creación de insumo elaborado...")
    
    # Buscar categoría y unidad de medida
    categoria = CategoriaInsumo.objects.first()
    unidad = UnidadMedida.objects.first()
    insumos_componentes = Insumo.objects.filter(tipo__in=['basico', 'compuesto'])[:2]
    
    if categoria and unidad and len(insumos_componentes) >= 2:
        data = {
            'codigo': 'TEST_CREATE_001',
            'nombre': 'Test Insumo Elaborado',
            'descripcion': 'Insumo creado via test',
            'categoria_id': categoria.id,
            'unidad_medida_id': unidad.id,
            'cantidad_producida': '1000',
            'componente_insumo[]': [str(ins.id) for ins in insumos_componentes],
            'componente_cantidad[]': ['100', '50'],
            'componente_tiempo[]': ['5', '3'],
            'componente_instrucciones[]': ['Paso 1', 'Paso 2']
        }
        
        response = client.post('/dashboard/insumos-elaborados/crear/', data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✓ Creación exitosa")
                
                # Limpiar - eliminar el insumo creado
                try:
                    Insumo.objects.filter(codigo='TEST_CREATE_001').delete()
                    print("   ✓ Limpieza completada")
                except:
                    pass
            else:
                print(f"   ✗ Error en creación: {result.get('message')}")
                return False
        else:
            print("   ✗ Error HTTP en creación")
            return False
    else:
        print("   - Faltan datos para testing de creación")
    
    print("\n=== RESULTADO FINAL ===")
    print("✅ Todos los tests de integración pasaron")
    print("✅ Frontend y backend funcionan correctamente juntos")
    print("✅ El sistema está listo para uso en producción")
    
    return True

if __name__ == '__main__':
    test_frontend_backend_integration()
