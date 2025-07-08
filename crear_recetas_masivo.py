#!/usr/bin/env python
"""
Script para crear recetas básicas para todos los productos que no tienen receta
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

def crear_recetas_basicas():
    """Crear recetas básicas para productos sin recetas"""
    print("🔧 CREANDO RECETAS BÁSICAS PARA PRODUCTOS SIN RECETAS")
    print("=" * 70)
    
    # 1. Encontrar productos sin recetas
    productos_sin_receta = ProductoVenta.objects.filter(receta__isnull=True)
    total = productos_sin_receta.count()
    
    print(f"📊 Productos sin recetas encontrados: {total}")
    
    if total == 0:
        print("✅ Todos los productos ya tienen recetas")
        return
    
    # 2. Buscar algunos insumos básicos para usar como plantilla
    insumos_basicos = []
    
    # Buscar arroz (común en sushi)
    try:
        arroz = Insumo.objects.filter(nombre__icontains="arroz").first()
        if arroz:
            insumos_basicos.append(("arroz", arroz, 100))  # 100g por defecto
    except:
        pass
    
    # Buscar alga nori
    try:
        alga = Insumo.objects.filter(nombre__icontains="alga").first()
        if alga:
            insumos_basicos.append(("alga", alga, 2))  # 2 unidades por defecto
    except:
        pass
    
    # Buscar salmón
    try:
        salmon = Insumo.objects.filter(nombre__icontains="salmón").first()
        if salmon:
            insumos_basicos.append(("salmón", salmon, 50))  # 50g por defecto
    except:
        pass
    
    print(f"🥗 Insumos básicos disponibles: {len(insumos_basicos)}")
    for nombre, insumo, cantidad in insumos_basicos:
        print(f"   • {nombre}: {insumo.nombre} ({cantidad} {insumo.unidad_medida})")
    
    if not insumos_basicos:
        print("❌ No se encontraron insumos básicos, no se pueden crear recetas")
        return
    
    # 3. Mostrar productos y pedir confirmación
    print(f"\n📋 PRODUCTOS QUE RECIBIRÁN RECETAS BÁSICAS:")
    print("-" * 50)
    
    for i, producto in enumerate(productos_sin_receta[:10], 1):  # Mostrar solo los primeros 10
        print(f"{i:2d}. {producto.nombre} (ID: {producto.id})")
    
    if total > 10:
        print(f"    ... y {total - 10} productos más")
    
    print(f"\n⚠️  ADVERTENCIA:")
    print(f"• Se crearán {total} recetas con insumos básicos")
    print(f"• Estas recetas son TEMPORALES y deben revisarse manualmente")
    print(f"• Sirven para permitir las ventas mientras se definen las recetas reales")
    
    respuesta = input(f"\n❓ ¿Proceder con la creación de {total} recetas? (s/N): ").strip().lower()
    
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Operación cancelada")
        return
    
    # 4. Crear las recetas
    print(f"\n🔧 Creando recetas...")
    creadas = 0
    errores = 0
    
    for producto in productos_sin_receta:
        try:
            # Crear la receta
            receta = Receta.objects.create(
                producto=producto,
                tiempo_preparacion=10,  # 10 minutos por defecto
                porciones=1,
                instrucciones=f"Receta básica generada automáticamente para {producto.nombre}",
                notas="⚠️ RECETA TEMPORAL - Revisar y actualizar con ingredientes reales",
                activo=True
            )
            
            # Agregar un insumo básico según el tipo de producto
            insumo_seleccionado = None
            cantidad_sugerida = 50
            
            # Lógica simple para seleccionar insumo según el nombre del producto
            nombre_lower = producto.nombre.lower()
            
            if "alga" in nombre_lower:
                # Buscar alga
                for nombre, insumo, cantidad in insumos_basicos:
                    if "alga" in nombre:
                        insumo_seleccionado = insumo
                        cantidad_sugerida = cantidad
                        break
            elif any(palabra in nombre_lower for palabra in ["sushi", "maki", "roll"]):
                # Buscar arroz para productos de sushi
                for nombre, insumo, cantidad in insumos_basicos:
                    if "arroz" in nombre:
                        insumo_seleccionado = insumo
                        cantidad_sugerida = cantidad
                        break
            elif "salmón" in nombre_lower:
                # Buscar salmón
                for nombre, insumo, cantidad in insumos_basicos:
                    if "salmón" in nombre:
                        insumo_seleccionado = insumo
                        cantidad_sugerida = cantidad
                        break
            
            # Si no se encontró uno específico, usar el primero disponible
            if not insumo_seleccionado and insumos_basicos:
                _, insumo_seleccionado, cantidad_sugerida = insumos_basicos[0]
            
            # Crear la relación insumo-receta
            if insumo_seleccionado:
                RecetaInsumo.objects.create(
                    receta=receta,
                    insumo=insumo_seleccionado,
                    cantidad=cantidad_sugerida
                )
            
            creadas += 1
            print(f"✅ {creadas:2d}/{total} - {producto.nombre}")
            
        except Exception as e:
            errores += 1
            print(f"❌ Error con {producto.nombre}: {e}")
    
    print(f"\n" + "=" * 70)
    print(f"📊 RESUMEN:")
    print(f"• Recetas creadas exitosamente: {creadas}")
    print(f"• Errores: {errores}")
    print(f"• Total productos sin recetas antes: {total}")
    
    # Verificar cuántos quedan sin recetas
    productos_restantes = ProductoVenta.objects.filter(receta__isnull=True).count()
    print(f"• Productos que aún no tienen recetas: {productos_restantes}")
    
    if creadas > 0:
        print(f"\n💡 PRÓXIMOS PASOS:")
        print(f"• Revisar las recetas creadas en el admin de Django")
        print(f"• Actualizar los insumos y cantidades según las recetas reales")
        print(f"• Eliminar la nota de 'RECETA TEMPORAL' cuando estén completas")

def main():
    crear_recetas_basicas()

if __name__ == "__main__":
    main()
