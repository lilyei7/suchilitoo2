#!/usr/bin/env python
"""
Script para crear datos de test para el sistema de meseros
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from accounts.models import Rol, Sucursal
from dashboard.models_ventas import Mesa

User = get_user_model()

def crear_usuarios_meseros():
    print('=== CREANDO USUARIOS MESEROS ===')
    
    # Verificar que existe el rol de mesero
    try:
        rol_mesero = Rol.objects.get(nombre='mesero')
        print(f'✓ Rol mesero encontrado: {rol_mesero.nombre}')
    except Rol.DoesNotExist:
        print('✗ Rol mesero no existe. Creando...')
        rol_mesero = Rol.objects.create(
            nombre='mesero',
            descripcion='Mesero del restaurante'
        )
        print(f'✓ Rol mesero creado: {rol_mesero.nombre}')
    
    # Obtener sucursal por defecto
    sucursal = Sucursal.objects.first()
    if not sucursal:
        print('✗ No hay sucursales. Creando sucursal por defecto...')
        sucursal = Sucursal.objects.create(
            nombre='Sucursal Principal',
            direccion='Calle Principal 123',
            telefono='555-0123'
        )
        print(f'✓ Sucursal creada: {sucursal.nombre}')
    
    # Crear usuarios meseros de test
    meseros_data = [
        {
            'username': 'mesero1',
            'password': 'mesero123',
            'first_name': 'Ana',
            'last_name': 'García',
            'email': 'ana.garcia@sushi.com'
        },
        {
            'username': 'mesero2', 
            'password': 'mesero123',
            'first_name': 'Pedro',
            'last_name': 'Martínez',
            'email': 'pedro.martinez@sushi.com'
        },
        {
            'username': 'mesero3',
            'password': 'mesero123', 
            'first_name': 'Laura',
            'last_name': 'López',
            'email': 'laura.lopez@sushi.com'
        }
    ]
    
    for data in meseros_data:
        username = data['username']
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            print(f'⚠ Usuario {username} ya existe. Actualizando contraseña...')
            user = User.objects.get(username=username)
            user.set_password(data['password'])
            user.save()
        else:
            print(f'Creando usuario: {username}')
            user = User.objects.create_user(
                username=username,
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email']
            )
        
        # Asignar rol y sucursal
        user.rol = rol_mesero
        user.sucursal = sucursal
        user.save()
        
        print(f'✓ Usuario {username} configurado con rol mesero')

def crear_mesas():
    print('\n=== CREANDO MESAS DE TEST ===')
    
    # Obtener sucursal
    sucursal = Sucursal.objects.first()
    if not sucursal:
        print('✗ No hay sucursales disponibles')
        return
    
    # Crear mesas si no existen
    for i in range(1, 13):  # Crear 12 mesas
        mesa_numero = str(i)
        
        if Mesa.objects.filter(numero=mesa_numero, sucursal=sucursal).exists():
            print(f'⚠ Mesa {mesa_numero} ya existe')
            continue
        
        mesa = Mesa.objects.create(
            numero=mesa_numero,
            nombre=f'Mesa {i}',
            capacidad=4 if i <= 8 else 6,  # Mesas pequeñas y grandes
            sucursal=sucursal,
            estado='disponible'
        )
        
        print(f'✓ Mesa {mesa_numero} creada')

def main():
    print('INICIANDO CREACIÓN DE DATOS PARA MESEROS...\n')
    
    try:
        crear_usuarios_meseros()
        crear_mesas()
        
        print('\n=== RESUMEN ===')
        print(f'Usuarios meseros: {User.objects.filter(rol__nombre="mesero").count()}')
        print(f'Mesas creadas: {Mesa.objects.count()}')
        
        print('\n=== USUARIOS CREADOS ===')
        for user in User.objects.filter(rol__nombre='mesero'):
            print(f'- {user.username} ({user.first_name})')
            print(f'  Contraseña: mesero123')
        
        print('\n✅ DATOS DE MESEROS CREADOS EXITOSAMENTE')
        
    except Exception as e:
        print(f'❌ Error al crear datos: {str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    main()
