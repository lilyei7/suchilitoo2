#!/usr/bin/env python
"""
Script para probar directamente la vista de insumos disponibles
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import RequestFactory
from dashboard.views.insumos_elaborados_views import obtener_insumos_para_elaborados
import json

def probar_vista_insumos_disponibles():
    """Probar la vista que obtiene insumos disponibles"""
    
    print("=" * 60)
    print("PRUEBA DIRECTA: Vista obtener_insumos_para_elaborados")
    print("=" * 60)
    
    # Crear request falso
    factory = RequestFactory()
    request = factory.get('/dashboard/insumos-elaborados/insumos-disponibles/')
    
    # Crear usuario falso para el request
    from django.contrib.auth.models import AnonymousUser
    request.user = AnonymousUser()
    
    try:
        response = obtener_insumos_para_elaborados(request)
        
        if hasattr(response, 'content'):
            data = json.loads(response.content.decode('utf-8'))
            
            print(f"✅ Respuesta recibida")
            print(f"Success: {data.get('success')}")
            
            if data.get('success'):
                print(f"Total insumos: {data.get('total', 0)}")
                print(f"Básicos: {data.get('total_basicos', 0)}")
                print(f"Compuestos: {data.get('total_compuestos', 0)}")
                
                insumos = data.get('insumos', [])
                print(f"\nPrimeros 3 insumos:")
                for i, insumo in enumerate(insumos[:3]):
                    print(f"  {i+1}. [{insumo['tipo']}] {insumo['nombre']} - ${insumo['precio_unitario']}")
                
                # Verificar que tengamos ambos tipos
                tipos = {}
                for insumo in insumos:
                    tipo = insumo['tipo']
                    tipos[tipo] = tipos.get(tipo, 0) + 1
                
                print(f"\nTipos encontrados: {tipos}")
                
                if 'basico' in tipos and 'compuesto' in tipos:
                    print("✅ Se encontraron tanto insumos básicos como compuestos")
                else:
                    print("⚠️ Faltan algunos tipos de insumos")
                    
            else:
                print(f"❌ Error: {data.get('message')}")
        else:
            print(f"❌ Respuesta inválida")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

if __name__ == '__main__':
    probar_vista_insumos_disponibles()
