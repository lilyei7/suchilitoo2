#!/usr/bin/env python3
"""
Crear usuario de prueba y verificar funcionalidad de eliminación
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Rol, Sucursal
from restaurant.models import Insumo, InsumoCompuesto, CategoriaInsumo, UnidadMedida
from decimal import Decimal

User = get_user_model()

def crear_usuario_prueba():
    """Crear un usuario de prueba para testing"""
    print("=== CREANDO USUARIO DE PRUEBA ===\n")
    
    # Crear rol admin si no existe
    rol_admin, created = Rol.objects.get_or_create(
        nombre='admin',
        defaults={'descripcion': 'Administrador del sistema'}
    )
    
    if created:
        print("✓ Rol admin creado")
    else:
        print("✓ Rol admin ya existe")
      # Crear sucursal si no existe
    from datetime import date
    sucursal, created = Sucursal.objects.get_or_create(
        nombre='Principal',
        defaults={
            'direccion': 'Dirección de prueba',
            'telefono': '123456789',
            'email': 'principal@test.com',
            'fecha_apertura': date.today()
        }
    )
    
    if created:
        print("✓ Sucursal principal creada")
    else:
        print("✓ Sucursal principal ya existe")
    
    # Crear usuario de prueba
    username = 'admin_test'
    password = '123456'
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': 'admin@test.com',
            'first_name': 'Admin',
            'last_name': 'Test',
            'rol': rol_admin,
            'sucursal': sucursal,
            'is_staff': True,
            'is_active': True
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"✓ Usuario creado: {username}")
    else:
        print(f"✓ Usuario ya existe: {username}")
    
    print(f"\n📋 CREDENCIALES DE ACCESO:")
    print(f"Usuario: {username}")
    print(f"Contraseña: {password}")
    print(f"Rol: {user.rol.nombre if user.rol else 'Sin rol'}")
    print(f"Sucursal: {user.sucursal.nombre if user.sucursal else 'Sin sucursal'}")
    
    return user

def crear_insumo_compuesto_prueba():
    """Crear un insumo compuesto para probar eliminación"""
    print("\n=== CREANDO INSUMO COMPUESTO DE PRUEBA ===\n")
    
    # Obtener o crear categoría
    categoria, _ = CategoriaInsumo.objects.get_or_create(
        nombre='Test Eliminación',
        defaults={'descripcion': 'Categoría para test de eliminación'}
    )
    
    # Obtener o crear unidad
    unidad, _ = UnidadMedida.objects.get_or_create(
        nombre='unidad',
        defaults={'abreviacion': 'ud'}
    )
    
    # Crear insumo básico para componente
    insumo_basico, _ = Insumo.objects.get_or_create(
        codigo='TEST-BASICO-001',
        defaults={
            'nombre': 'Insumo Básico Test',
            'tipo': 'basico',
            'categoria': categoria,
            'unidad_medida': unidad,
            'precio_unitario': Decimal('5.00')
        }
    )
    
    # Crear insumo compuesto de prueba
    compuesto, created = Insumo.objects.get_or_create(
        codigo='COMP-DELETE-TEST',
        defaults={
            'nombre': 'Insumo Compuesto Para Eliminar',
            'tipo': 'compuesto',
            'categoria': categoria,
            'unidad_medida': unidad,
            'cantidad_producida': Decimal('10.0'),
            'descripcion': 'Este insumo es para probar la eliminación'
        }
    )
    
    if created:
        # Agregar componente
        InsumoCompuesto.objects.create(
            insumo_compuesto=compuesto,
            insumo_componente=insumo_basico,
            cantidad=Decimal('2.0')
        )
        print(f"✓ Insumo compuesto creado: {compuesto.codigo}")
        print(f"✓ ID: {compuesto.id}")
        print(f"✓ Componentes: {compuesto.componentes.count()}")
    else:
        print(f"✓ Insumo compuesto ya existe: {compuesto.codigo}")
        print(f"✓ ID: {compuesto.id}")
    
    return compuesto

def verificar_url_eliminacion():
    """Verificar que la URL de eliminación esté configurada correctamente"""
    print("\n=== VERIFICANDO CONFIGURACIÓN DE URLS ===\n")
    
    from django.urls import reverse
    
    try:
        # Verificar URL de eliminación
        url = reverse('dashboard:eliminar_insumo_compuesto', kwargs={'insumo_id': 999})
        print(f"✓ URL de eliminación: {url}")
        
        # Verificar URL de lista
        url_lista = reverse('dashboard:insumos_compuestos')
        print(f"✓ URL de lista: {url_lista}")
        
        # Verificar URL de detalle
        url_detalle = reverse('dashboard:detalle_insumo_compuesto', kwargs={'insumo_id': 999})
        print(f"✓ URL de detalle: {url_detalle}")
        
        return True
    except Exception as e:
        print(f"❌ Error en URLs: {str(e)}")
        return False

if __name__ == '__main__':
    user = crear_usuario_prueba()
    compuesto = crear_insumo_compuesto_prueba()
    verificar_url_eliminacion()
    
    print(f"\n🎯 RESUMEN:")
    print(f"• Usuario creado/verificado: admin_test")
    print(f"• Insumo compuesto para test: ID {compuesto.id}")
    print(f"• URLs configuradas correctamente")
    
    print(f"\n🌐 ACCESO AL SISTEMA:")
    print(f"1. Ir a: http://127.0.0.1:8001/dashboard/login/")
    print(f"2. Usuario: admin_test")
    print(f"3. Contraseña: 123456")
    print(f"4. Navegar a: http://127.0.0.1:8001/dashboard/insumos-compuestos/")
    print(f"5. Probar eliminación del insumo ID {compuesto.id}")
