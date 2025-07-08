#!/usr/bin/env python
"""
Script para verificar y gestionar proveedores de insumos
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suchilitoo.settings')
django.setup()

from restaurant.models import Insumo, Proveedor

def verificar_proveedores():
    """Verificar el estado de los proveedores en el sistema"""
    
    print("=== VERIFICACIÓN DE PROVEEDORES ===")
    
    # Contar proveedores
    total_proveedores = Proveedor.objects.count()
    proveedores_activos = Proveedor.objects.filter(activo=True).count()
    
    print(f"Total de proveedores: {total_proveedores}")
    print(f"Proveedores activos: {proveedores_activos}")
    
    # Verificar insumos con proveedor
    insumos_con_proveedor = Insumo.objects.filter(proveedor_principal__isnull=False).count()
    insumos_sin_proveedor = Insumo.objects.filter(proveedor_principal__isnull=True).count()
    total_insumos = Insumo.objects.count()
    
    print(f"\nINSUMOS:")
    print(f"Total de insumos: {total_insumos}")
    print(f"Insumos con proveedor: {insumos_con_proveedor}")
    print(f"Insumos sin proveedor: {insumos_sin_proveedor}")
    
    # Mostrar proveedores existentes
    if total_proveedores > 0:
        print(f"\n=== PROVEEDORES EXISTENTES ===")
        for proveedor in Proveedor.objects.all():
            insumos_asignados = proveedor.insumos_proveidos.count()
            print(f"- {proveedor.nombre} ({'Activo' if proveedor.activo else 'Inactivo'})")
            print(f"  Insumos asignados: {insumos_asignados}")
            if proveedor.contacto:
                print(f"  Contacto: {proveedor.contacto}")
            if proveedor.telefono:
                print(f"  Teléfono: {proveedor.telefono}")
            if proveedor.email:
                print(f"  Email: {proveedor.email}")
            print()
    
    # Mostrar algunos insumos sin proveedor
    if insumos_sin_proveedor > 0:
        print(f"\n=== INSUMOS SIN PROVEEDOR (primeros 10) ===")
        for insumo in Insumo.objects.filter(proveedor_principal__isnull=True)[:10]:
            print(f"- {insumo.codigo}: {insumo.nombre} ({insumo.get_tipo_display()})")

def crear_proveedores_ejemplo():
    """Crear algunos proveedores de ejemplo si no existen"""
    
    proveedores_ejemplo = [
        {
            'nombre': 'Distribuidora MarCorp',
            'ruc': '20123456789',
            'direccion': 'Av. Industrial 123, Lima',
            'contacto': 'Carlos Martínez',
            'telefono': '01-234-5678',
            'email': 'ventas@marcorp.com',
            'notas': 'Proveedor principal de pescados y mariscos'
        },
        {
            'nombre': 'Agrícola del Valle',
            'ruc': '20987654321',
            'direccion': 'Carretera Central Km 25, Huachipa',
            'contacto': 'María González',
            'telefono': '01-987-6543',
            'email': 'pedidos@agricoladelvalle.pe',
            'notas': 'Especializado en vegetales frescos y hortalizas'
        },
        {
            'nombre': 'Comercial Nikkei SAC',
            'ruc': '20456789123',
            'direccion': 'Jr. Ucayali 456, Centro de Lima',
            'contacto': 'Akira Tanaka',
            'telefono': '01-456-7890',
            'email': 'info@comercialnikkei.com',
            'notas': 'Importador de ingredientes japoneses y asiáticos'
        },
        {
            'nombre': 'Envases y Empaques del Perú',
            'ruc': '20789123456',
            'direccion': 'Av. Argentina 789, Callao',
            'contacto': 'Roberto Silva',
            'telefono': '01-789-0123',
            'email': 'ventas@envasesperu.com',
            'notas': 'Proveedor de envases, empaques y materiales de cocina'
        }
    ]
    
    print("\n=== CREANDO PROVEEDORES DE EJEMPLO ===")
    
    for proveedor_data in proveedores_ejemplo:
        proveedor, created = Proveedor.objects.get_or_create(
            nombre=proveedor_data['nombre'],
            defaults=proveedor_data
        )
        
        if created:
            print(f"✅ Creado: {proveedor.nombre}")
        else:
            print(f"⚠️ Ya existe: {proveedor.nombre}")

def asignar_proveedores_inteligente():
    """Asignar proveedores a insumos basado en el tipo y nombre"""
    
    print("\n=== ASIGNACIÓN INTELIGENTE DE PROVEEDORES ===")
    
    # Obtener proveedores
    try:
        marcorp = Proveedor.objects.get(nombre__icontains='MarCorp')
        agricola = Proveedor.objects.get(nombre__icontains='Agrícola')
        nikkei = Proveedor.objects.get(nombre__icontains='Nikkei')
        envases = Proveedor.objects.get(nombre__icontains='Envases')
    except Proveedor.DoesNotExist:
        print("❌ Primero debe crear los proveedores de ejemplo")
        return
    
    asignaciones = 0
    
    # Asignar según categorías y nombres de insumos
    for insumo in Insumo.objects.filter(proveedor_principal__isnull=True):
        proveedor_asignado = None
        
        # Reglas de asignación basadas en nombre y categoría
        nombre_lower = insumo.nombre.lower()
        categoria_lower = insumo.categoria.nombre.lower() if insumo.categoria else ''
        
        if any(palabra in nombre_lower for palabra in ['pescado', 'salmón', 'atún', 'marisco', 'camarón', 'langostino']):
            proveedor_asignado = marcorp
        elif any(palabra in nombre_lower for palabra in ['verdura', 'vegetal', 'lechuga', 'tomate', 'cebolla', 'apio', 'pepino']):
            proveedor_asignado = agricola
        elif any(palabra in nombre_lower for palabra in ['nori', 'wasabi', 'soja', 'miso', 'sake', 'mirin', 'shoyu']):
            proveedor_asignado = nikkei
        elif any(palabra in nombre_lower for palabra in ['envase', 'recipiente', 'bandeja', 'bolsa', 'contenedor']):
            proveedor_asignado = envases
        elif any(palabra in categoria_lower for palabra in ['pescado', 'marisco']):
            proveedor_asignado = marcorp
        elif any(palabra in categoria_lower for palabra in ['vegetal', 'verdura']):
            proveedor_asignado = agricola
        elif any(palabra in categoria_lower for palabra in ['asiático', 'japonés']):
            proveedor_asignado = nikkei
        elif any(palabra in categoria_lower for palabra in ['empaque', 'envase']):
            proveedor_asignado = envases
        
        if proveedor_asignado:
            insumo.proveedor_principal = proveedor_asignado
            insumo.save()
            asignaciones += 1
            print(f"✅ {insumo.nombre} → {proveedor_asignado.nombre}")
    
    print(f"\n✅ Total de asignaciones realizadas: {asignaciones}")

def mostrar_estadisticas_finales():
    """Mostrar estadísticas finales después de las asignaciones"""
    
    print("\n=== ESTADÍSTICAS FINALES ===")
    
    for proveedor in Proveedor.objects.filter(activo=True):
        count = proveedor.insumos_proveidos.count()
        print(f"📦 {proveedor.nombre}: {count} insumos asignados")
    
    insumos_sin_proveedor = Insumo.objects.filter(proveedor_principal__isnull=True).count()
    print(f"\n⚠️ Insumos sin proveedor: {insumos_sin_proveedor}")

if __name__ == "__main__":
    verificar_proveedores()
    
    # Preguntar si crear proveedores de ejemplo
    if Proveedor.objects.count() == 0:
        print("\n💡 No hay proveedores en el sistema.")
        respuesta = input("¿Desea crear proveedores de ejemplo? (s/N): ")
        if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            crear_proveedores_ejemplo()
            asignar_proveedores_inteligente()
            mostrar_estadisticas_finales()
    else:
        respuesta = input("\n¿Desea asignar proveedores automáticamente a insumos sin proveedor? (s/N): ")
        if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            asignar_proveedores_inteligente()
            mostrar_estadisticas_finales()
