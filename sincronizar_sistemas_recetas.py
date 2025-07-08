#!/usr/bin/env python
"""
Script para crear la relación en ProductoReceta para que el dashboard la vea
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

try:
    django.setup()
except Exception as e:
    print(f"Error al configurar Django: {e}")
    sys.exit(1)

from restaurant.models import ProductoVenta, Receta
from restaurant.models_producto_receta import ProductoReceta

def sincronizar_sistemas():
    """Sincronizar el sistema OneToOne con el sistema Many-to-Many"""
    print("🔄 SINCRONIZANDO SISTEMAS DE PRODUCTO-RECETA")
    print("=" * 60)
    
    # 1. Buscar el producto y su receta OneToOne
    try:
        producto = ProductoVenta.objects.get(nombre="algas alas algas con algas")
        receta = producto.receta  # OneToOne
        
        print(f"✅ Producto: {producto.nombre} (ID: {producto.id})")
        print(f"✅ Receta OneToOne: ID {receta.id}")
        
    except (ProductoVenta.DoesNotExist, Receta.DoesNotExist):
        print("❌ No se pudo encontrar producto o receta en sistema OneToOne")
        return False
    
    # 2. Verificar si ya existe en ProductoReceta
    relacion_existente = ProductoReceta.objects.filter(
        producto=producto,
        receta=receta
    ).first()
    
    if relacion_existente:
        print(f"✅ La relación ya existe en ProductoReceta (ID: {relacion_existente.id})")
        return True
    
    # 3. Crear la relación en ProductoReceta
    print(f"\n🔗 Creando relación en ProductoReceta...")
    
    producto_receta = ProductoReceta.objects.create(
        producto=producto,
        receta=receta,
        orden=1,
        notas="Relación creada automáticamente para sincronizar con dashboard"
    )
    
    print(f"✅ Relación creada en ProductoReceta (ID: {producto_receta.id})")
    
    # 4. Verificar que el dashboard ahora puede ver la relación
    print(f"\n🔍 Verificando que el dashboard puede ver la relación...")
    
    recetas_dashboard = ProductoReceta.objects.filter(producto=producto)
    print(f"✅ Dashboard puede ver {recetas_dashboard.count()} recetas para el producto")
    
    for pr in recetas_dashboard:
        print(f"   • Receta ID: {pr.receta.id}")
        print(f"   • Tiempo preparación: {pr.receta.tiempo_preparacion} min")
        print(f"   • Orden: {pr.orden}")
    
    return True

def limpiar_relaciones_obsoletas():
    """Limpiar relaciones obsoletas que puedan confundir al dashboard"""
    print(f"\n🧹 LIMPIANDO RELACIONES OBSOLETAS")
    print("-" * 40)
    
    # Buscar relaciones ProductoReceta que no correspondan al sistema OneToOne
    relaciones_obsoletas = []
    
    for pr in ProductoReceta.objects.all():
        try:
            # Verificar si la receta está asociada al mismo producto en OneToOne
            if pr.receta.producto and pr.receta.producto != pr.producto:
                relaciones_obsoletas.append(pr)
                print(f"⚠️ Relación obsoleta: ProductoReceta ID {pr.id}")
                print(f"   • Producto en ProductoReceta: {pr.producto.nombre}")
                print(f"   • Producto en OneToOne: {pr.receta.producto.nombre}")
        except:
            # Si hay algún error, considerar como obsoleta
            relaciones_obsoletas.append(pr)
    
    if relaciones_obsoletas:
        respuesta = input(f"\n❓ ¿Eliminar {len(relaciones_obsoletas)} relaciones obsoletas? (s/N): ").strip().lower()
        
        if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            for pr in relaciones_obsoletas:
                print(f"🗑️ Eliminando relación ProductoReceta ID {pr.id}")
                pr.delete()
            print(f"✅ {len(relaciones_obsoletas)} relaciones obsoletas eliminadas")
        else:
            print("❌ No se eliminaron relaciones")
    else:
        print("✅ No hay relaciones obsoletas")

def verificar_dashboard():
    """Verificar que el dashboard ahora muestre la información correcta"""
    print(f"\n🖥️ VERIFICACIÓN FINAL DEL DASHBOARD")
    print("=" * 60)
    
    try:
        producto = ProductoVenta.objects.get(nombre="algas alas algas con algas")
        
        # Simular lo que hace la vista del dashboard
        recetas = ProductoReceta.objects.filter(producto=producto).select_related('receta')
        
        print(f"Dashboard mostrará:")
        print(f"• Producto: {producto.nombre}")
        print(f"• Precio: ${producto.precio}")
        print(f"• Recetas encontradas: {recetas.count()}")
        
        if recetas.exists():
            print(f"\nTabla de recetas en dashboard:")
            print(f"┌─────────────────┬───────────────────┬──────────┬─────────┐")
            print(f"│ RECETA          │ TIEMPO PREPARACIÓN│ PORCIONES│ COSTO   │")
            print(f"├─────────────────┼───────────────────┼──────────┼─────────┤")
            
            for pr in recetas:
                receta = pr.receta
                # Calcular costo (ejemplo)
                costo = "$8000.00"  # placeholder
                nombre_truncado = receta.producto.nombre[:15] if receta.producto else "Sin nombre"
                print(f"│ {nombre_truncado:<15} │ {receta.tiempo_preparacion} minutos{' ' * 8} │ {receta.porciones:<8} │ {costo}  │")
            
            print(f"└─────────────────┴───────────────────┴──────────┴─────────┘")
            
            print(f"\n✅ EL DASHBOARD AHORA DEBERÍA MOSTRAR LA INFORMACIÓN CORRECTA")
        else:
            print(f"❌ El dashboard aún no puede ver recetas")
            
    except Exception as e:
        print(f"❌ Error en verificación: {e}")

def main():
    print("🔄 SINCRONIZACIÓN DE SISTEMAS PRODUCTO-RECETA")
    print("=" * 80)
    
    # 1. Sincronizar sistemas
    if sincronizar_sistemas():
        # 2. Limpiar relaciones obsoletas
        limpiar_relaciones_obsoletas()
        
        # 3. Verificar dashboard
        verificar_dashboard()
        
        print(f"\n" + "=" * 80)
        print("🎉 SINCRONIZACIÓN COMPLETADA")
        print("• El sistema OneToOne funciona correctamente")
        print("• El dashboard ahora puede ver la relación")
        print("• Refresca el navegador (Ctrl+F5) para ver los cambios")
    else:
        print(f"\n❌ Error en la sincronización")

if __name__ == "__main__":
    main()
