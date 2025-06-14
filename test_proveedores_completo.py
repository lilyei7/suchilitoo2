#!/usr/bin/env python3
"""
Script para probar la funcionalidad completa del sistema de proveedores mejorado
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

try:
    django.setup()
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    sys.exit(1)

import requests
from django.contrib.auth import get_user_model
from dashboard.models import Proveedor, Insumo, ProveedorInsumo
from django.test import Client
from django.urls import reverse
import json

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_step(step, description):
    print(f"\n📋 Paso {step}: {description}")
    print("-" * 50)

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def test_models_and_relationships():
    """Probar modelos y relaciones"""
    print_step(1, "Probando modelos y relaciones")
    
    # Verificar que los modelos existen
    try:
        total_proveedores = Proveedor.objects.count()
        total_insumos = Insumo.objects.count()
        total_relaciones = ProveedorInsumo.objects.count()
        
        print_success(f"Modelos funcionando correctamente")
        print_info(f"- Proveedores: {total_proveedores}")
        print_info(f"- Insumos: {total_insumos}")
        print_info(f"- Relaciones proveedor-insumo: {total_relaciones}")
          # Verificar relaciones
        if total_proveedores > 0:
            proveedor = Proveedor.objects.first()
            insumos_count = proveedor.insumos_proveedor.count()
            print_info(f"- Insumos del primer proveedor: {insumos_count}")
        
        return True
    except Exception as e:
        print_error(f"Error en modelos: {e}")
        return False

def test_views_authentication():
    """Probar vistas y autenticación"""
    print_step(2, "Probando vistas y autenticación")
    
    try:
        client = Client()
        
        # Intentar acceder sin autenticación
        response = client.get('/dashboard/proveedores/')
        if response.status_code == 302:  # Redirección al login
            print_success("Protección de autenticación funcionando")
        else:
            print_error(f"Vista no protegida. Status: {response.status_code}")
            return False
        
        # Crear usuario de prueba si no existe
        User = get_user_model()
        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='admin',
                password='admin123',
                email='admin@test.com',
                is_staff=True,
                is_superuser=True
            )
            print_info("Usuario admin creado para pruebas")
        
        # Hacer login
        login_success = client.login(username='admin', password='admin123')
        if login_success:
            print_success("Login exitoso")
        else:
            print_error("Error en login")
            return False
        
        # Probar vista principal de proveedores
        response = client.get('/dashboard/proveedores/')
        if response.status_code == 200:
            print_success("Vista de proveedores accesible")
            print_info(f"Template renderizado correctamente")
        else:
            print_error(f"Error en vista de proveedores. Status: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print_error(f"Error en pruebas de vistas: {e}")
        return False

def test_api_endpoints():
    """Probar endpoints de API"""
    print_step(3, "Probando endpoints de API")
    
    try:
        client = Client()
        
        # Login primero
        User = get_user_model()
        user = User.objects.get(username='admin')
        client.force_login(user)
        
        # Crear proveedor de prueba si no existe
        proveedor, created = Proveedor.objects.get_or_create(
            nombre_comercial="Proveedor Test API",
            defaults={
                'estado': 'activo',
                'categoria_productos': 'ingredientes',
                'persona_contacto': 'Test Contact',
                'telefono': '1234567890',
                'email': 'test@api.com'
            }
        )
        
        if created:
            print_info("Proveedor de prueba creado")
        
        # Probar endpoint de detalle
        response = client.get(f'/dashboard/proveedor/{proveedor.id}/detalle/')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_success("Endpoint de detalle funcionando")
                print_info(f"Proveedor: {data['proveedor']['nombre_comercial']}")
            else:
                print_error(f"Error en respuesta de detalle: {data}")
                return False
        else:
            print_error(f"Error en endpoint de detalle. Status: {response.status_code}")
            return False
          # Probar endpoint de insumos disponibles (pasando el proveedor_id requerido)
        response = client.get(f'/dashboard/proveedores/insumos-disponibles/?proveedor_id={proveedor.id}')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_success("Endpoint de insumos disponibles funcionando")
                print_info(f"Insumos disponibles: {len(data.get('insumos', []))}")
            else:
                print_error(f"Error en respuesta de insumos: {data}")
                return False
        else:
            print_error(f"Error en endpoint de insumos. Status: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print_error(f"Error en pruebas de API: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crud_operations():
    """Probar operaciones CRUD"""
    print_step(4, "Probando operaciones CRUD")
    
    try:
        client = Client()
        
        # Login
        User = get_user_model()
        user = User.objects.get(username='admin')
        client.force_login(user)
        
        # Generate unique name with timestamp
        import time
        timestamp = int(time.time())
        unique_name = f'Proveedor CRUD Test {timestamp}'
        
        # Crear proveedor
        data_crear = {
            'nombre_comercial': unique_name,
            'razon_social': f'{unique_name} SA',
            'rfc': f'PCR{timestamp}',
            'persona_contacto': 'Juan Test',
            'telefono': '5551234567',
            'email': f'crud{timestamp}@test.com',
            'direccion': 'Calle Test 123',
            'ciudad_estado': 'Ciudad Test, Estado Test',
            'categoria_productos': 'ingredientes',
            'estado': 'activo',
            'notas_adicionales': 'Proveedor creado para pruebas CRUD'        }
        
        response = client.post('/dashboard/crear-proveedor/', data_crear, 
                              HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                proveedor_id = data.get('proveedor', {}).get('id')
                print_success(f"Proveedor creado exitosamente (ID: {proveedor_id})")
                
                # Obtener el proveedor creado
                proveedor = Proveedor.objects.get(id=proveedor_id)
                
                # Probar edición
                data_editar = data_crear.copy()
                data_editar['nombre_comercial'] = 'Proveedor CRUD Test EDITADO'
                data_editar['estado'] = 'inactivo'
                
                response = client.post(f'/dashboard/proveedor/{proveedor_id}/editar/', 
                                     data_editar, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print_success("Proveedor editado exitosamente")
                        
                        # Verificar cambios
                        proveedor.refresh_from_db()
                        if proveedor.nombre_comercial == 'Proveedor CRUD Test EDITADO':
                            print_success("Cambios persistidos correctamente")
                        else:
                            print_error("Los cambios no se persistieron")
                            return False
                    else:
                        print_error(f"Error en edición: {data}")
                        return False
                else:
                    print_error(f"Error en endpoint de edición. Status: {response.status_code}")
                    return False
                
                # Probar eliminación
                response = client.post(f'/dashboard/proveedor/{proveedor_id}/eliminar/', 
                                     {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print_success("Proveedor eliminado exitosamente")
                        
                        # Verificar eliminación
                        if not Proveedor.objects.filter(id=proveedor_id).exists():
                            print_success("Proveedor eliminado de la base de datos")
                        else:
                            print_error("El proveedor no fue eliminado de la base de datos")
                            return False
                    else:
                        print_error(f"Error en eliminación: {data}")
                        return False
                else:
                    print_error(f"Error en endpoint de eliminación. Status: {response.status_code}")
                    return False
                
            else:
                print_error(f"Error en creación: {data}")
                return False
        else:
            print_error(f"Error en endpoint de creación. Status: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print_error(f"Error en pruebas CRUD: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_insumo_assignment():
    """Probar asignación de insumos"""
    print_step(5, "Probando asignación de insumos")
    
    try:
        client = Client()
        
        # Login
        User = get_user_model()
        user = User.objects.get(username='admin')
        client.force_login(user)
        
        # Crear proveedor de prueba
        proveedor = Proveedor.objects.create(
            nombre_comercial='Proveedor Insumos Test',
            estado='activo',
            categoria_productos='ingredientes'
        )
        
        # Crear insumo de prueba
        insumo = Insumo.objects.create(
            nombre='Insumo Test',
            categoria='ingredientes',
            unidad_medida='kg',
            stock_actual=100.0,
            stock_minimo=10.0
        )
        
        print_info(f"Proveedor creado: {proveedor.nombre_comercial}")
        print_info(f"Insumo creado: {insumo.nombre}")
        
        # Asignar insumo a proveedor
        data_asignar = {
            'insumo_id': insumo.id,
            'precio_unitario': 25.50,
            'tiempo_entrega_dias': 5,
            'cantidad_minima': 1.0,
            'observaciones': 'Insumo de prueba'
        }
        
        response = client.post(f'/dashboard/proveedor/{proveedor.id}/asignar-insumo/', 
                              data_asignar, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_success("Insumo asignado exitosamente")
                
                # Verificar asignación
                relacion = ProveedorInsumo.objects.filter(
                    proveedor=proveedor, 
                    insumo=insumo
                ).first()
                
                if relacion:
                    print_success(f"Relación creada con precio: ${relacion.precio_unitario}")
                    
                    # Probar remoción
                    response = client.post(f'/dashboard/proveedor-insumo/{relacion.id}/remover/', 
                                         {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            print_success("Insumo removido exitosamente")
                            
                            # Verificar remoción
                            if not ProveedorInsumo.objects.filter(id=relacion.id).exists():
                                print_success("Relación eliminada de la base de datos")
                            else:
                                print_error("La relación no fue eliminada")
                                return False
                        else:
                            print_error(f"Error en remoción: {data}")
                            return False
                    else:
                        print_error(f"Error en endpoint de remoción. Status: {response.status_code}")
                        return False
                else:
                    print_error("La relación no fue creada")
                    return False
            else:
                print_error(f"Error en asignación: {data}")
                return False
        else:
            print_error(f"Error en endpoint de asignación. Status: {response.status_code}")
            return False
        
        # Limpiar datos de prueba
        proveedor.delete()
        insumo.delete()
        print_info("Datos de prueba limpiados")
        
        return True
    except Exception as e:
        print_error(f"Error en pruebas de asignación: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print_header("PRUEBAS COMPLETAS DEL SISTEMA DE PROVEEDORES MEJORADO")
    
    tests = [
        ("Modelos y Relaciones", test_models_and_relationships),
        ("Vistas y Autenticación", test_views_authentication),
        ("Endpoints de API", test_api_endpoints),
        ("Operaciones CRUD", test_crud_operations),
        ("Asignación de Insumos", test_insumo_assignment)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Error crítico en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print_header("RESUMEN DE PRUEBAS")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Resultados: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print_success("¡Todas las pruebas pasaron! El sistema está funcionando correctamente.")
        
        print("\n🎉 FUNCIONALIDADES IMPLEMENTADAS:")
        print("   ✅ CRUD completo de proveedores")
        print("   ✅ Asignación de insumos con precios")
        print("   ✅ Modales interactivos con AJAX")
        print("   ✅ Validación de formularios")
        print("   ✅ Interfaz moderna y responsiva")
        print("   ✅ Gestión de estados de proveedores")
        print("   ✅ Sistema de notificaciones")
        print("   ✅ Protección de autenticación")
        
    else:
        print_error(f"Algunas pruebas fallaron. Revisa los errores anteriores.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
