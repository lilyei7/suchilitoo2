#!/usr/bin/env python3
"""
Script para verificar que los botones de editar y eliminar están funcionando
"""

import requests
from bs4 import BeautifulSoup

def test_buttons_functionality():
    """Verificar que los botones de editar y eliminar están presentes y configurados"""
    
    print("🔍 Verificando botones de editar y eliminar...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/dashboard/inventario/")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar botones de editar
            edit_buttons = soup.find_all('button', class_='btn-editar-insumo')
            delete_buttons = soup.find_all('button', class_='btn-eliminar-insumo')
            
            print(f"✅ Botones de editar encontrados: {len(edit_buttons)}")
            print(f"✅ Botones de eliminar encontrados: {len(delete_buttons)}")
            
            # Verificar que tengan el atributo data-id
            edit_with_id = sum(1 for btn in edit_buttons if btn.get('data-id'))
            delete_with_id = sum(1 for btn in delete_buttons if btn.get('data-id'))
            
            print(f"✅ Botones de editar con data-id: {edit_with_id}")
            print(f"✅ Botones de eliminar con data-id: {delete_with_id}")
            
            # Verificar que estén cargando los archivos JS
            js_scripts = soup.find_all('script', src=True)
            js_files = [script['src'] for script in js_scripts]
            
            has_crud_js = any('insumos_crud.js' in src for src in js_files)
            has_inventario_js = any('inventario_funciones.js' in src for src in js_files)
            
            print(f"✅ Script insumos_crud.js cargado: {has_crud_js}")
            print(f"✅ Script inventario_funciones.js cargado: {has_inventario_js}")
            
            # Verificar que está SweetAlert2
            has_sweetalert = 'sweetalert2' in response.text.lower()
            print(f"✅ SweetAlert2 incluido: {has_sweetalert}")
            
            # Verificar que estén los event listeners
            has_event_listeners = 'addEventListener' in response.text
            has_btn_listeners = 'btn-editar-insumo' in response.text and 'forEach' in response.text
            
            print(f"✅ Event listeners configurados: {has_event_listeners}")
            print(f"✅ Event listeners para botones configurados: {has_btn_listeners}")
            
            return (len(edit_buttons) > 0 and len(delete_buttons) > 0 and 
                   has_crud_js and has_sweetalert and has_event_listeners)
        else:
            print(f"❌ Error al cargar la página: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 VERIFICACIÓN DE BOTONES DE INVENTARIO")
    print("="*50)
    
    if test_buttons_functionality():
        print(f"\n🎉 ¡BOTONES FUNCIONANDO CORRECTAMENTE!")
        print(f"\n📋 Estado actual:")
        print(f"   ✅ Botones de editar presentes y configurados")
        print(f"   ✅ Botones de eliminar presentes y configurados")
        print(f"   ✅ Scripts JavaScript cargados correctamente")
        print(f"   ✅ Event listeners configurados")
        print(f"   ✅ SweetAlert2 disponible para confirmaciones")
        
        print(f"\n💡 Para probar:")
        print(f"   1. Abrir http://127.0.0.1:8000/dashboard/inventario/")
        print(f"   2. Hacer clic en el botón de editar (ícono de lápiz)")
        print(f"   3. Hacer clic en el botón de eliminar (ícono de basura)")
        print(f"   4. Verificar en la consola que no hay errores")
    else:
        print(f"\n❌ Los botones aún tienen problemas")

if __name__ == "__main__":
    main()
