#!/usr/bin/env python3
"""
Script simple para debuggear el problema de JSON en croquis
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suchilitoo.settings')
django.setup()

from dashboard.models_croquis import CroquisLayout
import json

def debug_json_issue():
    print("🔍 Debuggeando problema de JSON en croquis...")
    
    # Buscar layouts
    layouts = CroquisLayout.objects.all()
    print(f"Total layouts encontrados: {layouts.count()}")
    
    for layout in layouts:
        print(f"\n📋 Sucursal {layout.sucursal.id}: {layout.sucursal.nombre}")
        
        if layout.layout_data:
            print(f"  Tipo layout_data: {type(layout.layout_data)}")
            
            # Si es dict, verificar contenido
            if isinstance(layout.layout_data, dict):
                # Buscar propiedades booleanas problemáticas
                def find_booleans(obj, path=""):
                    problems = []
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            current_path = f"{path}.{key}" if path else key
                            if isinstance(value, bool):
                                problems.append(f"{current_path}={value}")
                            elif isinstance(value, (dict, list)):
                                problems.extend(find_booleans(value, current_path))
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            problems.extend(find_booleans(item, f"{path}[{i}]"))
                    return problems
                
                boolean_props = find_booleans(layout.layout_data)
                if boolean_props:
                    print(f"  ⚠️ Propiedades booleanas encontradas:")
                    for prop in boolean_props[:5]:  # Solo primeras 5
                        print(f"    {prop}")
                
                # Intentar serializar
                try:
                    json_str = json.dumps(layout.layout_data, ensure_ascii=False)
                    print(f"  ✅ JSON serialization OK (length: {len(json_str)})")
                    
                    # Verificar si contiene True/False de Python
                    if 'True' in json_str or 'False' in json_str:
                        print(f"  ❌ PROBLEMA: JSON contiene True/False de Python")
                        
                        # Mostrar fragmento problemático
                        import re
                        matches = re.findall(r'.{0,20}(True|False).{0,20}', json_str)
                        for match in matches[:3]:
                            print(f"    '{match}'")
                    else:
                        print(f"  ✅ JSON no contiene True/False problemáticos")
                        
                except Exception as e:
                    print(f"  ❌ Error serializando: {e}")
            else:
                print(f"  ⚠️ layout_data no es diccionario")
        else:
            print(f"  ⚠️ layout_data vacío")

if __name__ == "__main__":
    debug_json_issue()
