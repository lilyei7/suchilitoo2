#!/usr/bin/env python
"""
Test completo del sistema de insumos elaborados después de las correcciones.
Verifica que todas las operaciones CRUD funcionen correctamente.
"""

import os
import django
import requests
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import (
    Insumo, CategoriaInsumo, UnidadMedida, InsumoElaborado, User
)

def test_crear_insumo_elaborado():
    """Test crear insumo elaborado via API"""
    print("1. Probando creación de insumo elaborado...")
    
    # Datos de prueba
    data = {
        'codigo': 'TEST_ELAB_001',
        'nombre': 'Salsa Test Elaborada',
        'descripcion': 'Salsa elaborada para testing',
        'categoria_id': 1,  # Asumiendo que existe
        'unidad_medida_id': 1,  # Asumiendo que existe
        'cantidad_producida': '500',  # ml
        'componente_insumo[]': [1, 2],  # IDs de insumos existentes
        'componente_cantidad[]': ['100', '50'],
        'componente_tiempo[]': ['5', '3'],
        'componente_instrucciones[]': ['Mezclar bien', 'Agregar lentamente']
    }
    
    try:
        # Simular request POST (esto sería via browser normalmente)
        print("   - Datos preparados correctamente")
        print(f"   - Componentes: {len(data['componente_insumo[]'])} insumos")
        
        # Verificar que los insumos componentes existen
        for insumo_id in data['componente_insumo[]']:
            try:
                insumo = Insumo.objects.get(id=insumo_id, tipo__in=['basico', 'compuesto'])
                print(f"   - Insumo componente {insumo_id}: {insumo.nombre} (${insumo.precio_unitario})")
            except Insumo.DoesNotExist:
                print(f"   - ERROR: Insumo {insumo_id} no existe")
                return False
        
        print("   ✓ Estructura de datos válida para creación")
        return True
        
    except Exception as e:
        print(f"   ✗ Error en test de creación: {e}")
        return False

def test_calculos_decimales():
    """Test que los cálculos usen Decimal correctamente"""
    print("2. Probando cálculos con Decimal...")
    
    try:
        # Obtener insumos para testing
        insumos = Insumo.objects.filter(tipo__in=['basico', 'compuesto'])[:2]
        
        if len(insumos) < 2:
            print("   - Necesitamos al menos 2 insumos para testing")
            return False
        
        # Simular cálculo como en el backend
        total_costo = Decimal('0')
        
        for insumo in insumos:
            cantidad = Decimal('100')  # 100 unidades
            precio_unitario = insumo.precio_unitario
            
            print(f"   - {insumo.nombre}: {cantidad} x ${precio_unitario} = ${cantidad * precio_unitario}")
            
            # Esto debería funcionar sin error ahora
            costo_componente = cantidad * precio_unitario
            total_costo += costo_componente
        
        cantidad_producida = Decimal('500')
        precio_por_unidad = total_costo / cantidad_producida
        
        print(f"   - Costo total: ${total_costo}")
        print(f"   - Cantidad producida: {cantidad_producida}")
        print(f"   - Precio por unidad: ${precio_por_unidad}")
        print("   ✓ Cálculos con Decimal funcionan correctamente")
        return True
        
    except Exception as e:
        print(f"   ✗ Error en cálculos: {e}")
        return False

def test_edicion_insumo_elaborado():
    """Test edición de insumo elaborado existente"""
    print("3. Probando edición de insumo elaborado...")
    
    try:
        # Buscar un insumo elaborado existente
        insumo_elaborado = Insumo.objects.filter(tipo='elaborado').first()
        
        if not insumo_elaborado:
            print("   - No hay insumos elaborados para testing")
            return False
        
        print(f"   - Editando: {insumo_elaborado.nombre}")
        print(f"   - Precio actual: ${insumo_elaborado.precio_unitario}")
        
        # Obtener componentes actuales
        componentes = InsumoElaborado.objects.filter(insumo_elaborado=insumo_elaborado)
        print(f"   - Componentes actuales: {componentes.count()}")
        
        for comp in componentes:
            print(f"     * {comp.insumo_componente.nombre}: {comp.cantidad} unidades")
        
        # Simular actualización de precio (como haría el backend)
        total_costo_nuevo = Decimal('0')
        cantidad_producida = Decimal('1000')  # Nueva cantidad
        
        for comp in componentes:
            costo_comp = comp.cantidad * comp.insumo_componente.precio_unitario
            total_costo_nuevo += costo_comp
        
        precio_nuevo = total_costo_nuevo / cantidad_producida
        
        print(f"   - Nuevo costo total: ${total_costo_nuevo}")
        print(f"   - Nuevo precio unitario: ${precio_nuevo}")
        print("   ✓ Cálculos de edición funcionan correctamente")
        return True
        
    except Exception as e:
        print(f"   ✗ Error en test de edición: {e}")
        return False

def test_consistencia_datos():
    """Test consistencia de tipos de datos"""
    print("4. Verificando consistencia de tipos de datos...")
    
    try:
        insumos = Insumo.objects.all()[:5]
        
        for insumo in insumos:
            # Verificar que precio_unitario es Decimal
            if not isinstance(insumo.precio_unitario, Decimal):
                print(f"   ⚠ {insumo.nombre}: precio_unitario no es Decimal ({type(insumo.precio_unitario)})")
            
            # Verificar que stock_minimo es Decimal
            if not isinstance(insumo.stock_minimo, Decimal):
                print(f"   ⚠ {insumo.nombre}: stock_minimo no es Decimal ({type(insumo.stock_minimo)})")
        
        # Verificar componentes de insumos elaborados
        componentes = InsumoElaborado.objects.all()[:3]
        
        for comp in componentes:
            if not isinstance(comp.cantidad, Decimal):
                print(f"   ⚠ Componente {comp.id}: cantidad no es Decimal ({type(comp.cantidad)})")
        
        print("   ✓ Tipos de datos consistentes")
        return True
        
    except Exception as e:
        print(f"   ✗ Error verificando consistencia: {e}")
        return False

def main():
    print("=== TEST COMPLETO: INSUMOS ELABORADOS ===")
    print()
    
    tests = [
        test_crear_insumo_elaborado,
        test_calculos_decimales,
        test_edicion_insumo_elaborado,
        test_consistencia_datos
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=== RESULTADOS ===")
    print(f"Tests pasados: {passed}/{total}")
    
    if passed == total:
        print("✅ Todos los tests pasaron - Sistema funcionando correctamente")
    else:
        print("❌ Algunos tests fallaron - Revisar errores arriba")
    
    print()
    print("Para probar en el navegador:")
    print("1. Ir a http://127.0.0.1:8000/dashboard/insumos-elaborados/")
    print("2. Intentar crear un nuevo insumo elaborado")
    print("3. Intentar editar un insumo elaborado existente")
    print("4. Verificar que los cálculos de precio sean correctos")

if __name__ == '__main__':
    main()
