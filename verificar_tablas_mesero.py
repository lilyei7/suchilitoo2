#!/usr/bin/env python3
"""
Script para verificar qué tablas de mesero existen
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.db import connection

def main():
    print("=== VERIFICANDO TABLAS DE MESERO ===\n")
    
    cursor = connection.cursor()
    
    # Verificar qué tablas de mesero existen
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE 'mesero_%'
    """)
    
    tablas = cursor.fetchall()
    print("📋 TABLAS DE MESERO EXISTENTES:")
    
    if tablas:
        for tabla in tablas:
            print(f"   ✅ {tabla[0]}")
            
            # Mostrar estructura de cada tabla
            cursor.execute(f"PRAGMA table_info({tabla[0]});")
            columns = cursor.fetchall()
            print(f"      Columnas: {', '.join([col[1] for col in columns])}")
    else:
        print("   ❌ No hay tablas de mesero")
    
    print("\n📋 TABLAS NECESARIAS:")
    print("   - mesero_mesa ✅" if any('mesero_mesa' in t[0] for t in tablas) else "   - mesero_mesa ❌")
    print("   - mesero_orden ✅" if any('mesero_orden' in t[0] for t in tablas) else "   - mesero_orden ❌")
    print("   - mesero_ordenitem ✅" if any('mesero_ordenitem' in t[0] for t in tablas) else "   - mesero_ordenitem ❌")
    print("   - mesero_historialorden ✅" if any('mesero_historialorden' in t[0] for t in tablas) else "   - mesero_historialorden ❌")
    print("   - mesero_historialmesa ✅" if any('mesero_historialmesa' in t[0] for t in tablas) else "   - mesero_historialmesa ❌")

if __name__ == '__main__':
    main()
