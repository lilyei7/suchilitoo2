#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para crear datos iniciales para el sistema de checklist
"""

import os
import sys
import django
import datetime

# Configurar entorno Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from dashboard.models_checklist import ChecklistCategory, ChecklistTask
from accounts.models import Rol

# Crear categorías de checklist
def crear_categorias():
    categorias = [
        {
            'name': 'Limpieza',
            'order': 1
        },
        {
            'name': 'Seguridad',
            'order': 2
        },
        {
            'name': 'Operaciones',
            'order': 3
        },
        {
            'name': 'Inventario',
            'order': 4
        },
        {
            'name': 'Servicio al Cliente',
            'order': 5
        }
    ]
    
    for categoria in categorias:
        ChecklistCategory.objects.get_or_create(
            name=categoria['name'],
            defaults={
                'order': categoria['order'],
                'active': True
            }
        )
    print(f"✅ {len(categorias)} categorías creadas o actualizadas")

# Crear tareas de checklist
def crear_tareas():
    # Obtener roles para asignar
    try:
        rol_admin = Rol.objects.get(nombre='Administrador')
        rol_gerente = Rol.objects.get(nombre='Gerente')
        rol_mesero = Rol.objects.get(nombre='Mesero')
        rol_cocinero = Rol.objects.get(nombre='Cocinero')
        rol_cajero = Rol.objects.get(nombre='Cajero')
    except Rol.DoesNotExist:
        print("⚠ Algunos roles no existen. Usando None para roles faltantes.")
        rol_admin = None
        rol_gerente = None
        rol_mesero = None
        rol_cocinero = None
        rol_cajero = None
        
    # Obtener categorías
    try:
        cat_limpieza = ChecklistCategory.objects.get(name='Limpieza')
        cat_seguridad = ChecklistCategory.objects.get(name='Seguridad')
        cat_operaciones = ChecklistCategory.objects.get(name='Operaciones')
        cat_inventario = ChecklistCategory.objects.get(name='Inventario')
        cat_servicio = ChecklistCategory.objects.get(name='Servicio al Cliente')
    except ChecklistCategory.DoesNotExist:
        print("❌ Error: Primero debe crear las categorías.")
        return

    # Lista de tareas por categoría
    tareas = [
        # Limpieza
        {
            'title': 'Limpiar y desinfectar mesas',
            'description': 'Usar desinfectante aprobado en todas las superficies de mesas y sillas.',
            'requires_evidence': True,
            'category': cat_limpieza,
            'default_role': rol_mesero
        },
        {
            'title': 'Limpiar baños',
            'description': 'Verificar que los baños estén limpios, con papel y jabón. Llenar registro de limpieza.',
            'requires_evidence': True,
            'category': cat_limpieza,
            'default_role': rol_mesero
        },
        {
            'title': 'Limpiar cocina',
            'description': 'Limpiar y desinfectar todas las superficies de cocina, equipos y utensilios.',
            'requires_evidence': True,
            'category': cat_limpieza,
            'default_role': rol_cocinero
        },
        
        # Seguridad
        {
            'title': 'Revisar extintores',
            'description': 'Verificar que todos los extintores estén en su lugar y con presión adecuada.',
            'requires_evidence': True,
            'category': cat_seguridad,
            'default_role': rol_gerente
        },
        {
            'title': 'Revisar salidas de emergencia',
            'description': 'Verificar que las salidas de emergencia estén despejadas y las luces de emergencia funcionen.',
            'requires_evidence': True,
            'category': cat_seguridad,
            'default_role': rol_gerente
        },
        
        # Operaciones
        {
            'title': 'Verificar funcionamiento de POS',
            'description': 'Comprobar que el sistema de punto de venta funcione correctamente.',
            'requires_evidence': False,
            'category': cat_operaciones,
            'default_role': rol_cajero
        },
        {
            'title': 'Revisar menú del día',
            'description': 'Confirmar que todos los platos del menú del día estén disponibles.',
            'requires_evidence': False,
            'category': cat_operaciones,
            'default_role': rol_cocinero
        },
        
        # Inventario
        {
            'title': 'Verificar stock de insumos críticos',
            'description': 'Revisar que los insumos críticos tengan stock suficiente para el día.',
            'requires_evidence': True,
            'category': cat_inventario,
            'default_role': rol_cocinero
        },
        {
            'title': 'Revisar stock de bebidas',
            'description': 'Verificar el inventario de bebidas y solicitar reposición si es necesario.',
            'requires_evidence': False,
            'category': cat_inventario,
            'default_role': rol_cajero
        },
        
        # Servicio al Cliente
        {
            'title': 'Verificar limpieza de uniforme del personal',
            'description': 'Revisar que todo el personal tenga su uniforme limpio y completo.',
            'requires_evidence': False,
            'category': cat_servicio,
            'default_role': rol_gerente
        },
        {
            'title': 'Revisar funcionamiento de WiFi',
            'description': 'Comprobar que el WiFi para clientes funcione correctamente.',
            'requires_evidence': False,
            'category': cat_servicio,
            'default_role': rol_mesero
        }
    ]
    
    count = 0
    for tarea in tareas:
        ChecklistTask.objects.get_or_create(
            title=tarea['title'],
            category=tarea['category'],
            defaults={
                'description': tarea['description'],
                'requires_evidence': tarea['requires_evidence'],
                'default_role': tarea['default_role'],
                'active': True
            }
        )
        count += 1
    
    print(f"✅ {count} tareas creadas o actualizadas")

if __name__ == "__main__":
    print("🚀 Creando datos iniciales para el sistema de checklist...")
    crear_categorias()
    crear_tareas()
    print("✅ Proceso completado.")
