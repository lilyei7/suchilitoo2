#!/usr/bin/env python
"""
Script simple para verificar productos y crear uno activo para pruebas
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta, CategoriaProducto
from decimal import Decimal

def verificar_y_crear_productos():
    print("=" * 60)
    print("VERIFICACIÓN DE PRODUCTOS PARA PRUEBA")
    print("=" * 60)
    
    # 1. Verificar productos existentes
    productos = ProductoVenta.objects.all()
    print(f"Total productos: {productos.count()}")
    
    for producto in productos:
        estado = "ACTIVO" if producto.disponible else "INACTIVO"
        print(f"- {producto.nombre} ({estado})")
    
    # 2. Asegurar que tengamos al menos un producto activo y uno inactivo
    activos = productos.filter(disponible=True).count()
    inactivos = productos.filter(disponible=False).count()
    
    print(f"\nEstado actual:")
    print(f"- Productos activos: {activos}")
    print(f"- Productos inactivos: {inactivos}")
    
    # 3. Crear productos de ejemplo si es necesario
    if activos == 0:
        print("\n🔧 Creando producto ACTIVO de ejemplo...")
        
        # Obtener o crear categoría
        categoria, created = CategoriaProducto.objects.get_or_create(
            nombre="Sushi",
            defaults={'descripcion': 'Productos de sushi', 'activo': True}
        )
        
        # Crear producto activo
        producto_activo, created = ProductoVenta.objects.get_or_create(
            codigo="SUSHI001",
            defaults={
                'nombre': 'California Roll',
                'descripcion': 'Delicioso California Roll con aguacate y cangrejo',
                'precio': Decimal('15.99'),
                'costo': Decimal('8.50'),
                'disponible': True,  # ACTIVO
                'categoria': categoria,
                'tipo': 'plato',
                'calorias': 250
            }
        )
        
        if created:
            print(f"✅ Producto ACTIVO creado: {producto_activo.nombre}")
        else:
            # Si ya existe, asegurar que esté activo
            producto_activo.disponible = True
            producto_activo.save()
            print(f"✅ Producto existente activado: {producto_activo.nombre}")
    
    if inactivos == 0:
        print("\n🔧 Asegurando que hay un producto INACTIVO...")
        
        # Si solo hay el producto "rollosake", mantenerlo inactivo
        if productos.filter(nombre="rollosake").exists():
            print("✅ Ya existe producto INACTIVO: rollosake")
        else:
            # Crear otro producto inactivo
            categoria, _ = CategoriaProducto.objects.get_or_create(
                nombre="Bebidas",
                defaults={'descripcion': 'Bebidas y refrescos', 'activo': True}
            )
            
            producto_inactivo, created = ProductoVenta.objects.get_or_create(
                codigo="BEB001",
                defaults={
                    'nombre': 'Té Verde',
                    'descripcion': 'Té verde tradicional japonés',
                    'precio': Decimal('5.99'),
                    'costo': Decimal('2.50'),
                    'disponible': False,  # INACTIVO
                    'categoria': categoria,
                    'tipo': 'bebida',
                    'calorias': 0
                }
            )
            
            if created:
                print(f"✅ Producto INACTIVO creado: {producto_inactivo.nombre}")
    
    # 4. Mostrar resultado final
    print("\n" + "=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)
    
    productos_final = ProductoVenta.objects.all().order_by('nombre')
    activos_final = productos_final.filter(disponible=True).count()
    inactivos_final = productos_final.filter(disponible=False).count()
    
    print(f"Total productos: {productos_final.count()}")
    print(f"- Activos: {activos_final}")
    print(f"- Inactivos: {inactivos_final}")
    
    print(f"\nListado completo:")
    for producto in productos_final:
        estado = "ACTIVO" if producto.disponible else "INACTIVO"
        print(f"- {producto.nombre} ({estado})")
    
    print(f"\n✅ AHORA puedes ir a: http://127.0.0.1:8000/dashboard/productos-venta/")
    print(f"   Deberías ver {productos_final.count()} productos:")
    print(f"   - {activos_final} con etiqueta ACTIVO (verde)")
    print(f"   - {inactivos_final} con etiqueta INACTIVO (roja)")

if __name__ == "__main__":
    verificar_y_crear_productos()
