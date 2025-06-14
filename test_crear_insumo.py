#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Insumo, CategoriaInsumo, UnidadMedida, Inventario, MovimientoInventario
from accounts.models import Usuario, Sucursal

def test_crear_insumo():
    print("=== PRUEBA DE CREACIÓN DE INSUMO ===")
    
    # Obtener datos necesarios
    categoria = CategoriaInsumo.objects.first()
    unidad = UnidadMedida.objects.first()
    usuario = Usuario.objects.filter(is_superuser=True).first()
    
    print(f"Categoría: {categoria}")
    print(f"Unidad: {unidad}")
    print(f"Usuario: {usuario}")
    print(f"Usuario es admin: {usuario.is_superuser if usuario else 'No hay usuario'}")
    print(f"Usuario tiene sucursal: {usuario.sucursal if usuario else 'No hay usuario'}")
    
    if not categoria or not unidad:
        print("ERROR: No hay categorías o unidades de medida")
        return
    
    if not usuario:
        print("ERROR: No hay usuario superusuario")
        return
    
    # Datos del insumo de prueba
    datos_insumo = {
        'codigo': 'TEST001',
        'nombre': 'Insumo de Prueba',
        'categoria_id': categoria.id,
        'unidad_medida_id': unidad.id,
        'tipo': 'basico',
        'precio_unitario': 10.50,
        'stock_minimo': 5
    }
    
    # Verificar si ya existe
    if Insumo.objects.filter(codigo=datos_insumo['codigo']).exists():
        print("El insumo de prueba ya existe, eliminándolo...")
        Insumo.objects.filter(codigo=datos_insumo['codigo']).delete()
    
    try:
        # Crear el insumo
        insumo = Insumo.objects.create(**datos_insumo)
        print(f"✅ Insumo creado exitosamente: {insumo}")
          # Crear inventario en todas las sucursales (simulando admin)
        stock_inicial = 100
        sucursales = Sucursal.objects.filter(activa=True)
        print(f"Sucursales activas: {sucursales.count()}")
        
        for sucursal in sucursales:
            inventario = Inventario.objects.create(
                sucursal=sucursal,
                insumo=insumo,
                cantidad_actual=stock_inicial
            )
            print(f"✅ Inventario creado en {sucursal.nombre}: {inventario}")
            
            # Crear movimiento
            movimiento = MovimientoInventario.objects.create(
                sucursal=sucursal,
                insumo=insumo,
                tipo_movimiento='entrada',
                cantidad=stock_inicial,
                motivo='Stock inicial del insumo (Prueba)',
                usuario=usuario
            )
            print(f"✅ Movimiento creado: {movimiento}")
        
        print("\n=== VERIFICACIÓN ===")
        print(f"Total insumos: {Insumo.objects.count()}")
        print(f"Total inventarios: {Inventario.objects.count()}")
        print(f"Total movimientos: {MovimientoInventario.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error al crear insumo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_crear_insumo()
