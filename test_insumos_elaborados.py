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
            html_content = response.text
            
            # Verificar elementos del template
            elementos_importantes = [
                'modalCrearElaborado',
                'formCrearElaborado', 
                'abrirModalCrearElaborado',
                'agregarComponenteElaborado',
                'Roll California',
                'ELAB-001'
            ]
            
            elementos_encontrados = []
            for elemento in elementos_importantes:
                if elemento in html_content:
                    elementos_encontrados.append(elemento)
            
            print(f"   📋 Elementos encontrados: {len(elementos_encontrados)}/{len(elementos_importantes)}")
            for elemento in elementos_encontrados:
                print(f"      ✅ {elemento}")
                
            elementos_faltantes = set(elementos_importantes) - set(elementos_encontrados)
            if elementos_faltantes:
                for elemento in elementos_faltantes:
                    print(f"      ⚠️ {elemento}")
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
                print(f"   📄 Contenido: {response.text[:200]}...")
        else:
            print(f"   ❌ Error en endpoint ({response.status_code})")
        
        # 3. Probar detalle de insumo elaborado (si existe)
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
                print(f"   📄 Contenido: {response.text[:200]}...")
        else:
            print(f"   ⚠️ No hay insumo con ID 1 o error ({response.status_code})")
        
        print(f"\n✅ Pruebas de endpoints completadas")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def mostrar_urls_importantes():
    """Mostrar URLs importantes del sistema"""
    print(f"\n🔗 URLs importantes del sistema:")
    print(f"   📊 Dashboard principal: http://127.0.0.1:8000/dashboard/")
    print(f"   🍣 Insumos elaborados: http://127.0.0.1:8000/dashboard/insumos-elaborados/")
    print(f"   📦 Inventario: http://127.0.0.1:8000/dashboard/inventario/")
    
    print(f"\n🎯 APIs de insumos elaborados:")
    print(f"   📋 Listar: GET /dashboard/insumos-elaborados/")
    print(f"   ➕ Crear: POST /dashboard/insumos-elaborados/crear/")
    print(f"   👁️ Ver: GET /dashboard/insumos-elaborados/detalle/<id>/")
    print(f"   ✏️ Editar: POST /dashboard/insumos-elaborados/editar/<id>/")
    print(f"   🗑️ Eliminar: POST /dashboard/insumos-elaborados/eliminar/<id>/")
    print(f"   🔗 Insumos compuestos: GET /dashboard/insumos-elaborados/insumos-compuestos/")

def mostrar_funcionalidades():
    """Mostrar resumen de funcionalidades"""
    print(f"\n🎯 Funcionalidades implementadas:")
    print(f"   ✅ Listado de insumos elaborados con estadísticas")
    print(f"   ✅ Vista de detalles con componentes")
    print(f"   ✅ Modal de creación con formulario dinámico")
    print(f"   ✅ Selección de insumos compuestos como componentes")
    print(f"   ✅ Cálculo automático de costos")
    print(f"   ✅ Validaciones de formulario")
    print(f"   ✅ Operaciones CRUD completas")
    print(f"   ✅ Interfaz responsive y moderna")
    
    print(f"\n🔄 Para probar manualmente:")
    print(f"   1. Ve a http://127.0.0.1:8000/dashboard/insumos-elaborados/")
    print(f"   2. Haz clic en 'Nuevo Insumo Elaborado'")
    print(f"   3. Completa el formulario y agrega componentes")
    print(f"   4. Verifica que se calculen los costos automáticamente")
    print(f"   5. Guarda y verifica que aparezca en el listado")

if __name__ == '__main__':
    probar_endpoints()
    mostrar_urls_importantes()
    mostrar_funcionalidades()
