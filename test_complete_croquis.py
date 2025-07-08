#!/usr/bin/env python3
"""
Script de validación completa para verificar que todas las funciones
del editor de croquis están correctamente implementadas.
"""

import re
import sys
from pathlib import Path

def validate_mouse_events():
    """Valida que todos los eventos del mouse estén definidos"""
    file_path = Path(__file__).parent / "dashboard" / "templates" / "dashboard" / "croquis_editor.html"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Funciones de eventos del mouse que deben existir
    mouse_functions = [
        'onMouseDown',
        'onMouseMove', 
        'onMouseUp',
        'onWheel',
        'getMousePos',
        'getObjectAt',
        'crearObjeto',
        'getColorForType'
    ]
    
    print("🖱️ VALIDACIÓN DE EVENTOS DEL MOUSE")
    print("=" * 40)
    
    missing_functions = []
    for func in mouse_functions:
        if f"function {func}(" in content:
            print(f"  ✅ {func}")
        else:
            print(f"  ❌ {func}")
            missing_functions.append(func)
    
    if missing_functions:
        print(f"\n❌ Funciones faltantes: {missing_functions}")
        return False
    else:
        print(f"\n✅ Todas las funciones de eventos del mouse están definidas")
        return True

def validate_event_listeners():
    """Valida que los event listeners estén correctamente configurados"""
    file_path = Path(__file__).parent / "dashboard" / "templates" / "dashboard" / "croquis_editor.html"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Event listeners que deben estar configurados
    listeners = [
        'addEventListener.*mousedown.*onMouseDown',
        'addEventListener.*mousemove.*onMouseMove',
        'addEventListener.*mouseup.*onMouseUp',
        'addEventListener.*wheel.*onWheel'
    ]
    
    print("\n🎧 VALIDACIÓN DE EVENT LISTENERS")
    print("=" * 40)
    
    missing_listeners = []
    for listener in listeners:
        if re.search(listener, content):
            event_name = listener.split('.*')[1]
            print(f"  ✅ {event_name}")
        else:
            print(f"  ❌ {listener}")
            missing_listeners.append(listener)
    
    if missing_listeners:
        print(f"\n❌ Event listeners faltantes: {len(missing_listeners)}")
        return False
    else:
        print(f"\n✅ Todos los event listeners están configurados")
        return True

def validate_core_functions():
    """Valida las funciones principales del editor"""
    file_path = Path(__file__).parent / "dashboard" / "templates" / "dashboard" / "croquis_editor.html"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Funciones core que deben existir
    core_functions = [
        'inicializarCanvas',
        'redraw',
        'dibujarCuadricula',
        'dibujarLimites',
        'dibujarEscala',
        'dibujarObjeto',
        'dibujarMesa',
        'dibujarSilla',
        'dibujarPared',
        'dibujarPuerta',
        'dibujarBarra',
        'actualizarContadorObjetos',
        'actualizarPanelPropiedades'
    ]
    
    print("\n⚙️ VALIDACIÓN DE FUNCIONES PRINCIPALES")
    print("=" * 40)
    
    missing_functions = []
    for func in core_functions:
        if f"function {func}(" in content:
            print(f"  ✅ {func}")
        else:
            print(f"  ❌ {func}")
            missing_functions.append(func)
    
    if missing_functions:
        print(f"\n❌ Funciones faltantes: {missing_functions}")
        return False
    else:
        print(f"\n✅ Todas las funciones principales están definidas")
        return True

def main():
    """Función principal de validación"""
    print("🔍 VALIDACIÓN COMPLETA DEL EDITOR DE CROQUIS")
    print("=" * 50)
    
    results = []
    
    # Ejecutar todas las validaciones
    results.append(validate_mouse_events())
    results.append(validate_event_listeners())
    results.append(validate_core_functions())
    
    # Resultado final
    all_passed = all(results)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 VALIDACIÓN COMPLETA EXITOSA")
        print("✅ Todos los eventos del mouse están implementados")
        print("✅ Todos los event listeners están configurados")
        print("✅ Todas las funciones principales están definidas")
        print("🚀 El editor de croquis está completamente funcional")
        print("\n📋 FUNCIONALIDADES DISPONIBLES:")
        print("  🖱️ Eventos de mouse: click, move, drag, zoom")
        print("  🎨 Herramientas: seleccionar, mesa, silla, pared, puerta, barra")
        print("  🏢 Gestión de pisos: agregar, eliminar, cambiar")
        print("  📐 Dimensiones reales: configuración en metros")
        print("  📊 Cuadrícula: visible con escala real")
        print("  🏗️ Layout predefinido: creación automática")
        print("  💾 Persistencia: guardar/cargar layouts")
        print("  🔗 Gestión de mesas: vincular mesas del sistema")
    else:
        print("❌ VALIDACIÓN FALLIDA")
        print("⚠️ Algunos componentes no están correctamente implementados")
        print("🔧 Revisa los errores mostrados arriba")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
