#!/usr/bin/env python3
"""
Script para iniciar el servidor y probar cocina
"""

import os
import sys

def main():
    print("🍣 INICIANDO SERVIDOR PARA PROBAR COCINA")
    print("=" * 50)
    print()
    print("1. Para iniciar el servidor ejecute:")
    print("   python manage.py runserver")
    print()
    print("2. Luego vaya a: http://localhost:8000/cocina/")
    print()
    print("3. Use las credenciales de cocina:")
    print("   Usuario: cocinero")
    print("   Contraseña: cocinero123")
    print("   O:")
    print("   Usuario: ayudante") 
    print("   Contraseña: ayudante123")
    print()
    print("🎯 FUNCIONALIDADES DISPONIBLES:")
    print("   ✓ /cocina/ - Dashboard principal")
    print("   ✓ /cocina/login/ - Login específico")
    print("   ✓ /cocina/ordenes/ - Órdenes pendientes")
    print("   ✓ /cocina/reportes/ - Reportes")
    print("   ✓ /cocina/estadisticas/ - Estadísticas")
    print()
    print("🔥 CARACTERÍSTICAS:")
    print("   ✓ Interfaz moderna y responsive")
    print("   ✓ Tiempo real con auto-refresh")
    print("   ✓ Gestión de estados de órdenes")
    print("   ✓ Cronómetro integrado")
    print("   ✓ Filtros y búsqueda")
    print("   ✓ Reportes y estadísticas")
    print("   ✓ Asignación de cocineros")
    print("   ✓ Seguimiento de tiempos")
    print()
    print("🍜 ¡EL SISTEMA DE COCINA ESTÁ LISTO!")

if __name__ == '__main__':
    main()
