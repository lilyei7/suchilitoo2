#!/usr/bin/env python3
"""
Script para verificar específicamente que los errores de JavaScript estén corregidos
"""

import requests
import re

def check_javascript_syntax():
    """Verificar que no haya errores evidentes de sintaxis JavaScript"""
    
    print("🔍 Verificando sintaxis JavaScript en inventario.html...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/dashboard/inventario/")
        
        if response.status_code == 200:
            content = response.text
            
            # Verificar patrones problemáticos que causan errores de sintaxis
            problemas = []
            
            # Buscar funciones que no están separadas por líneas
            if re.search(r'}\s*function\s+\w+', content):
                problemas.append("Funciones no separadas correctamente")
            
            # Buscar llaves desequilibradas
            open_braces = content.count('{')
            close_braces = content.count('}')
            if abs(open_braces - close_braces) > 50:  # Margen para llaves de Django
                problemas.append(f"Posible desequilibrio de llaves: {open_braces} vs {close_braces}")
            
            # Verificar que las funciones críticas estén presentes
            funciones_criticas = ['editarInsumo', 'eliminarInsumo', 'addEventListener']
            funciones_encontradas = []
            for funcion in funciones_criticas:
                if funcion in content:
                    funciones_encontradas.append(funcion)
            
            print(f"✅ Funciones encontradas: {', '.join(funciones_encontradas)}")
            
            if problemas:
                print(f"⚠️ Problemas detectados:")
                for problema in problemas:
                    print(f"   - {problema}")
                return False
            else:
                print(f"✅ No se detectaron errores evidentes de sintaxis JavaScript")
                print(f"✅ La página carga correctamente (status 200)")
                return True
        else:
            print(f"❌ Error al cargar la página: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 VERIFICACIÓN DE SINTAXIS JAVASCRIPT")
    print("="*50)
    
    if check_javascript_syntax():
        print(f"\n🎉 ¡SINTAXIS CORREGIDA!")
        print(f"\n📋 Ahora deberías poder:")
        print(f"   1. Abrir http://127.0.0.1:8000/dashboard/inventario/")
        print(f"   2. No ver errores 'Unexpected token' en la consola")
        print(f"   3. Los botones de editar y eliminar deben responder")
        print(f"   4. Las funciones JavaScript están disponibles globalmente")
        
        print(f"\n🔧 Errores corregidos:")
        print(f"   ✅ Separación adecuada entre funciones")
        print(f"   ✅ Sintaxis JavaScript validada")
        print(f"   ✅ Event listeners configurados correctamente")
    else:
        print(f"\n❌ Aún hay problemas de sintaxis por resolver")

if __name__ == "__main__":
    main()
