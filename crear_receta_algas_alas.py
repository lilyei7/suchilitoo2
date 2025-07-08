#!/usr/bin/env python
"""
Script para crear una receta para "algas alas algas con algas"
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

def crear_receta_algas_alas():
    """Crear receta para 'algas alas algas con algas'"""
    print("🔧 CREANDO RECETA PARA 'algas alas algas con algas'")
    print("=" * 60)
    
    # 1. Buscar el producto
    try:
        producto = ProductoVenta.objects.get(nombre="algas alas algas con algas")
        print(f"✅ Producto encontrado: {producto.nombre} (ID: {producto.id})")
    except ProductoVenta.DoesNotExist:
        print("❌ Producto 'algas alas algas con algas' no encontrado")
        return False
    
    # 2. Verificar si ya tiene receta
    try:
        receta_existente = producto.receta
        print(f"⚠️ El producto ya tiene una receta (ID: {receta_existente.id})")
        return False
    except Receta.DoesNotExist:
        print("✅ El producto no tiene receta, procediendo a crear una")
    
    # 3. Buscar el insumo "alga nori"
    try:
        alga_nori = Insumo.objects.get(nombre__icontains="alga nori")
        print(f"✅ Insumo encontrado: {alga_nori.nombre} (ID: {alga_nori.id})")
    except Insumo.DoesNotExist:
        print("❌ Insumo 'alga nori' no encontrado")
        return False
    except Insumo.MultipleObjectsReturned:
        alga_nori = Insumo.objects.filter(nombre__icontains="alga nori").first()
        print(f"⚠️ Múltiples insumos encontrados, usando: {alga_nori.nombre} (ID: {alga_nori.id})")
    
    # 4. Crear la receta
    print("\n📝 Creando receta...")
    
    receta = Receta.objects.create(
        producto=producto,
        tiempo_preparacion=15,  # 15 minutos
        porciones=1,
        instrucciones="1. Preparar el alga nori\n2. Servir con acompañamientos",
        notas="Receta generada automáticamente para permitir la venta del producto",
        activo=True
    )
    
    print(f"✅ Receta creada con ID: {receta.id}")
    
    # 5. Agregar el insumo alga nori a la receta
    print("\n🥬 Agregando insumo alga nori...")
    
    # Usar una cantidad similar a "algas con nalgas" (80 pz)
    receta_insumo = RecetaInsumo.objects.create(
        receta=receta,
        insumo=alga_nori,
        cantidad=60  # Un poco menos que "algas con nalgas"
    )
    
    print(f"✅ Insumo agregado: {receta_insumo.cantidad} {alga_nori.unidad_medida} de {alga_nori.nombre}")
    
    print("\n" + "=" * 60)
    print("🎉 RECETA CREADA EXITOSAMENTE")
    print(f"• Producto: {producto.nombre}")
    print(f"• Receta ID: {receta.id}")
    print(f"• Insumo: {receta_insumo.cantidad} {alga_nori.unidad_medida} de {alga_nori.nombre}")
    print("\n💡 Ahora el producto debería poder ordenarse correctamente")
    
    return True

def main():
    success = crear_receta_algas_alas()
    
    if success:
        print("\n🧪 VERIFICANDO LA CREACIÓN...")
        
        # Verificar que se creó correctamente
        try:
            producto = ProductoVenta.objects.get(nombre="algas alas algas con algas")
            receta = producto.receta
            insumos = RecetaInsumo.objects.filter(receta=receta)
            
            print(f"✅ Verificación exitosa:")
            print(f"   • Producto: {producto.nombre}")
            print(f"   • Receta: ID {receta.id}")
            print(f"   • Insumos: {insumos.count()}")
            
            for ri in insumos:
                print(f"     - {ri.cantidad} {ri.insumo.unidad_medida} de {ri.insumo.nombre}")
                
        except Exception as e:
            print(f"❌ Error en verificación: {e}")

if __name__ == "__main__":
    main()
