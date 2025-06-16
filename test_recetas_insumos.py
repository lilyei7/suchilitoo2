#!/usr/bin/env python3
"""
Script para probar el funcionamiento de la carga de insumos en la página de recetas
"""
import requests
import json
import argparse
from time import sleep

def test_recetas_insumos():
    """Probar la funcionalidad de carga de insumos para recetas"""
    print("🧪 Iniciando prueba de funcionalidad de insumos en recetas...")
    
    base_url = "http://127.0.0.1:8000/dashboard"
    
    try:
        # 1. Verificar que la URL principal de recetas funcione
        print("\n1. Comprobando acceso a la página de recetas...")
        response = requests.get(f"{base_url}/recetas/")
        if response.status_code == 200:
            print(f"   ✅ Página de recetas accesible (HTTP {response.status_code})")
        else:
            print(f"   ❌ Error accediendo a recetas (HTTP {response.status_code})")
            return False
        
        # 2. Verificar que la URL de API de insumos funcione
        print("\n2. Comprobando API de insumos para recetas...")
        headers = {'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
        response = requests.get(f"{base_url}/recetas/insumos/todos/", headers=headers)
        
        if response.status_code == 200:
            print(f"   ✅ API de insumos accesible (HTTP {response.status_code})")
            try:
                data = response.json()
                if data.get('success'):
                    insumos = data.get('insumos', [])
                    print(f"   📊 Total de insumos: {len(insumos)}")
                    
                    # Analizar tipos de insumos
                    tipos = {}
                    for insumo in insumos:
                        tipo = insumo.get('tipo', 'desconocido')
                        tipos[tipo] = tipos.get(tipo, 0) + 1
                    
                    for tipo, cantidad in tipos.items():
                        print(f"   - {tipo.capitalize()}: {cantidad}")
                    
                    # Mostrar algunos ejemplos
                    if insumos:
                        print("\n   📋 Ejemplos de insumos:")
                        for i, insumo in enumerate(insumos[:3]):  # Mostrar solo los primeros 3
                            print(f"   {i+1}. {insumo.get('nombre')} ({insumo.get('codigo')}) - ${insumo.get('precio_unitario')} por {insumo.get('unidad_medida')}")
                else:
                    print(f"   ⚠️ Respuesta con error: {data.get('message', 'Sin mensaje')}")
            except json.JSONDecodeError:
                print(f"   ❌ La respuesta no es JSON válido")
                print(f"   Contenido: {response.text[:150]}...")
        else:
            print(f"   ❌ Error accediendo a API de insumos (HTTP {response.status_code})")
            print(f"   Contenido: {response.text[:150]}...")
            return False
        
        print("\n✅ Pruebas completadas exitosamente")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión al servidor")
        print("   Asegúrate de que el servidor Django esté ejecutándose en http://127.0.0.1:8000")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Herramienta para probar la funcionalidad de recetas")
    parser.add_argument('--url', help="URL base para las pruebas", default="http://127.0.0.1:8000")
    
    args = parser.parse_args()
    
    success = test_recetas_insumos()
    
    if success:
        print("\n🎉 La funcionalidad de carga de insumos está configurada correctamente")
    else:
        print("\n⚠️ Se encontraron problemas en la funcionalidad")
        print("   Revisa los errores reportados y haz las correcciones necesarias")

if __name__ == "__main__":
    main()
