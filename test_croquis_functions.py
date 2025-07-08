#!/usr/bin/env python3
"""
Test script to check if the croquis editor has all required JavaScript functions
"""

import re
import os

def check_croquis_functions():
    print("🔍 Verificando funciones JavaScript del editor de croquis...")
    
    croquis_file = "dashboard/templates/dashboard/croquis_editor.html"
    
    if not os.path.exists(croquis_file):
        print(f"❌ Archivo no encontrado: {croquis_file}")
        return
    
    with open(croquis_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Funciones requeridas en el HTML
    required_functions = [
        'onMouseDown',
        'onMouseMove', 
        'onMouseUp',
        'onWheel',
        'seleccionarHerramienta',
        'actualizarPanelPropiedades',
        'guardarLayout',
        'cargarLayout',
        'eliminarSeleccionado',
        'cambiarPiso',
        'agregarPiso',
        'inicializarCanvas',
        'inicializarDragAndDrop',
        'crearObjetoEnPosicion',
        'duplicarSeleccionado',
        'limpiarPiso',
        'centrarVista',
        'ajustarTamaño',
        'zoomIn',
        'zoomOut',
        'redraw',
        'showToast',
        'encontrarObjetoEnPunto',
        # Funciones de dibujo
        'dibujarObjeto',
        'dibujarMesa',
        'dibujarSilla',
        'dibujarPared',
        'dibujarPuerta',
        'dibujarVentana',
        'dibujarBarra',
        'dibujarBano',
        'dibujarCocina',
        'dibujarPlanta',
        'dibujarCaja',
        'dibujarTelevision',
        'dibujarCuadro',
        'dibujarGenerico',
        'dibujarGrid'
    ]
    
    print(f"📋 Verificando {len(required_functions)} funciones requeridas...")
    
    missing_functions = []
    found_functions = []
    
    for func in required_functions:
        # Buscar declaración de función
        pattern = rf'function\s+{func}\s*\('
        if re.search(pattern, content):
            found_functions.append(func)
            print(f"✅ {func}")
        else:
            missing_functions.append(func)
            print(f"❌ {func} - FALTANTE")
    
    print(f"\n📊 Resumen:")
    print(f"✅ Funciones encontradas: {len(found_functions)}/{len(required_functions)}")
    print(f"❌ Funciones faltantes: {len(missing_functions)}")
    
    if missing_functions:
        print(f"\n🚨 Funciones que faltan:")
        for func in missing_functions:
            print(f"  - {func}")
        
        return False
    else:
        print(f"\n🎉 ¡Todas las funciones JavaScript están presentes!")
        return True

if __name__ == "__main__":
    check_croquis_functions()
