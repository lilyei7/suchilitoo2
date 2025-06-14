#!/usr/bin/env python
"""
Script para probar las funcionalidades CRUD de insumos elaborados
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/dashboard"

def probar_endpoints():
    """Probar los endpoints de insumos elaborados"""
    print("🧪 Probando endpoints de insumos elaborados...")
    
    # Crear una sesión para mantener cookies
    session = requests.Session()
    
    try:
        # 1. Probar página principal de insumos elaborados
        print("\n1. 📋 Probando listado de insumos elaborados...")
        response = session.get(f"{BASE_URL}/insumos-elaborados/")
        if response.status_code == 200:
            print(f"   ✅ Listado cargado correctamente (200)")
            if "Roll California" in response.text:
                print(f"   ✅ Datos de ejemplo encontrados en el HTML")
            else:
                print(f"   ⚠️ No se encontraron datos de ejemplo en el HTML")
        else:
            print(f"   ❌ Error en listado ({response.status_code})")
        
        # 2. Probar endpoint de insumos compuestos
        print("\n2. 🔗 Probando endpoint de insumos compuestos...")
        response = session.get(f"{BASE_URL}/insumos-elaborados/insumos-compuestos/")
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    insumos = data.get('insumos', [])
                    print(f"   ✅ Endpoint funcional - {len(insumos)} insumos compuestos")
                    if insumos:
                        print(f"   📋 Ejemplo: {insumos[0]['nombre']} - ${insumos[0]['precio_unitario']}")
                else:
                    print(f"   ❌ Error en respuesta JSON: {data.get('message', 'Unknown')}")
            except json.JSONDecodeError:
                print(f"   ❌ Respuesta no es JSON válido")
        else:
            print(f"   ❌ Error en endpoint ({response.status_code})")
        
        # 3. Probar detalle de insumo elaborado
        print("\n3. 👁️ Probando detalle de insumo elaborado...")
        response = session.get(f"{BASE_URL}/insumos-elaborados/detalle/1/")
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    insumo = data.get('insumo', {})
                    componentes = data.get('componentes', [])
                    print(f"   ✅ Detalle obtenido: {insumo.get('nombre', 'N/A')}")
                    print(f"   🔧 Componentes: {len(componentes)}")
                    if componentes:
                        print(f"   📋 Primer componente: {componentes[0].get('nombre', 'N/A')}")
                else:
                    print(f"   ❌ Error en detalle: {data.get('message', 'Unknown')}")
            except json.JSONDecodeError:
                print(f"   ❌ Respuesta no es JSON válido")
        else:
            print(f"   ❌ Error en detalle ({response.status_code})")
          # 4. Probar estructura del formulario de creación
        print("\n4. 📝 Verificando estructura del template...")
        response = session.get(f"{BASE_URL}/insumos-elaborados/")        if response.status_code == 200:
            html_content = response.text
            elements_to_check = [
                'modalCrearElaborado',
                'formCrearElaborado',
                'componentesElaboradoContainer',
                'agregarComponenteElaborado',
                'calcularResumenElaborado',
            ]
            
            found_elements = []
            for element in elements_to_check:
                if element in html_content:
                    found_elements.append(element)
            
            print(f"   ✅ Elementos encontrados: {len(found_elements)}/{len(elements_to_check)}")
            for element in found_elements:
                print(f"      • {element}")
            
            if len(found_elements) < len(elements_to_check):
                missing = set(elements_to_check) - set(found_elements)
                print(f"   ⚠️ Elementos faltantes:")
                for element in missing:
                    print(f"      • {element}")
            
            # Verificar que existan los insumos elaborados de ejemplo
            if "Roll California" in html_content or "ELAB-001" in html_content:
                print(f"   ✅ Datos de ejemplo encontrados en el listado")
            else:
                print(f"   ⚠️ No se encontraron datos de ejemplo en el listado")
        
        print(f"\n✅ Pruebas de endpoints completadas")
        print(f"🌐 Abre http://127.0.0.1:8000/dashboard/insumos-elaborados/ para probar manualmente")
        print(f"🎯 Funcionalidades disponibles:")
        print(f"   • ✅ Listado de insumos elaborados")
        print(f"   • ✅ Ver detalles de insumos elaborados")
        print(f"   • ✅ Obtener insumos compuestos para formularios")
        print(f"   • 🔄 Crear nuevo insumo elaborado (probar manualmente)")
        print(f"   • 🔄 Editar insumo elaborado (probar manualmente)")
        print(f"   • 🔄 Eliminar insumo elaborado (probar manualmente)")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def mostrar_urls_importantes():
    """Mostrar URLs importantes del sistema"""
    print(f"\n🔗 URLs importantes del sistema:")
    print(f"   📊 Dashboard principal: http://127.0.0.1:8000/dashboard/")
    print(f"   🍱 Insumos compuestos: http://127.0.0.1:8000/dashboard/insumos-compuestos/")
    print(f"   🍣 Insumos elaborados: http://127.0.0.1:8000/dashboard/insumos-elaborados/")
    print(f"   📦 Inventario: http://127.0.0.1:8000/dashboard/inventario/")
    
    print(f"\n🎯 APIs de insumos elaborados:")
    print(f"   📋 Listar: GET /dashboard/insumos-elaborados/")
    print(f"   ➕ Crear: POST /dashboard/insumos-elaborados/crear/")
    print(f"   👁️ Ver: GET /dashboard/insumos-elaborados/detalle/<id>/")
    print(f"   ✏️ Editar: POST /dashboard/insumos-elaborados/editar/<id>/")
    print(f"   🗑️ Eliminar: POST /dashboard/insumos-elaborados/eliminar/<id>/")
    print(f"   🔗 Insumos compuestos: GET /dashboard/insumos-elaborados/insumos-compuestos/")

if __name__ == '__main__':
    probar_endpoints()
    mostrar_urls_importantes()
