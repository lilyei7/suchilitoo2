#!/usr/bin/env python
"""
Script para crear proveedores de ejemplo para completar el flujo
"""
import os
import sys

# Agregar el directorio del proyecto al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

import django
django.setup()

from restaurant.models import Proveedor, Insumo

def crear_proveedores_ejemplo():
    print("🏭 CREANDO PROVEEDORES DE EJEMPLO")
    print("=" * 50)
    
    proveedores_data = [
        {
            'nombre': 'Verduras Frescas S.A.',
            'ruc': '20123456789',
            'direccion': 'Av. Mercado Central 456, Lima',
            'contacto': 'María González',
            'telefono': '+51 987 654 321',
            'email': 'ventas@verdurasfrescas.com',
            'notas': 'Proveedor especializado en verduras y hortalizas frescas'
        },
        {
            'nombre': 'Distribuidora El Sabor',
            'ruc': '20234567890',
            'direccion': 'Jr. Los Proveedores 123, San Juan de Lurigancho',
            'contacto': 'Carlos Ramírez',
            'telefono': '+51 999 888 777',
            'email': 'carlos@elsabor.com',
            'notas': 'Distribuidor de insumos para restaurantes'
        },
        {
            'nombre': 'Insumos Premium',
            'ruc': '20345678901',
            'direccion': 'Av. Industrial 789, Callao',
            'contacto': 'Ana Torres',
            'telefono': '+51 966 555 444',
            'email': 'info@insumospremium.com',
            'notas': 'Proveedor de insumos de alta calidad'
        }
    ]
    
    proveedores_creados = []
    
    for data in proveedores_data:
        proveedor, created = Proveedor.objects.get_or_create(
            nombre=data['nombre'],
            defaults=data
        )
        
        if created:
            print(f"✅ Creado: {proveedor.nombre}")
        else:
            print(f"ℹ️ Ya existe: {proveedor.nombre}")
        
        proveedores_creados.append(proveedor)
    
    return proveedores_creados

def asignar_proveedores_a_insumos(proveedores):
    print("\n🔗 ASIGNANDO PROVEEDORES A INSUMOS")
    print("=" * 50)
    
    insumos_sin_proveedor = Insumo.objects.filter(activo=True, proveedor_principal__isnull=True)
    
    if not insumos_sin_proveedor:
        print("✅ Todos los insumos ya tienen proveedor asignado")
        return
    
    # Asignar el primer proveedor (Verduras Frescas) al insumo "Pepinos"
    pepinos = Insumo.objects.filter(nombre__icontains='pepino').first()
    if pepinos and proveedores:
        verduras_proveedor = next((p for p in proveedores if 'Verduras' in p.nombre), proveedores[0])
        pepinos.proveedor_principal = verduras_proveedor
        pepinos.save()
        print(f"✅ {pepinos.codigo} - {pepinos.nombre} → {verduras_proveedor.nombre}")
    
    # Asignar otros proveedores a los demás insumos
    for i, insumo in enumerate(insumos_sin_proveedor.exclude(id=pepinos.id if pepinos else 0)):
        proveedor = proveedores[i % len(proveedores)]
        insumo.proveedor_principal = proveedor
        insumo.save()
        print(f"✅ {insumo.codigo} - {insumo.nombre} → {proveedor.nombre}")

def mostrar_resumen_final():
    print("\n📊 RESUMEN FINAL")
    print("=" * 50)
    
    # Proveedores
    total_proveedores = Proveedor.objects.filter(activo=True).count()
    print(f"🏭 Proveedores activos: {total_proveedores}")
    
    # Insumos con proveedor
    insumos_con_proveedor = Insumo.objects.filter(activo=True, proveedor_principal__isnull=False).count()
    total_insumos = Insumo.objects.filter(activo=True).count()
    print(f"📦 Insumos con proveedor: {insumos_con_proveedor}/{total_insumos}")
    
    # Mostrar detalles
    print(f"\n📋 DETALLES:")
    for insumo in Insumo.objects.filter(activo=True):
        proveedor_info = f" → {insumo.proveedor_principal.nombre}" if insumo.proveedor_principal else " → ❌ Sin proveedor"
        print(f"   {insumo.codigo} - {insumo.nombre}{proveedor_info}")

if __name__ == "__main__":
    print("🚀 CONFIGURANDO PROVEEDORES PARA COMPLETAR EL FLUJO\n")
    
    # Crear proveedores
    proveedores = crear_proveedores_ejemplo()
    
    # Asignar a insumos
    asignar_proveedores_a_insumos(proveedores)
    
    # Mostrar resumen
    mostrar_resumen_final()
    
    print("\n✅ CONFIGURACIÓN COMPLETADA")
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Actualizar /dashboard/inventario/ para ver la información del proveedor")
    print("2. Probar el modal 'Ver detalles' de cualquier insumo")
    print("3. El modal ahora debe mostrar:")
    print("   - Nombre del proveedor")
    print("   - Contacto del proveedor")
    print("   - Teléfono del proveedor")
    print("   - Email del proveedor")
