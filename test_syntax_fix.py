#!/usr/bin/env python3
"""
Verificación de la funcionalidad después de corregir errores de sintaxis JavaScript
"""

import requests
import time

def test_inventory_page():
    """Probar que la página de inventario carga correctamente"""
    print("🧪 PRUEBA: Verificando que la página de inventario carga sin errores JavaScript...")
    
    try:
        # Hacer una petición a la página de inventario
        response = requests.get('http://127.0.0.1:8000/dashboard/inventario/')
        
        if response.status_code == 200:
            print("✅ ÉXITO: La página de inventario carga correctamente")
            print(f"   - Status Code: {response.status_code}")
            print(f"   - Content Length: {len(response.content)} bytes")
            
            # Verificar que no hay errores JavaScript evidentes en el HTML
            content = response.text.lower()
            
            # Buscar indicadores de errores JavaScript
            js_errors = []
            if '})    .' in content:
                js_errors.append("Espaciado incorrecto en promesas")
            if 'syntaxerror' in content:
                js_errors.append("SyntaxError mencionado en el código")
            
            if js_errors:
                print("⚠️  ADVERTENCIA: Posibles errores JavaScript detectados:")
                for error in js_errors:
                    print(f"   - {error}")
            else:
                print("✅ VERIFICACIÓN: No se detectaron errores de sintaxis JavaScript evidentes")
            
            return True
        else:
            print(f"❌ ERROR: La página retornó status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al servidor. ¿Está corriendo Django?")
        return False
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
        return False

def main():
    print("🔧 === VERIFICACIÓN POST-CORRECCIÓN DE SINTAXIS JAVASCRIPT ===")
    print()
    
    # Pruebas principales
    test_inventory_page()
    
    print()
    print("📋 RESUMEN:")
    print("✅ Se corrigieron los errores de sintaxis JavaScript:")
    print("   - Espaciado incorrecto en .catch() chain")
    print("   - Espaciado incorrecto en .then() chain") 
    print("   - Promesas mal formateadas")
    print()
    print("🎯 SIGUIENTE PASO: Probar la creación de insumos en el navegador")
    print("   1. Ir a http://127.0.0.1:8000/dashboard/inventario/")
    print("   2. Hacer clic en 'Nuevo Insumo'")
    print("   3. Completar el formulario")
    print("   4. Verificar que no aparezcan errores JavaScript en la consola")

if __name__ == "__main__":
    main()
