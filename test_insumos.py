#!/usr/bin/env python
"""
Script para probar la creación de insumos
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import CategoriaInsumo, UnidadMedida, Insumo
from accounts.models import Sucursal, Usuario
from dashboard.models import Proveedor

def test_crear_insumo():
    """Prueba de creación de un insumo"""
    print("🧪 Probando creación de insumo...")
    
    # Verificar datos necesarios
    categorias = CategoriaInsumo.objects.all()
    unidades = UnidadMedida.objects.all()
    
    print(f"📂 Categorías disponibles: {categorias.count()}")
    for cat in categorias:
        print(f"  - {cat.id}: {cat.nombre}")
    
    print(f"📏 Unidades disponibles: {unidades.count()}")
    for unidad in unidades:
        print(f"  - {unidad.id}: {unidad.nombre} ({unidad.abreviacion})")
    
    if categorias.exists() and unidades.exists():
        # Crear insumo de prueba
        try:
            insumo = Insumo.objects.create(
                codigo="TEST001",
                nombre="Insumo de Prueba",
                categoria=categorias.first(),
                unidad_medida=unidades.first(),
                tipo="basico",
                precio_unitario=10.50,
                stock_minimo=5.0
            )
            print(f"✅ Insumo creado exitosamente: {insumo}")
            
            # Eliminar el insumo de prueba
            insumo.delete()
            print("🗑️ Insumo de prueba eliminado")
            
        except Exception as e:
            print(f"❌ Error al crear insumo: {str(e)}")
    else:
        print("❌ No hay categorías o unidades disponibles")

def verificar_usuarios():
    """Verificar usuarios disponibles"""
    print("\n👥 Verificando usuarios...")
    usuarios = Usuario.objects.all()
    print(f"Total usuarios: {usuarios.count()}")
    
    for usuario in usuarios:
        print(f"  - {usuario.username}: {usuario.first_name} {usuario.last_name}")
        if usuario.sucursal:
            print(f"    Sucursal: {usuario.sucursal.nombre}")
        else:
            print("    Sin sucursal asignada")

if __name__ == '__main__':
    test_crear_insumo()
    verificar_usuarios()
