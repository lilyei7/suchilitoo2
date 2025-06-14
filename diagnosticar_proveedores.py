#!/usr/bin/env python3
"""
Diagnosticar problema con proveedores
Verificar datos en base de datos y configuración de la vista
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def diagnosticar_proveedores():
    """Diagnosticar el problema con proveedores"""
    print("=== DIAGNÓSTICO DE PROVEEDORES ===\n")
    
    # 1. Verificar datos en restaurant.models.Proveedor
    print("1. Verificando proveedores en restaurant.models...")
    try:
        from restaurant.models import Proveedor as RestaurantProveedor
        restaurant_proveedores = RestaurantProveedor.objects.all()
        print(f"   ✓ Proveedores en restaurant.models: {restaurant_proveedores.count()}")
        
        for proveedor in restaurant_proveedores[:5]:
            print(f"     - {proveedor.nombre} ({proveedor.contacto})")
            
    except Exception as e:
        print(f"   ❌ Error en restaurant.models.Proveedor: {e}")
    
    # 2. Verificar datos en dashboard.models.Proveedor
    print("\n2. Verificando proveedores en dashboard.models...")
    try:
        from dashboard.models import Proveedor as DashboardProveedor
        dashboard_proveedores = DashboardProveedor.objects.all()
        print(f"   ✓ Proveedores en dashboard.models: {dashboard_proveedores.count()}")
        
        for proveedor in dashboard_proveedores[:5]:
            print(f"     - {proveedor.nombre} ({proveedor.contacto})")
            
    except Exception as e:
        print(f"   ❌ Error en dashboard.models.Proveedor: {e}")
    
    # 3. Verificar la vista actual
    print("\n3. Verificando vista de proveedores...")
    from dashboard.views import proveedores_view
    print(f"   ✓ Vista proveedores_view existe")
    
    # 4. Verificar template
    print("\n4. Verificando template de proveedores...")
    template_path = "dashboard/templates/dashboard/proveedores.html"
    if os.path.exists(template_path):
        print(f"   ✓ Template existe: {template_path}")
        
        # Verificar contenido del template
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'proveedores' in content:
            print("   ✓ Template hace referencia a 'proveedores'")
        else:
            print("   ⚠ Template no hace referencia a 'proveedores'")
            
        if 'for proveedor in' in content:
            print("   ✓ Template tiene loop de proveedores")
        else:
            print("   ⚠ Template no tiene loop de proveedores")
            
    else:
        print(f"   ❌ Template no existe: {template_path}")
    
    # 5. Crear algunos proveedores de prueba si no existen
    print("\n5. Creando proveedores de prueba...")
    
    # Decidir qué modelo usar basado en la vista
    try:
        from dashboard.models import Proveedor
        modelo_a_usar = "dashboard.models"
    except:
        from restaurant.models import Proveedor
        modelo_a_usar = "restaurant.models"
    
    print(f"   ℹ Usando modelo: {modelo_a_usar}")
    
    # Crear proveedores de ejemplo
    proveedores_ejemplo = [
        {
            'nombre': 'Mariscos del Pacífico',
            'contacto': 'Juan Pérez',
            'telefono': '555-0101',
            'email': 'contacto@mariscospacifico.com',
            'direccion': 'Av. Marítima 123, Puerto Principal'
        },
        {
            'nombre': 'Distribuidora de Arroz Oriental',
            'contacto': 'María Rodriguez',
            'telefono': '555-0102',
            'email': 'ventas@arrozoriental.com',
            'direccion': 'Calle del Comercio 456, Centro'
        },
        {
            'nombre': 'Verduras Frescas Ltda',
            'contacto': 'Carlos López',
            'telefono': '555-0103',
            'email': 'info@verdurasfrescas.com',
            'direccion': 'Mercado Central Local 789'
        }
    ]
    
    for proveedor_data in proveedores_ejemplo:
        proveedor, created = Proveedor.objects.get_or_create(
            nombre=proveedor_data['nombre'],
            defaults=proveedor_data
        )
        
        if created:
            print(f"   ✓ Creado: {proveedor.nombre}")
        else:
            print(f"   ✓ Ya existe: {proveedor.nombre}")
    
    # 6. Resumen final
    print(f"\n6. RESUMEN:")
    total_proveedores = Proveedor.objects.count()
    print(f"   ✓ Total proveedores en BD: {total_proveedores}")
    print(f"   ✓ Modelo utilizado: {Proveedor._meta.app_label}.{Proveedor._meta.model_name}")
    
    return total_proveedores > 0

if __name__ == '__main__':
    resultado = diagnosticar_proveedores()
    
    if resultado:
        print("\n🎯 DIAGNÓSTICO COMPLETADO")
        print("✅ Hay datos de proveedores en la base de datos")
        print("📋 Próximos pasos:")
        print("   1. Verificar la vista proveedores_view")
        print("   2. Verificar el template proveedores.html")
        print("   3. Verificar que el contexto se pase correctamente")
    else:
        print("\n❌ No hay datos de proveedores")
        print("📋 Se han creado proveedores de ejemplo")
