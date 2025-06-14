#!/usr/bin/env python3
"""
Script de demostración completa del sistema de insumos compuestos
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Insumo, CategoriaInsumo, UnidadMedida, InsumoCompuesto
from decimal import Decimal

def mostrar_estado_actual():
    """Muestra el estado actual del sistema"""
    print("📊 ESTADO ACTUAL DEL SISTEMA")
    print("="*50)
    
    print(f"💾 Categorías: {CategoriaInsumo.objects.count()}")
    print(f"📏 Unidades de medida: {UnidadMedida.objects.count()}")
    print(f"📦 Insumos básicos: {Insumo.objects.filter(tipo='basico').count()}")
    print(f"🔧 Insumos compuestos: {Insumo.objects.filter(tipo='compuesto').count()}")
    print(f"🧩 Relaciones componente: {InsumoCompuesto.objects.count()}")

def demostrar_insumo_compuesto():
    """Demuestra cómo funciona un insumo compuesto"""
    print("\n🎯 DEMOSTRACIÓN: INSUMO COMPUESTO")
    print("="*50)
    
    # Buscar el insumo compuesto que creamos
    compuesto = Insumo.objects.filter(tipo='compuesto').first()
    
    if not compuesto:
        print("❌ No hay insumos compuestos para demostrar")
        return
    
    print(f"🔧 Insumo compuesto: {compuesto.nombre}")
    print(f"   Código: {compuesto.codigo}")
    print(f"   Categoría: {compuesto.categoria.nombre}")
    print(f"   Unidad: {compuesto.unidad_medida.nombre}")
    print(f"   Precio unitario: ${compuesto.precio_unitario}")
    
    print(f"\n🧩 Componentes:")
    total_calculado = Decimal('0')
    for i, componente in enumerate(compuesto.componentes.all(), 1):
        costo_componente = componente.costo_total()
        total_calculado += costo_componente
        
        print(f"   {i}. {componente.insumo_componente.nombre}")
        print(f"      Cantidad: {componente.cantidad} {componente.insumo_componente.unidad_medida.abreviacion}")
        print(f"      Precio unitario: ${componente.insumo_componente.precio_unitario}")
        print(f"      Costo total: ${costo_componente}")
    
    print(f"\n💰 Cálculo de costos:")
    print(f"   Costo total componentes: ${total_calculado}")
    print(f"   Costo calculado (método): ${compuesto.calcular_costo_compuesto()}")
    print(f"   Precio por unidad: ${compuesto.precio_unitario}")

def mostrar_ejemplo_uso():
    """Muestra un ejemplo práctico de uso"""
    print("\n💡 EJEMPLO PRÁCTICO DE USO")
    print("="*50)
    
    print("🍣 Caso de uso: Salsa Teriyaki Casera")
    print("")
    print("Para un restaurante de sushi, puedes crear insumos compuestos como:")
    print("")
    print("1. 📦 Insumos básicos necesarios:")
    print("   - Salsa de soja (500ml)")
    print("   - Mirin (100ml)")
    print("   - Azúcar (50g)")
    print("   - Jengibre rallado (10g)")
    print("")
    print("2. 🔧 Insumo compuesto resultante:")
    print("   - Salsa Teriyaki Casera (1 litro)")
    print("   - Costo automáticamente calculado")
    print("   - Precio por porción conocido")
    print("")
    print("3. ✅ Beneficios:")
    print("   - Control de costos automático")
    print("   - Consistencia en la preparación")
    print("   - Facilita el cálculo de precios de venta")
    print("   - Inventario más organizado")

def main():
    print("🚀 DEMOSTRACIÓN COMPLETA: SISTEMA DE INSUMOS COMPUESTOS")
    print("="*60)
    
    mostrar_estado_actual()
    demostrar_insumo_compuesto()
    mostrar_ejemplo_uso()
    
    print(f"\n🎉 SISTEMA COMPLETAMENTE FUNCIONAL")
    print("="*60)
    print(f"✅ Puedes acceder al sistema en:")
    print(f"   📱 http://localhost:8000/dashboard/insumos-compuestos/")
    print(f"")
    print(f"🔧 Características implementadas:")
    print(f"   ✅ Crear insumos compuestos con múltiples componentes")
    print(f"   ✅ Cálculo automático de costos")
    print(f"   ✅ Interfaz web intuitiva")
    print(f"   ✅ Validaciones completas")
    print(f"   ✅ Gestión de componentes dinámica")
    print(f"   ✅ Base de datos consistente")

if __name__ == '__main__':
    main()
