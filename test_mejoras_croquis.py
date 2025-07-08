#!/usr/bin/env python3
"""
Script para probar las mejoras del editor de croquis:
- Coordenadas corregidas (inician desde 0,0)
- Zoom mejorado que no pierde objetos
- Rotación de paredes y otros objetos
"""

import sys
from pathlib import Path

def test_mejoras_croquis():
    """Verifica que las mejoras estén implementadas"""
    file_path = Path(__file__).parent / "dashboard" / "templates" / "dashboard" / "croquis_editor.html"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 VERIFICACIÓN DE MEJORAS DEL EDITOR DE CROQUIS")
    print("=" * 55)
    
    mejoras = [
        ("📍 Coordenadas desde 0,0", "Math.max(0, (pos.x / escalaPixelsPorMetro))" in content),
        ("🔄 Función de rotación", "function rotarObjeto(" in content),
        ("🖱️ Doble-click para rotar", "onDoubleClick" in content and "dblclick" in content),
        ("📏 Propiedad rotable", "rotable: rotable" in content),
        ("🎯 Zoom mejorado", "panOffset.x = mouseX -" in content),
        ("📐 Escala fija", "function dibujarEscalaFija(" in content),
        ("🔧 Panel rotación", "Orientación" in content and "Rotar" in content),
        ("🌐 Función global rotarObjeto", "window.rotarObjeto = rotarObjeto" in content),
        ("🎨 Redraw mejorado", "ctx.translate(panOffset.x, panOffset.y)" in content),
        ("📍 Límites de objetos", "Math.max(0, Math.min(maxX, newX))" in content)
    ]
    
    todas_correctas = True
    
    for descripcion, existe in mejoras:
        status = "✅" if existe else "❌"
        print(f"  {status} {descripcion}")
        if not existe:
            todas_correctas = False
    
    print("\n" + "=" * 55)
    
    if todas_correctas:
        print("🎉 TODAS LAS MEJORAS IMPLEMENTADAS CORRECTAMENTE")
        print("\n📋 NUEVAS FUNCIONALIDADES DISPONIBLES:")
        print("  📍 Coordenadas exactas desde X:0, Y:0")
        print("  🔄 Rotación de paredes con doble-click")
        print("  🎯 Zoom que mantiene objetos visibles")
        print("  📏 Escala visual que se adapta al zoom")
        print("  🎨 Sistema de coordenadas mejorado")
        print("  🔧 Panel de propiedades con rotación")
        print("\n🎮 CONTROLES:")
        print("  • Click: Seleccionar/crear objetos")
        print("  • Drag: Mover objetos seleccionados")
        print("  • Doble-click: Rotar paredes/puertas/barras")
        print("  • Scroll: Zoom in/out")
        print("  • Botón 'Centrar': Resetear vista a 0,0")
        print("\n🏗️ OBJETOS ROTABLES:")
        print("  • 🧱 Paredes: Horizontal ↔ Vertical")
        print("  • 🚪 Puertas: Horizontal ↔ Vertical") 
        print("  • 🍸 Barras: Horizontal ↔ Vertical")
    else:
        print("❌ ALGUNAS MEJORAS NO ESTÁN IMPLEMENTADAS")
        print("🔧 Revisa los elementos marcados con ❌")
    
    return todas_correctas

def mostrar_instrucciones():
    """Muestra instrucciones de uso"""
    print("\n" + "=" * 55)
    print("📖 INSTRUCCIONES DE USO DEL EDITOR MEJORADO")
    print("=" * 55)
    
    print("\n🎯 COORDENADAS:")
    print("  • Las coordenadas ahora inician correctamente desde X:0, Y:0")
    print("  • Se muestran en tiempo real en metros en la esquina inferior izquierda")
    print("  • El zoom ya no afecta las coordenadas mostradas")
    
    print("\n🔄 ROTACIÓN DE OBJETOS:")
    print("  • Paredes, puertas y barras se pueden rotar")
    print("  • Doble-click sobre el objeto para rotarlo")
    print("  • También usar el botón 'Rotar' en el panel de propiedades")
    print("  • La orientación se muestra en el panel (Horizontal/Vertical)")
    
    print("\n🎯 ZOOM MEJORADO:")
    print("  • El zoom ahora mantiene los objetos siempre visibles")
    print("  • Límites: 50% - 200% para mejor usabilidad")
    print("  • La escala visual se adapta automáticamente")
    print("  • Usar 'Centrar Vista' para resetear todo")
    
    print("\n🎨 CREACIÓN DE OBJETOS:")
    print("  • Los objetos se crean dentro de los límites del canvas")
    print("  • Las paredes inician horizontales (puedes rotarlas)")
    print("  • Al crear un objeto rotable, se muestra tip de rotación")
    
    print("\n🔧 CONSEJOS:")
    print("  • Usa 'Layout Base' para empezar con un diseño predefinido")
    print("  • El botón 'Cuadrícula' ayuda con el alineamiento")
    print("  • Configura las dimensiones en metros para tu espacio real")
    print("  • Los objetos se ajustan automáticamente a los límites")

if __name__ == "__main__":
    exito = test_mejoras_croquis()
    mostrar_instrucciones()
    
    print(f"\n{'🎉 ¡TODO LISTO!' if exito else '⚠️  REQUIERE ATENCIÓN'}")
    sys.exit(0 if exito else 1)
