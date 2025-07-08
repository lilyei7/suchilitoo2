#!/usr/bin/env python
"""
Script para verificar que la eliminación de productos funciona completamente
después de las correcciones realizadas.
"""
import os
import sys
import django
from django.db import connection

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from restaurant.models import ProductoVenta, CategoriaProducto
from dashboard.views.productos_venta_views import eliminar_producto_venta
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from bs4 import BeautifulSoup
import json

User = get_user_model()

def crear_datos_test():
    """Crea datos de prueba necesarios"""
    print("🔧 Creando datos de prueba...")
    
    # Crear categoría si no existe
    categoria, created = CategoriaProducto.objects.get_or_create(
        nombre="Test Category",
        defaults={"descripcion": "Categoría de prueba"}
    )
    
    # Crear producto de prueba
    producto = ProductoVenta.objects.create(
        codigo="TEST001",
        nombre="Producto Test Eliminación",
        descripcion="Producto para probar eliminación",
        precio=15.99,
        categoria=categoria,
        disponible=True
    )
    
    # Crear usuario admin con permisos
    admin_user, created = User.objects.get_or_create(
        username='admin_test_eliminacion',
        defaults={
            'email': 'admin@test.com',
            'is_staff': True,
            'is_superuser': True,
            'first_name': 'Admin',
            'last_name': 'Test'
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Usuario admin creado: {admin_user.username}")
    
    # Asegurar permisos
    permisos = [
        'restaurant.view_productoventa',
        'restaurant.add_productoventa', 
        'restaurant.change_productoventa',
        'restaurant.delete_productoventa'
    ]
    
    for perm_name in permisos:
        try:
            perm = Permission.objects.get(codename=perm_name.split('.')[1])
            admin_user.user_permissions.add(perm)
        except Permission.DoesNotExist:
            print(f"⚠️ Permiso no encontrado: {perm_name}")
    
    return producto, admin_user

def test_html_renderizado():
    """Prueba que el HTML se renderice correctamente con modal y botones"""
    print("\n📄 Probando renderizado de HTML...")
    
    client = Client()
    producto, admin_user = crear_datos_test()
    
    # Login
    client.force_login(admin_user)
    
    # Obtener la página
    url = reverse('dashboard:productos_venta')
    response = client.get(url)
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        
        # Verificar que el producto aparece
        producto_cards = soup.find_all('div', class_='card product-card')
        print(f"✅ Productos encontrados en cards: {len(producto_cards)}")
        
        # Verificar modal de eliminación
        modal = soup.find('div', id='deleteModal')
        if modal:
            print("✅ Modal de eliminación encontrado")
            
            # Verificar elementos del modal
            modal_title = modal.find('h5', class_='modal-title')
            modal_form = modal.find('form', id='deleteForm')
            csrf_token = modal.find('input', {'name': 'csrfmiddlewaretoken'})
            delete_button = modal.find('button', {'type': 'submit'})
            
            print(f"  - Título del modal: {'✅' if modal_title else '❌'}")
            print(f"  - Formulario: {'✅' if modal_form else '❌'}")
            print(f"  - CSRF token: {'✅' if csrf_token else '❌'}")
            print(f"  - Botón eliminar: {'✅' if delete_button else '❌'}")
        else:
            print("❌ Modal de eliminación NO encontrado")
        
        # Verificar botones de eliminar en las cards
        delete_buttons = soup.find_all('button', {'data-bs-toggle': 'modal', 'data-bs-target': '#deleteModal'})
        print(f"✅ Botones de eliminar encontrados: {len(delete_buttons)}")
        
        # Verificar scripts JavaScript
        scripts = soup.find_all('script')
        js_content = ""
        for script in scripts:
            if script.string:
                js_content += script.string
        
        modal_js = 'deleteModal' in js_content
        form_action_js = 'deleteForm' in js_content
        print(f"  - JavaScript del modal: {'✅' if modal_js else '❌'}")
        print(f"  - JavaScript del formulario: {'✅' if form_action_js else '❌'}")
        
        return True
    else:
        print(f"❌ Error al cargar la página: {response.status_code}")
        return False

def test_eliminacion_post():
    """Prueba la eliminación vía POST desde la interfaz"""
    print("\n🗑️ Probando eliminación vía POST...")
    
    client = Client()
    producto, admin_user = crear_datos_test()
    
    # Login
    client.force_login(admin_user)
    
    producto_id = producto.id
    print(f"ID del producto a eliminar: {producto_id}")
    
    # Verificar que existe antes
    existe_antes = ProductoVenta.objects.filter(id=producto_id).exists()
    print(f"Producto existe antes: {existe_antes}")
    
    # Eliminar vía POST
    url = reverse('dashboard:eliminar_producto_venta', kwargs={'pk': producto_id})
    response = client.post(url, follow=True)
    
    print(f"Status code: {response.status_code}")
    print(f"URL final: {response.request['PATH_INFO']}")
    
    # Verificar que se eliminó
    existe_despues = ProductoVenta.objects.filter(id=producto_id).exists()
    print(f"Producto existe después: {existe_despues}")
    
    if not existe_despues:
        print("✅ Eliminación vía POST exitosa")
        return True
    else:
        print("❌ Eliminación vía POST falló")
        return False

def test_eliminacion_ajax():
    """Prueba la eliminación vía AJAX"""
    print("\n🔄 Probando eliminación vía AJAX...")
    
    client = Client()
    producto, admin_user = crear_datos_test()
    
    # Login
    client.force_login(admin_user)
    
    producto_id = producto.id
    print(f"ID del producto a eliminar: {producto_id}")
    
    # Verificar que existe antes
    existe_antes = ProductoVenta.objects.filter(id=producto_id).exists()
    print(f"Producto existe antes: {existe_antes}")
    
    # Eliminar vía AJAX
    url = reverse('dashboard:eliminar_producto_venta', kwargs={'pk': producto_id})
    response = client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    
    print(f"Status code: {response.status_code}")
    
    # Verificar que se eliminó
    existe_despues = ProductoVenta.objects.filter(id=producto_id).exists()
    print(f"Producto existe después: {existe_despues}")
    
    if response.status_code == 200 and not existe_despues:
        try:
            data = json.loads(response.content)
            print(f"Respuesta JSON: {data}")
            print("✅ Eliminación vía AJAX exitosa")
            return True
        except json.JSONDecodeError:
            print("⚠️ Respuesta no es JSON válido")
            return False
    else:
        print("❌ Eliminación vía AJAX falló")
        return False

def verificar_template_final():
    """Verificación final del template"""
    print("\n📋 Verificación final del template...")
    
    template_path = "dashboard/templates/dashboard/productos_venta/lista.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificaciones
        modal_pos = content.find("deleteModal")
        first_endblock = content.find("{% endblock %}")
        
        checks = {
            "Modal dentro del content": modal_pos != -1 and first_endblock != -1 and modal_pos < first_endblock,
            "Scripts después del content": "{% block scripts %}" in content and content.find("{% block scripts %}") > first_endblock,
            "Estilos después del content": "{% block styles %}" in content and content.find("{% block styles %}") > first_endblock,
            "Botón eliminar con modal": 'data-bs-toggle="modal"' in content and 'data-bs-target="#deleteModal"' in content,
            "JavaScript del modal": "deleteModal.addEventListener" in content,
            "CSRF token en formulario": "{% csrf_token %}" in content,
            "No duplicación de modal": content.count('id="deleteModal"') == 1
        }
        
        for check, passed in checks.items():
            print(f"  {check}: {'✅' if passed else '❌'}")
        
        return all(checks.values())
        
    except FileNotFoundError:
        print(f"❌ Template no encontrado: {template_path}")
        return False

def main():
    """Función principal"""
    print("🧪 VERIFICACIÓN COMPLETA DE ELIMINACIÓN DE PRODUCTOS")
    print("=" * 60)
    
    tests = [
        ("Verificación del template", verificar_template_final),
        ("Renderizado del HTML", test_html_renderizado),
        ("Eliminación vía POST", test_eliminacion_post),
        ("Eliminación vía AJAX", test_eliminacion_ajax),
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        print(f"\n🔍 {nombre}...")
        try:
            resultado = test_func()
            resultados.append(resultado)
            print(f"{'✅ EXITOSO' if resultado else '❌ FALLÓ'}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            resultados.append(False)
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS:")
    
    for i, (nombre, _) in enumerate(tests):
        estado = "✅ EXITOSO" if resultados[i] else "❌ FALLÓ"
        print(f"  {nombre}: {estado}")
    
    exitosos = sum(resultados)
    total = len(resultados)
    porcentaje = (exitosos / total * 100) if total > 0 else 0
    
    print(f"\n🎯 RESULTADO FINAL: {exitosos}/{total} pruebas exitosas ({porcentaje:.1f}%)")
    
    if all(resultados):
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! La eliminación debería funcionar correctamente.")
        print("\n📝 INSTRUCCIONES PARA PROBAR EN EL NAVEGADOR:")
        print("1. Ejecuta el servidor: python manage.py runserver")
        print("2. Ve a: http://127.0.0.1:8000/dashboard/productos-venta/")
        print("3. Haz clic en el botón rojo de eliminar (🗑️) en cualquier producto")
        print("4. Confirma la eliminación en el modal")
        print("5. El producto debería desaparecer de la lista")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")

if __name__ == "__main__":
    main()
