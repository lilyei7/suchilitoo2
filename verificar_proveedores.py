#!/usr/bin/env python3
"""
Script para verificar y crear datos de prueba para proveedores
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from dashboard.models import Proveedor

def main():
    print("🔍 Verificando proveedores existentes...")
    
    proveedores = Proveedor.objects.all()
    print(f"✅ Total de proveedores encontrados: {proveedores.count()}")
    
    for proveedor in proveedores:
        print(f"  - ID: {proveedor.id}, Nombre: {proveedor.nombre_comercial}, Estado: {proveedor.estado}")
    
    if proveedores.count() == 0:
        print("\n📦 Creando proveedores de prueba...")
        
        # Crear proveedores de ejemplo
        proveedores_ejemplo = [
            {
                'nombre_comercial': 'Mariscos del Pacífico',
                'razon_social': 'Distribuidora de Mariscos del Pacífico S.A. de C.V.',
                'rfc': 'DMP890123ABC',
                'persona_contacto': 'María González',
                'telefono': '555-0123',
                'email': 'ventas@mariscospacifico.com',
                'direccion': 'Av. Costa 123, Col. Puerto',
                'ciudad_estado': 'Mazatlán, Sinaloa',
                'categoria_productos': 'ingredientes',
                'forma_pago_preferida': 'transferencia',
                'dias_credito': 15,
                'estado': 'activo',
                'notas_adicionales': 'Especialista en pescado fresco y mariscos de alta calidad'
            },
            {
                'nombre_comercial': 'Verduras Orgánicas del Valle',
                'razon_social': 'Verduras Orgánicas del Valle S.A.',
                'rfc': 'VOV780456DEF',
                'persona_contacto': 'Carlos Hernández',
                'telefono': '555-0456',
                'email': 'pedidos@verdurasorganicas.com',
                'direccion': 'Carretera Nacional Km 45',
                'ciudad_estado': 'Valle de Bravo, Estado de México',
                'categoria_productos': 'ingredientes',
                'forma_pago_preferida': 'credito',
                'dias_credito': 30,
                'estado': 'activo',
                'notas_adicionales': 'Productos orgánicos certificados, entrega diaria'
            },
            {
                'nombre_comercial': 'Bebidas y Refrescos SA',
                'razon_social': 'Distribuidora de Bebidas y Refrescos S.A. de C.V.',
                'rfc': 'DBR670789GHI',
                'persona_contacto': 'Ana Martínez',
                'telefono': '555-0789',
                'email': 'contacto@bebidasrefrescos.com',
                'direccion': 'Blvd. Industrial 789',
                'ciudad_estado': 'Guadalajara, Jalisco',
                'categoria_productos': 'bebidas',
                'forma_pago_preferida': 'transferencia',
                'dias_credito': 21,
                'estado': 'activo',
                'notas_adicionales': 'Distribuidor autorizado de las principales marcas'
            },
            {
                'nombre_comercial': 'Equipos de Cocina Pro',
                'razon_social': 'Equipos Profesionales de Cocina S.A.',
                'rfc': 'EPC560321JKL',
                'persona_contacto': 'Roberto Silva',
                'telefono': '555-0321',
                'email': 'ventas@equiposcocina.com',
                'direccion': 'Zona Industrial Norte 456',
                'ciudad_estado': 'Monterrey, Nuevo León',
                'categoria_productos': 'equipos',
                'forma_pago_preferida': 'cheque',
                'dias_credito': 45,
                'estado': 'inactivo',
                'notas_adicionales': 'Especialista en equipos profesionales de cocina y refrigeración'
            }
        ]
        
        for datos in proveedores_ejemplo:
            proveedor = Proveedor.objects.create(**datos)
            print(f"  ✅ Creado: {proveedor.nombre_comercial} (ID: {proveedor.id})")
        
        print(f"\n🎉 Se crearon {len(proveedores_ejemplo)} proveedores de prueba")
    
    print(f"\n📊 Estado final:")
    print(f"  - Total proveedores: {Proveedor.objects.count()}")
    print(f"  - Proveedores activos: {Proveedor.objects.filter(estado='activo').count()}")
    print(f"  - Proveedores inactivos: {Proveedor.objects.filter(estado='inactivo').count()}")

if __name__ == '__main__':
    main()
