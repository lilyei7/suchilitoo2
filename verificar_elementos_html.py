#!/usr/bin/env python
"""
Script para verificar que el HTML tenga todos los elementos necesarios
"""
import os

# Leer el archivo HTML
html_file = r"c:\Users\olcha\Desktop\sushi_restaurant - Copy (2)\suchilitoo2\dashboard\templates\dashboard\sucursales.html"

print("=== VERIFICACIÓN DE ELEMENTOS HTML ===")

try:
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Elementos a verificar
    elementos_check = [
        ('función gestionarMesas', 'function gestionarMesas('),
        ('modal Gestionar Mesas', 'id="modalGestionarMesas"'),
        ('botón Gestionar Mesas', 'Gestionar Mesas'),
        ('formulario nueva mesa', 'id="formularioNuevaMesa"'),
        ('grid de mesas', 'id="gridMesas"'),
        ('función cargarMesasSucursal', 'function cargarMesasSucursal('),
        ('función mostrarMesas', 'function mostrarMesas('),
        ('formulario editar mesa', 'id="formularioEditarMesa"'),
        ('función editarMesa', 'function editarMesa('),
        ('evento onclick', 'onclick="gestionarMesas(')
    ]
    
    print("Verificando elementos...")
    todos_presentes = True
    
    for nombre, buscar in elementos_check:
        if buscar in content:
            print(f"✓ {nombre} - PRESENTE")
        else:
            print(f"✗ {nombre} - FALTANTE")
            todos_presentes = False
    
    if todos_presentes:
        print("\n🎉 ¡Todos los elementos están presentes!")
        print("\nInstrucciones para probar:")
        print("1. Ve a: http://localhost:8000/dashboard/sucursales/")
        print("2. Haz login si es necesario")
        print("3. Busca cualquier tarjeta de sucursal")
        print("4. Haz clic en el botón '...' (tres puntos)")
        print("5. Haz clic en 'Gestionar Mesas'")
        print("6. Debería abrirse el modal con las mesas")
        
        # Conteo de líneas
        lines = content.split('\n')
        print(f"\nEstadísticas del archivo:")
        print(f"- Total de líneas: {len(lines)}")
        print(f"- Tamaño: {len(content)} caracteres")
        
    else:
        print("\n❌ Faltan algunos elementos necesarios")
        
except FileNotFoundError:
    print(f"❌ No se encontró el archivo: {html_file}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n=== FIN DE LA VERIFICACIÓN ===")
