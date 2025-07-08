#!/usr/bin/env python
"""
Script para investigar los productos con algas y sus recetas
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

def main():
    print("🔍 INVESTIGANDO PRODUCTOS CON ALGAS Y SUS RECETAS")
    print("=" * 60)
    
    # Buscar todos los productos que contengan "algas"
    productos = ProductoVenta.objects.filter(nombre__icontains='algas').order_by('id')
    
    print(f"📱 Productos encontrados: {productos.count()}")
    
    for producto in productos:
        print(f"\n🍱 Producto ID {producto.id}: '{producto.nombre}'")
        print(f"   📊 Disponible: {producto.disponible}")
        print(f"   💰 Precio: ${producto.precio}")
        
        # Verificar si tiene receta
        try:
            receta = producto.receta
            print(f"   ✅ Receta: SÍ (ID: {receta.id})")
            
            # Mostrar insumos de la receta
            insumos = receta.insumos_receta.all()
            if insumos:
                print(f"   📋 Insumos ({insumos.count()}):")
                for insumo_receta in insumos:
                    print(f"      • {insumo_receta.insumo.nombre}: {insumo_receta.cantidad} {insumo_receta.insumo.unidad_medida.abreviacion}")
            else:
                print(f"   ⚠️  Receta existe pero sin insumos")
                
        except Receta.DoesNotExist:
            print(f"   ❌ Receta: NO")
        except Exception as e:
            print(f"   ❌ Error al verificar receta: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 RESUMEN:")
    print("• El mesero debe usar el producto que SÍ tiene receta")
    print("• Si necesitas que ambos productos tengan receta, hay que crearla")

if __name__ == "__main__":
    main()
