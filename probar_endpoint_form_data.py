import requests
import json
import os
import sys

def probar_endpoint():
    """
    Script para probar el endpoint de form-data
    """
    print("🔍 VERIFICANDO ENDPOINT DE DATOS DEL FORMULARIO")
    print("===============================================")
    
    # URL del endpoint
    base_url = "http://127.0.0.1:8000"
    form_data_url = f"{base_url}/dashboard/insumos/form-data/"
    
    try:
        # Intentar acceder al endpoint directamente
        print(f"Accediendo a {form_data_url}...")
        response = requests.get(form_data_url)
        
        if response.status_code == 200:
            print("✅ Conexión exitosa (Status 200)")
            
            try:
                data = response.json()
                print("\nDATOS RECIBIDOS:")
                print("----------------")
                print(json.dumps(data, indent=4, ensure_ascii=False))
                
                # Analizar los datos
                categorias = data.get('categorias', [])
                unidades = data.get('unidades', [])
                
                print(f"\nCategorías: {len(categorias)}")
                for i, cat in enumerate(categorias, 1):
                    print(f"  {i}. ID: {cat.get('id')}, Nombre: {cat.get('nombre')}")
                
                print(f"\nUnidades: {len(unidades)}")
                for i, uni in enumerate(unidades, 1):
                    print(f"  {i}. ID: {uni.get('id')}, Nombre: {uni.get('nombre')}, Abrev: {uni.get('abreviacion')}")
                
                # Verificar si hay datos
                if not categorias:
                    print("\n⚠️ ADVERTENCIA: No hay categorías en la respuesta")
                if not unidades:
                    print("\n⚠️ ADVERTENCIA: No hay unidades en la respuesta")
                
                return data
            except json.JSONDecodeError:
                print("❌ ERROR: La respuesta no es un JSON válido")
                print("Contenido de la respuesta:", response.text[:200] + "..." if len(response.text) > 200 else response.text)
        else:
            print(f"❌ ERROR: Status code {response.status_code}")
            print("Contenido de la respuesta:", response.text[:200] + "..." if len(response.text) > 200 else response.text)
    
    except requests.RequestException as e:
        print(f"❌ ERROR: Error de conexión: {str(e)}")
        print("Asegúrate de que el servidor Django esté ejecutándose")
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    return None

if __name__ == "__main__":
    print("Probando endpoint de datos del formulario...")
    probar_endpoint()
