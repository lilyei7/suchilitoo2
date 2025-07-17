#!/usr/bin/env python
"""
Script para crear datos de prueba para el módulo de RRHH
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from rrhh.models import Rol, Empleado
from accounts.models import Sucursal
from django.utils import timezone
from datetime import date

def crear_datos_prueba():
    print("Creando datos de prueba para RRHH...")
    
    # Crear roles si no existen
    roles_data = [
        {'nombre': 'Gerente', 'descripcion': 'Responsable de la gestión general del restaurante'},
        {'nombre': 'Chef', 'descripcion': 'Responsable de la cocina y preparación de alimentos'},
        {'nombre': 'Mesero', 'descripcion': 'Atención al cliente y servicio de mesas'},
        {'nombre': 'Cajero', 'descripcion': 'Manejo de caja y facturación'},
        {'nombre': 'Auxiliar de Cocina', 'descripcion': 'Apoyo en la preparación de alimentos'},
        {'nombre': 'Administrador', 'descripcion': 'Gestión administrativa y recursos humanos'},
    ]

    for rol_data in roles_data:
        rol, created = Rol.objects.get_or_create(
            nombre=rol_data['nombre'],
            defaults={'descripcion': rol_data['descripcion']}
        )
        if created:
            print(f"✓ Rol '{rol.nombre}' creado")
        else:
            print(f"- Rol '{rol.nombre}' ya existe")

    # Verificar sucursales
    sucursales = Sucursal.objects.all()
    print(f"\nSucursales disponibles: {sucursales.count()}")
    for sucursal in sucursales:
        print(f"  - {sucursal.nombre}")

    # Crear empleados de ejemplo
    if sucursales.exists():
        sucursal_principal = sucursales.first()
        
        empleados_data = [
            {
                'nombre': 'Juan Carlos',
                'apellido': 'Rodriguez',
                'rut': '12345678-9',
                'fecha_nacimiento': date(1985, 3, 15),
                'direccion': 'Av. Principal 123',
                'telefono': '+56912345678',
                'email': 'juan.rodriguez@restaurante.com',
                'cargo': 'Gerente General',
                'salario_base': 1500000,
                'tipo_contrato': 'indefinido',
                'estado': 'activo',
                'roles': ['Gerente', 'Administrador']
            },
            {
                'nombre': 'María Elena',
                'apellido': 'González',
                'rut': '98765432-1',
                'fecha_nacimiento': date(1990, 7, 22),
                'direccion': 'Calle Secundaria 456',
                'telefono': '+56987654321',
                'email': 'maria.gonzalez@restaurante.com',
                'cargo': 'Chef Principal',
                'salario_base': 1200000,
                'tipo_contrato': 'indefinido',
                'estado': 'activo',
                'roles': ['Chef']
            },
            {
                'nombre': 'Pedro',
                'apellido': 'Martínez',
                'rut': '11223344-5',
                'fecha_nacimiento': date(1992, 12, 5),
                'direccion': 'Plaza Central 789',
                'telefono': '+56911223344',
                'email': 'pedro.martinez@restaurante.com',
                'cargo': 'Mesero Senior',
                'salario_base': 600000,
                'tipo_contrato': 'indefinido',
                'estado': 'activo',
                'roles': ['Mesero']
            }
        ]

        for emp_data in empleados_data:
            empleado, created = Empleado.objects.get_or_create(
                rut=emp_data['rut'],
                defaults={
                    'nombre': emp_data['nombre'],
                    'apellido': emp_data['apellido'],
                    'fecha_nacimiento': emp_data['fecha_nacimiento'],
                    'direccion': emp_data['direccion'],
                    'telefono': emp_data['telefono'],
                    'email': emp_data['email'],
                    'cargo': emp_data['cargo'],
                    'salario_base': emp_data['salario_base'],
                    'tipo_contrato': emp_data['tipo_contrato'],
                    'estado': emp_data['estado'],
                    'fecha_ingreso': date.today(),
                }
            )
            
            if created:
                # Asignar sucursal
                empleado.sucursales.add(sucursal_principal)
                
                # Asignar roles
                for rol_nombre in emp_data['roles']:
                    try:
                        rol = Rol.objects.get(nombre=rol_nombre)
                        empleado.roles.add(rol)
                    except Rol.DoesNotExist:
                        print(f"  ⚠ Rol '{rol_nombre}' no encontrado para {empleado.nombre}")
                
                print(f"✓ Empleado '{empleado.nombre} {empleado.apellido}' creado")
            else:
                print(f"- Empleado '{empleado.nombre} {empleado.apellido}' ya existe")

    print("\n🎉 Datos de prueba creados exitosamente!")
    print(f"Total roles: {Rol.objects.count()}")
    print(f"Total empleados: {Empleado.objects.count()}")

if __name__ == '__main__':
    crear_datos_prueba()
