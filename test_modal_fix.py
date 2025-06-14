#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup
import json

def test_modal_fix():
    print("=== PROBANDO FIX DEL MODAL DE INVENTARIO ===")
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # 1. Hacer login
    login_url = "http://127.0.0.1:8000/accounts/login/"
    
    # Primero obtener el formulario de login para el CSRF token
    response = session.get(login_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    
    if not csrf_token:
        print("❌ No se pudo obtener el token CSRF")
        return
    
    csrf_value = csrf_token['value']
    print(f"✅ Token CSRF obtenido: {csrf_value[:10]}...")
    
    # Hacer login
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrfmiddlewaretoken': csrf_value
    }
    
    response = session.post(login_url, data=login_data)
    if response.status_code == 200 and 'dashboard' in response.url:
        print("✅ Login exitoso")
    else:
        print(f"❌ Login falló. Status: {response.status_code}")
        return
    
    # 2. Obtener la página de inventario
    inventario_url = "http://127.0.0.1:8000/dashboard/inventario/"
    response = session.get(inventario_url)
    
    if response.status_code != 200:
        print(f"❌ Error accediendo al inventario: {response.status_code}")
        return
    
    print("✅ Página de inventario cargada")
    
    # 3. Extraer el primer insumo ID de la página
    soup = BeautifulSoup(response.content, 'html.parser')
    first_edit_btn = soup.find('button', {'class': 'btn-editar-insumo'})
    
    if not first_edit_btn:
        print("❌ No se encontró botón de editar insumo")
        return
    
    insumo_id = first_edit_btn.get('data-id')
    if not insumo_id:
        print("❌ No se pudo obtener el ID del insumo")
        return
    
    print(f"✅ ID del primer insumo encontrado: {insumo_id}")
    
    # 4. Hacer petición al endpoint de edición
    edit_url = f"http://127.0.0.1:8000/dashboard/insumos/editar/{insumo_id}/"
    
    # Añadir headers para simular petición AJAX
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json',
    }
    
    response = session.get(edit_url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Error en endpoint de edición: {response.status_code}")
        print(f"Contenido: {response.text}")
        return
    
    print("✅ Endpoint de edición respondió correctamente")
    
    # 5. Verificar los datos JSON
    try:
        data = response.json()
        print("✅ Respuesta JSON válida")
        
        # Verificar campos críticos
        categoria_nombre = data.get('categoria_nombre')
        unidad_medida_nombre = data.get('unidad_medida_nombre')
        
        print(f"\n=== RESULTADOS DEL TEST ===")
        print(f"categoria_nombre: '{categoria_nombre}'")
        print(f"unidad_medida_nombre: '{unidad_medida_nombre}'")
        
        # Verificar que no estén undefined o vacíos
        if categoria_nombre and categoria_nombre != 'undefined':
            print("✅ categoria_nombre está presente y válido")
        else:
            print("❌ categoria_nombre está vacío o undefined")
        
        if unidad_medida_nombre and unidad_medida_nombre != 'undefined':
            print("✅ unidad_medida_nombre está presente y válido")
        else:
            print("❌ unidad_medida_nombre está vacío o undefined")
            
        # Mostrar todos los datos para debugging
        print(f"\n=== DATOS COMPLETOS ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        return categoria_nombre and unidad_medida_nombre
        
    except json.JSONDecodeError as e:
        print(f"❌ Error decodificando JSON: {e}")
        print(f"Contenido: {response.text}")
        return False

if __name__ == "__main__":
    success = test_modal_fix()
    if success:
        print("\n🎉 ¡PRUEBA EXITOSA! El modal debería mostrar correctamente categoría y unidad.")
    else:
        print("\n❌ PRUEBA FALLÓ. Hay problemas con los datos del modal.")
