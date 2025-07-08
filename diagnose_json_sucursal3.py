#!/usr/bin/env python3
"""
Script para diagnosticar el problema de JSON en vista previa
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from dashboard.models_croquis import CroquisLayout
from accounts.models import Sucursal
import json

def diagnose_json_issue():
    """Diagnosticar problema de JSON específicamente para sucursal 3"""
    
    print("🔍 Diagnosticando problema JSON para sucursal 3...")
    
    try:
        # Buscar sucursal 3 específicamente
        sucursal = Sucursal.objects.get(id=3)
        print(f"✅ Sucursal encontrada: {sucursal.nombre}")
        
        # Buscar layout
        try:
            layout = CroquisLayout.objects.get(sucursal=sucursal)
            print(f"✅ Layout encontrado")
            
            if layout.layout_data:
                print(f"📊 Tipo layout_data: {type(layout.layout_data)}")
                
                # Mostrar una muestra de los datos
                if isinstance(layout.layout_data, dict):
                    print(f"📋 Keys en layout_data: {list(layout.layout_data.keys())}")
                    
                    if 'objetos' in layout.layout_data:
                        objetos = layout.layout_data['objetos']
                        print(f"📦 Número de objetos: {len(objetos)}")
                        
                        # Mostrar primer objeto
                        if objetos:
                            primer_objeto = objetos[0]
                            print(f"🔍 Primer objeto: {primer_objeto}")
                
                # Intentar la conversión paso a paso
                print("\n🔧 Probando conversión...")
                
                def convert_python_to_js(obj):
                    """Convertir recursivamente True/False de Python a true/false de JS"""
                    if isinstance(obj, dict):
                        return {k: convert_python_to_js(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [convert_python_to_js(item) for item in obj]
                    elif isinstance(obj, bool):
                        return obj  # JSON dumps manejará esto correctamente
                    else:
                        return obj
                
                # Paso 1: Convertir datos
                clean_data = convert_python_to_js(layout.layout_data)
                print("✅ Conversión Python->JS completada")
                
                # Paso 2: Serializar a JSON
                layout_json = json.dumps(clean_data, ensure_ascii=False, separators=(',', ':'))
                print(f"✅ Serialización JSON completada (length: {len(layout_json)})")
                
                # Mostrar inicio del JSON
                print(f"📄 Primeros 200 caracteres del JSON:")
                print(f"'{layout_json[:200]}...'")
                
                # Paso 3: Verificar que se puede parsear
                parsed_back = json.loads(layout_json)
                print("✅ Verificación de parseo exitosa")
                
                # Verificar caracteres problemáticos
                problematic_chars = []
                for i, char in enumerate(layout_json[:50]):
                    if ord(char) > 127 or char in ['"', "'", '\\']:
                        problematic_chars.append(f"pos {i}: '{char}' (ord {ord(char)})")
                
                if problematic_chars:
                    print(f"⚠️ Caracteres potencialmente problemáticos: {problematic_chars}")
                else:
                    print("✅ No se detectaron caracteres problemáticos en el inicio")
                
                # Crear contenido de template simulado
                print(f"\n📝 Template content simulado:")
                template_content = f"layoutData = {layout_json};"
                print(f"'{template_content[:100]}...'")
                
            else:
                print("❌ layout_data está vacío")
        
        except CroquisLayout.DoesNotExist:
            print("❌ No existe layout para sucursal 3")
            
            # Crear layout de prueba
            print("🔧 Creando layout de prueba...")
            sample_data = {
                'objetos': [
                    {
                        'id': 1,
                        'tipo': 'mesa',
                        'x': 100,
                        'y': 100,
                        'width': 60,
                        'height': 60,
                        'piso': 1,
                        'propiedades': {
                            'numero': '1',
                            'capacidad': 4
                        }
                    }
                ],
                'version': '2.0'
            }
            
            layout = CroquisLayout.objects.create(
                sucursal=sucursal,
                layout_data=sample_data
            )
            print("✅ Layout de prueba creado")
    
    except Sucursal.DoesNotExist:
        print("❌ Sucursal 3 no existe")
        
        # Mostrar sucursales disponibles
        sucursales = Sucursal.objects.all()
        print(f"📋 Sucursales disponibles:")
        for s in sucursales:
            print(f"  - ID {s.id}: {s.nombre}")
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_json_issue()
