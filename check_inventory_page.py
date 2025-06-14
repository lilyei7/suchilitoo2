#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificación específica de la página de inventario
"""

import requests

def main():
    """Verificación final simple"""
    try:
        response = requests.get('http://127.0.0.1:8000/dashboard/inventario/', timeout=10)
        
        if response.status_code == 200:
            print("✅ Página carga correctamente")
            
            html_content = response.text
            
            # Verificaciones específicas
            checks = [
                ('id="nuevoInsumoModal"', 'Modal de nuevo insumo'),
                ('function crearInsumo()', 'Función crearInsumo'),
                ('data-bs-target="#nuevoInsumoModal"', 'Botón de nuevo insumo'),
                ('NUEVO INSUMO', 'Texto del botón'),
                ('Total Insumos', 'Estadísticas'),
            ]
            
            for search_term, description in checks:
                if search_term in html_content:
                    print(f"✅ {description}: Encontrado")
                else:
                    print(f"❌ {description}: NO encontrado")
            
            # Verificar que no hay templates sin renderizar
            if '{{' in html_content and '}}' in html_content:
                # Buscar líneas específicas con templates
                lines = html_content.split('\n')
                unrendered = []
                for i, line in enumerate(lines, 1):
                    if '{{' in line and '}}' in line and not line.strip().startswith('<!--'):
                        unrendered.append(f"Línea {i}: {line.strip()[:100]}...")
                
                if unrendered:
                    print(f"❌ Templates sin renderizar encontrados: {len(unrendered)}")
                    for template in unrendered[:3]:
                        print(f"   🔴 {template}")
                else:
                    print("✅ No hay templates sin renderizar visibles")
            
            return True
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 VERIFICACIÓN ESPECÍFICA DE INVENTARIO")
    print("=" * 45)
    main()
    print("=" * 45)
    print("💡 Si todo está ✅, recarga la página del navegador")
