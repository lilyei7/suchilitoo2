#!/usr/bin/env python
"""
Script simplificado para investigar la relación ProductoVenta-Receta
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

from restaurant.models import ProductoVenta, Receta, Insumo, RecetaInsumo

def main():
    print("🔍 INVESTIGACIÓN SIMPLE: PRODUCTOS Y RECETAS")
    print("=" * 60)
    
    # 1. Verificar la relación OneToOne vs ForeignKey
    print("\n1️⃣ VERIFICANDO MODELO DE RELACIÓN")
    print("-" * 40)
    
    # Revisar campos del modelo Receta
    print("Campos del modelo Receta:")
    for field in Receta._meta.fields:
        if hasattr(field, 'related_model') and field.related_model == ProductoVenta:
            print(f"  • {field.name}: {type(field).__name__}")
    
    # 2. Contar productos y recetas
    print("\n2️⃣ CONTADORES BÁSICOS")
    print("-" * 40)
    total_productos = ProductoVenta.objects.count()
    total_recetas = Receta.objects.count()
    recetas_con_producto = Receta.objects.filter(producto__isnull=False).count()
    recetas_huerfanas = Receta.objects.filter(producto__isnull=True).count()
    
    print(f"Total productos: {total_productos}")
    print(f"Total recetas: {total_recetas}")
    print(f"Recetas con producto: {recetas_con_producto}")
    print(f"Recetas huérfanas: {recetas_huerfanas}")
    
    # 3. Casos específicos mencionados
    print("\n3️⃣ CASOS ESPECÍFICOS")
    print("-" * 40)
    
    casos = ["algas con nalgas", "algas alas algas con algas"]
    
    for caso in casos:
        print(f"\n🔍 Buscando: '{caso}'")
        
        # Buscar producto
        productos = ProductoVenta.objects.filter(nombre__icontains=caso)
        
        if not productos.exists():
            print(f"   ❌ No se encontró producto con '{caso}'")
            continue
            
        for producto in productos:
            print(f"   ✅ Producto: {producto.nombre} (ID: {producto.id})")
            
            # Buscar receta usando reverse lookup
            try:
                receta = producto.receta  # OneToOne reverse lookup
                print(f"      ✅ Tiene receta: ID {receta.id}")
                
                # Contar insumos
                insumos_count = RecetaInsumo.objects.filter(receta=receta).count()
                print(f"      📝 Insumos en receta: {insumos_count}")
                
            except Receta.DoesNotExist:
                print(f"      ❌ NO tiene receta")
    
    # 4. Buscar violaciones de OneToOne (si las hay)
    print("\n4️⃣ VERIFICANDO VIOLACIONES DE ONETOONE")
    print("-" * 40)
    
    # Agrupar por producto_id para ver si hay duplicados
    from django.db.models import Count
    
    duplicados = Receta.objects.values('producto_id').annotate(
        count=Count('producto_id')
    ).filter(count__gt=1, producto_id__isnull=False)
    
    if duplicados.exists():
        print("⚠️ ENCONTRADAS VIOLACIONES DE ONETOONE:")
        for dup in duplicados:
            producto_id = dup['producto_id']
            count = dup['count']
            producto = ProductoVenta.objects.get(id=producto_id)
            print(f"   • Producto: {producto.nombre} (ID: {producto_id}) tiene {count} recetas")
            
            # Mostrar las recetas duplicadas
            recetas = Receta.objects.filter(producto_id=producto_id)
            for i, receta in enumerate(recetas, 1):
                print(f"     - Receta {i}: ID {receta.id}")
    else:
        print("✅ No hay violaciones de OneToOne")
    
    # 5. Productos sin recetas
    print("\n5️⃣ PRODUCTOS SIN RECETAS")
    print("-" * 40)
    
    productos_sin_receta = ProductoVenta.objects.filter(receta__isnull=True)
    print(f"Total: {productos_sin_receta.count()}")
    
    if productos_sin_receta.count() <= 10:
        for producto in productos_sin_receta:
            print(f"   • {producto.nombre} (ID: {producto.id})")
    else:
        print("   (Lista muy larga, mostrando solo los primeros 10)")
        for producto in productos_sin_receta[:10]:
            print(f"   • {producto.nombre} (ID: {producto.id})")
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSIÓN:")
    if duplicados.exists():
        print("• ⚠️ HAY PRODUCTOS CON MÚLTIPLES RECETAS (violando OneToOne)")
        print("• Esto explica el problema con la deducción de inventario")
        print("• Necesitamos decidir qué receta usar cuando hay múltiples")
    else:
        print("• ✅ La relación OneToOne se respeta")
        print("• El problema es que algunos productos NO tienen receta")
        print("• Necesitamos crear recetas para productos sin ellas")

if __name__ == "__main__":
    main()
