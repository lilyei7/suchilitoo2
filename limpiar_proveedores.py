#!/usr/bin/env python3
"""
Limpiar y crear proveedores con datos correctos
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from dashboard.models import Proveedor

def limpiar_y_crear_proveedores():
    """Limpiar proveedores incorrectos y crear nuevos con datos completos"""
    print("=== LIMPIANDO Y CREANDO PROVEEDORES CORRECTOS ===\n")
    
    # 1. Limpiar proveedores sin nombre o con datos incompletos
    print("1. Limpiando proveedores incorrectos...")
    proveedores_incorrectos = Proveedor.objects.filter(
        models.Q(nombre_comercial="Sin nombre") | 
        models.Q(nombre_comercial="") |
        models.Q(nombre_comercial__isnull=True)
    )
    
    count_eliminados = proveedores_incorrectos.count()
    if count_eliminados > 0:
        proveedores_incorrectos.delete()
        print(f"✓ Eliminados {count_eliminados} proveedores sin nombre")
    else:
        print("✓ No hay proveedores sin nombre para eliminar")
    
    # 2. Crear proveedores con datos completos
    print("\n2. Creando proveedores con datos completos...")
    
    proveedores_ejemplo = [
        {
            'nombre_comercial': 'Mariscos del Pacífico S.A.',
            'razon_social': 'Distribuidora de Mariscos del Pacífico S.A. de C.V.',
            'rfc': 'DMP890123ABC',
            'persona_contacto': 'Juan Carlos Pérez',
            'telefono': '555-0101',
            'email': 'ventas@mariscospacifico.com',
            'direccion': 'Av. Marítima 123, Puerto Principal, CP 12345',
            'categoria_productos': 'ingredientes',
            'estado': 'activo',
            'forma_pago_preferida': 'transferencia',
            'dias_credito': 30
        },
        {
            'nombre_comercial': 'Distribuidora de Arroz Oriental',
            'razon_social': 'Arroz Oriental Distribuciones S.C.',
            'rfc': 'AOD780456DEF',
            'persona_contacto': 'María Elena Rodriguez',
            'telefono': '555-0102',
            'email': 'contacto@arrozoriental.com',
            'direccion': 'Calle del Comercio 456, Centro Histórico, CP 54321',
            'categoria_productos': 'ingredientes',
            'estado': 'activo',
            'forma_pago_preferida': 'credito',
            'dias_credito': 15
        },
        {
            'nombre_comercial': 'Verduras Frescas Premium',
            'razon_social': 'Verduras y Hortalizas Premium S.A.',
            'rfc': 'VHP950789GHI',
            'persona_contacto': 'Carlos Alberto López',
            'telefono': '555-0103',
            'email': 'gerencia@verdurasfrescas.com',
            'direccion': 'Mercado Central Local 789, Zona Norte, CP 67890',
            'categoria_productos': 'ingredientes',
            'estado': 'activo',
            'forma_pago_preferida': 'efectivo',
            'dias_credito': 0
        },
        {
            'nombre_comercial': 'Bebidas Asiáticas Import',
            'razon_social': 'Importadora de Bebidas Asiáticas Ltda.',
            'rfc': 'IBA630147JKL',
            'persona_contacto': 'Ana Sofia Tanaka',
            'telefono': '555-0104',
            'email': 'importaciones@bebidasasiaticas.com',
            'direccion': 'Av. Importadores 321, Zona Industrial, CP 98765',
            'categoria_productos': 'bebidas',
            'estado': 'activo',
            'forma_pago_preferida': 'transferencia',
            'dias_credito': 45
        },
        {
            'nombre_comercial': 'Empaques Sushi Pro',
            'razon_social': 'Empaques Especializados para Sushi S.A.',
            'rfc': 'EPS740258MNO',
            'persona_contacto': 'Roberto Kim',
            'telefono': '555-0105',
            'email': 'ventas@empaques-sushi.com',
            'direccion': 'Parque Industrial 456, Sector B, CP 13579',
            'categoria_productos': 'empaque',
            'estado': 'pendiente',
            'forma_pago_preferida': 'cheque',
            'dias_credito': 20
        }
    ]
    
    for proveedor_data in proveedores_ejemplo:
        proveedor, created = Proveedor.objects.get_or_create(
            nombre_comercial=proveedor_data['nombre_comercial'],
            defaults=proveedor_data
        )
        
        if created:
            print(f"✓ Creado: {proveedor.nombre_comercial}")
            print(f"  - Contacto: {proveedor.persona_contacto}")
            print(f"  - Teléfono: {proveedor.telefono}")
            print(f"  - Estado: {proveedor.estado}")
        else:
            print(f"✓ Ya existe: {proveedor.nombre_comercial}")
    
    # 3. Mostrar resumen final
    print(f"\n3. RESUMEN FINAL:")
    total = Proveedor.objects.count()
    activos = Proveedor.objects.filter(estado='activo').count()
    pendientes = Proveedor.objects.filter(estado='pendiente').count()
    inactivos = Proveedor.objects.filter(estado='inactivo').count()
    
    print(f"   • Total proveedores: {total}")
    print(f"   • Activos: {activos}")
    print(f"   • Pendientes: {pendientes}")
    print(f"   • Inactivos: {inactivos}")
    
    # 4. Mostrar los primeros proveedores para verificar
    print(f"\n4. PRIMEROS PROVEEDORES:")
    for proveedor in Proveedor.objects.all()[:5]:
        print(f"   - {proveedor.nombre_comercial} ({proveedor.estado})")
    
    print(f"\n🌐 ACCESO AL SISTEMA:")
    print(f"   URL: http://127.0.0.1:8001/dashboard/proveedores/")
    print(f"   Usuario: admin_test")
    print(f"   Contraseña: 123456")

if __name__ == '__main__':
    # Importar Q para las consultas
    from django.db import models
    limpiar_y_crear_proveedores()
