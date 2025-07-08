#!/usr/bin/env python
"""
Script para probar el filtrado de movimientos para administradores
"""
import os
import sys
import django
from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import Mock
import json

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_restaurant.settings')
django.setup()

from accounts.models import User, Rol
from restaurant.models import Sucursal
from dashboard.models import Insumo, UnidadMedida, CategoriaInsumo, MovimientoInventario
from dashboard.views.entradas_salidas_views import filtrar_movimientos

def test_admin_filtrado():
    """Prueba del filtrado para administradores"""
    print("=== PRUEBA DE FILTRADO PARA ADMINISTRADORES ===")
    
    try:
        # 1. Verificar que existe un usuario admin
        admin_users = User.objects.filter(rol__nombre='admin')
        if not admin_users.exists():
            print("No se encontró usuario admin, creando uno...")
            admin_role, _ = Rol.objects.get_or_create(nombre='admin')
            admin_user = User.objects.create_user(
                username='admin_test',
                email='admin@test.com',
                password='test123',
                rol=admin_role
            )
        else:
            admin_user = admin_users.first()
        
        print(f"Usuario admin: {admin_user.username} (Rol: {admin_user.rol.nombre if admin_user.rol else 'Sin rol'})")
        
        # 2. Verificar que hay sucursales
        sucursales = Sucursal.objects.all()
        print(f"Sucursales disponibles: {sucursales.count()}")
        for sucursal in sucursales:
            print(f"  - {sucursal.nombre} (ID: {sucursal.id})")
        
        # 3. Verificar que hay movimientos
        movimientos = MovimientoInventario.objects.all()
        print(f"Movimientos disponibles: {movimientos.count()}")
        
        # 4. Crear un cliente para las pruebas
        client = Client()
        client.force_login(admin_user)
        
        # 5. Probar filtrado sin parámetros (debería mostrar todos)
        print("\n--- Prueba 1: Sin filtros ---")
        response = client.get(reverse('dashboard:filtrar_movimientos'))
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data['success']}")
            print(f"Movimientos encontrados: {len(data['movimientos'])}")
        else:
            print(f"Error: {response.content.decode()}")
        
        # 6. Probar filtrado por sucursal específica
        if sucursales.exists():
            sucursal_test = sucursales.first()
            print(f"\n--- Prueba 2: Filtrar por sucursal {sucursal_test.nombre} ---")
            response = client.get(reverse('dashboard:filtrar_movimientos'), {
                'sucursal': str(sucursal_test.id)
            })
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Success: {data['success']}")
                print(f"Movimientos encontrados: {len(data['movimientos'])}")
                # Verificar que todos son de la sucursal correcta
                for mov in data['movimientos']:
                    print(f"  - Movimiento {mov['id']}: {mov['sucursal']}")
            else:
                print(f"Error: {response.content.decode()}")
        
        # 7. Probar filtrado con "todos"
        print("\n--- Prueba 3: Filtrar con 'todos' ---")
        response = client.get(reverse('dashboard:filtrar_movimientos'), {
            'sucursal': 'todos'
        })
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data['success']}")
            print(f"Movimientos encontrados: {len(data['movimientos'])}")
        else:
            print(f"Error: {response.content.decode()}")
        
        # 8. Probar filtrado por tipo
        print("\n--- Prueba 4: Filtrar por tipo 'entrada' ---")
        response = client.get(reverse('dashboard:filtrar_movimientos'), {
            'tipo': 'entrada'
        })
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data['success']}")
            print(f"Movimientos encontrados: {len(data['movimientos'])}")
            # Verificar que todos son entradas
            for mov in data['movimientos']:
                print(f"  - Movimiento {mov['id']}: {mov['tipo']}")
        else:
            print(f"Error: {response.content.decode()}")
        
        print("\n=== PRUEBAS COMPLETADAS ===")
        
    except Exception as e:
        print(f"Error en las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_admin_filtrado()
