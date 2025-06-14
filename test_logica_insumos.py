#!/usr/bin/env python
"""
Script para probar directamente la lógica de obtener insumos sin decoradores
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Insumo

def probar_logica_insumos():
    """Probar la lógica de obtener insumos disponibles"""
    
    print("=" * 60)
    print("PRUEBA DIRECTA: Lógica de insumos disponibles")
    print("=" * 60)
    
    try:
        # Replicar exactamente la lógica de la vista
        insumos = Insumo.objects.filter(
            tipo__in=['basico', 'compuesto'], 
            activo=True
        ).select_related('categoria', 'unidad_medida').order_by('tipo', 'nombre')
        
        insumos_data = []
        total_basicos = 0
        total_compuestos = 0
        
        for insumo in insumos:
            insumos_data.append({
                'id': insumo.id,
                'codigo': insumo.codigo,
                'nombre': insumo.nombre,
                'tipo': insumo.tipo,
                'categoria_nombre': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
                'unidad_medida_nombre': str(insumo.unidad_medida) if insumo.unidad_medida else 'Sin unidad',
                'precio_unitario': float(insumo.precio_unitario)
            })
            
            if insumo.tipo == 'basico':
                total_basicos += 1
            elif insumo.tipo == 'compuesto':
                total_compuestos += 1
        
        print(f"✅ Consulta exitosa")
        print(f"Total de insumos: {len(insumos_data)}")
        print(f"Básicos: {total_basicos}")
        print(f"Compuestos: {total_compuestos}")
        
        # Mostrar algunos ejemplos
        print(f"\n📦 Primeros 3 insumos básicos:")
        basicos = [i for i in insumos_data if i['tipo'] == 'basico'][:3]
        for insumo in basicos:
            print(f"   ID {insumo['id']}: {insumo['codigo']} - {insumo['nombre']} (${insumo['precio_unitario']})")
        
        print(f"\n🔧 Primeros 3 insumos compuestos:")
        compuestos = [i for i in insumos_data if i['tipo'] == 'compuesto'][:3]
        for insumo in compuestos:
            print(f"   ID {insumo['id']}: {insumo['codigo']} - {insumo['nombre']} (${insumo['precio_unitario']})")
        
        # Simular la respuesta JSON
        response_data = {
            'success': True,
            'insumos': insumos_data,
            'total_basicos': total_basicos,
            'total_compuestos': total_compuestos,
            'total': len(insumos_data)
        }
        
        print(f"\n✅ Respuesta JSON que se generaría:")
        print(f"   success: {response_data['success']}")
        print(f"   total: {response_data['total']}")
        print(f"   total_basicos: {response_data['total_basicos']}")
        print(f"   total_compuestos: {response_data['total_compuestos']}")
        
        if total_basicos > 0 and total_compuestos > 0:
            print("\n✅ ÉXITO: Hay ambos tipos de insumos disponibles")
        elif total_basicos > 0:
            print("\n⚠️ PARCIAL: Solo hay insumos básicos")
        elif total_compuestos > 0:
            print("\n⚠️ PARCIAL: Solo hay insumos compuestos")
        else:
            print("\n❌ PROBLEMA: No hay insumos disponibles")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

if __name__ == '__main__':
    probar_logica_insumos()
