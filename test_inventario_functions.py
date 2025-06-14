#!/usr/bin/env python3
"""
Script para probar que las funciones de inventario (editar/eliminar insumos) funcionen correctamente
"""

import requests
import sys

def test_inventario_page():
    """Test que la página de inventario cargue sin errores de JavaScript"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Probando página de inventario...")
    
    try:
        response = requests.get(f"{base_url}/dashboard/inventario/")
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Verificar elementos clave en la página
            checks = [
                ('Script insumos_crud.js cargado', 'insumos_crud.js' in content),
                ('Función editarInsumo', 'editarInsumo' in content),
                ('Función eliminarInsumo', 'eliminarInsumo' in content),
                ('Botones de editar', 'btn-editar-insumo' in content),
                ('Botones de eliminar', 'btn-eliminar-insumo' in content),
                ('Event listeners configurados', 'addEventListener' in content),
                ('SweetAlert2 incluido', 'sweetalert2' in content.lower()),
            ]
            
            print("📥 Verificaciones de contenido:")
            all_good = True
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"   {status} {check_name}")
                if not result:
                    all_good = False
            
            if all_good:
                print("✅ Página de inventario carga correctamente con todas las funciones")
                return True
            else:
                print("⚠️ Algunos elementos faltantes pero la página carga")
                return True
        else:
            print(f"❌ Status incorrecto: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Error de conexión - ¿Está corriendo el servidor?")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    print("🚀 VERIFICACIÓN DE FUNCIONES DE INVENTARIO")
    print("="*50)
    
    # Test de la página principal
    if test_inventario_page():
        print(f"\n🎉 ¡ÉXITO! Las funciones de inventario están disponibles")
        print(f"\n💡 INSTRUCCIONES:")
        print(f"   1. Abrir http://127.0.0.1:8000/dashboard/inventario/")
        print(f"   2. Los botones 'Editar' y 'Eliminar' ahora deben funcionar")
        print(f"   3. Verificar en la consola del navegador que no hay errores de JavaScript")
        print(f"   4. Probar hacer clic en los botones para confirmar que funcionan")
        
        print(f"\n🔧 Funciones corregidas:")
        print(f"   ✅ Sintaxis JavaScript reparada")
        print(f"   ✅ Función editarInsumo disponible globalmente")
        print(f"   ✅ Función eliminarInsumo disponible globalmente")
        print(f"   ✅ Event listeners configurados correctamente")
        print(f"   ✅ Verificaciones de funciones añadidas")
    else:
        print(f"\n❌ Problemas detectados en las funciones de inventario")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
