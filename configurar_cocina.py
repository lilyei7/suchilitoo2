#!/usr/bin/env python3
"""
Script para configurar datos iniciales para la aplicación de cocina
"""

import os
import sys
import django
from django.contrib.auth.models import Group, User
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from cocina.models import EstadoCocina, TiempoPreparacion
from restaurant.models import ProductoVenta

def main():
    print("=== CONFIGURACIÓN INICIAL DE COCINA ===\n")
    
    # 1. Crear grupo de cocina
    print("1. Creando grupo de cocina...")
    grupo_cocina, created = Group.objects.get_or_create(name='Cocina')
    if created:
        print("   ✓ Grupo 'Cocina' creado")
    else:
        print("   ✓ Grupo 'Cocina' ya existe")
    
    # 2. Crear usuarios de cocina
    print("\n2. Creando usuarios de cocina...")
    
    # Usuario cocinero principal
    cocinero_principal, created = User.objects.get_or_create(
        username='cocinero',
        defaults={
            'first_name': 'Chef',
            'last_name': 'Principal',
            'email': 'cocinero@sushi.com',
            'is_staff': True,
            'is_active': True,
        }
    )
    
    if created:
        cocinero_principal.set_password('cocinero123')
        cocinero_principal.save()
        print("   ✓ Usuario 'cocinero' creado (password: cocinero123)")
    else:
        print("   ✓ Usuario 'cocinero' ya existe")
    
    # Agregar al grupo de cocina
    grupo_cocina.user_set.add(cocinero_principal)
    
    # Usuario ayudante de cocina
    ayudante, created = User.objects.get_or_create(
        username='ayudante',
        defaults={
            'first_name': 'Ayudante',
            'last_name': 'Cocina',
            'email': 'ayudante@sushi.com',
            'is_staff': True,
            'is_active': True,
        }
    )
    
    if created:
        ayudante.set_password('ayudante123')
        ayudante.save()
        print("   ✓ Usuario 'ayudante' creado (password: ayudante123)")
    else:
        print("   ✓ Usuario 'ayudante' ya existe")
    
    # Agregar al grupo de cocina
    grupo_cocina.user_set.add(ayudante)
    
    # 3. Crear estados de cocina
    print("\n3. Creando estados de cocina...")
    
    estados_cocina = [
        ('recibida', 'Recibida', '#6c757d', 1),
        ('en_preparacion', 'En Preparación', '#17a2b8', 2),
        ('lista', 'Lista', '#28a745', 3),
        ('entregada', 'Entregada', '#007bff', 4),
        ('cancelada', 'Cancelada', '#dc3545', 5),
    ]
    
    for nombre, descripcion, color, orden in estados_cocina:
        estado, created = EstadoCocina.objects.get_or_create(
            nombre=nombre,
            defaults={
                'descripcion': descripcion,
                'color': color,
                'orden': orden,
                'activo': True,
            }
        )
        
        if created:
            print(f"   ✓ Estado '{descripcion}' creado")
        else:
            print(f"   ✓ Estado '{descripcion}' ya existe")
    
    # 4. Configurar tiempos de preparación para productos existentes
    print("\n4. Configurando tiempos de preparación...")
    
    productos = ProductoVenta.objects.all()
    
    # Tiempos por defecto basados en categorías/tipos
    tiempos_por_categoria = {
        'sushi': 10,
        'sashimi': 8,
        'maki': 12,
        'temaki': 15,
        'ramen': 20,
        'entrante': 8,
        'postre': 5,
        'bebida': 2,
    }
    
    for producto in productos:
        # Determinar tiempo basado en el nombre del producto
        tiempo_estimado = 15  # Tiempo por defecto
        
        nombre_lower = producto.nombre.lower()
        for categoria, tiempo in tiempos_por_categoria.items():
            if categoria in nombre_lower:
                tiempo_estimado = tiempo
                break
        
        tiempo_prep, created = TiempoPreparacion.objects.get_or_create(
            producto=producto,
            defaults={
                'tiempo_estimado': tiempo_estimado,
                'tiempo_promedio': tiempo_estimado,
                'cantidad_preparaciones': 0,
            }
        )
        
        if created:
            print(f"   ✓ Tiempo configurado para '{producto.nombre}': {tiempo_estimado} min")
    
    # 5. Asignar permisos al grupo de cocina
    print("\n5. Asignando permisos al grupo de cocina...")
    
    # Permisos básicos para cocina
    permisos_cocina = [
        'view_orden',
        'change_orden',
        'view_ordenitem',
        'change_ordenitem',
        'view_productoventa',
        'view_mesa',
    ]
    
    for permiso_name in permisos_cocina:
        try:
            # Buscar el permiso
            permiso = Permission.objects.get(codename=permiso_name)
            grupo_cocina.permissions.add(permiso)
            print(f"   ✓ Permiso '{permiso_name}' asignado")
        except Permission.DoesNotExist:
            print(f"   ⚠ Permiso '{permiso_name}' no encontrado")
    
    # 6. Crear permisos específicos para cocina
    print("\n6. Creando permisos específicos para cocina...")
    
    # Obtener content types
    try:
        ct_orden_cocina = ContentType.objects.get(app_label='cocina', model='ordencocina')
        ct_item_cocina = ContentType.objects.get(app_label='cocina', model='itemcocina')
        
        permisos_especificos = [
            ('view_dashboard_cocina', 'Can view kitchen dashboard', ct_orden_cocina),
            ('change_orden_cocina_estado', 'Can change kitchen order state', ct_orden_cocina),
            ('view_estadisticas_cocina', 'Can view kitchen statistics', ct_orden_cocina),
            ('change_item_cocina_estado', 'Can change kitchen item state', ct_item_cocina),
        ]
        
        for codename, name, content_type in permisos_especificos:
            permiso, created = Permission.objects.get_or_create(
                codename=codename,
                content_type=content_type,
                defaults={'name': name}
            )
            
            if created:
                print(f"   ✓ Permiso '{name}' creado")
            else:
                print(f"   ✓ Permiso '{name}' ya existe")
            
            grupo_cocina.permissions.add(permiso)
    
    except ContentType.DoesNotExist:
        print("   ⚠ Modelos de cocina no encontrados, ejecute las migraciones primero")
    
    print("\n=== CONFIGURACIÓN COMPLETADA ===")
    print("\nUsuarios de cocina creados:")
    print("- cocinero / cocinero123")
    print("- ayudante / ayudante123")
    print("\nAcceso a cocina: http://localhost:8000/cocina/")
    print("\n¡La aplicación de cocina está lista para usar!")

if __name__ == '__main__':
    main()
