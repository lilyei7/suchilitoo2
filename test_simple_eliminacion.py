#!/usr/bin/env python
"""
Script simplificado para verificar que la corrección del modal funciona.
"""
import os
import sys
import django
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from restaurant.models import ProductoVenta, CategoriaProducto
from django.urls import reverse
from bs4 import BeautifulSoup

User = get_user_model()

def test_simple():
    """Test simplificado del frontend"""
    print("🧪 TEST SIMPLIFICADO DE ELIMINACIÓN")
    print("=" * 50)
    
    # Crear datos básicos
    categoria, _ = CategoriaProducto.objects.get_or_create(
        nombre="Test Category Simple",
        defaults={"descripcion": "Categoría de prueba"}
    )
    
    # Crear producto con código único
    codigo_unico = f"TEST{random.randint(1000, 9999)}"
    producto = ProductoVenta.objects.create(
        codigo=codigo_unico,
        nombre="Producto Test Simple",
        descripcion="Test",
        precio=10.00,
        categoria=categoria,
        disponible=True
    )
    
    # Crear usuario admin
    admin_user, created = User.objects.get_or_create(
        username='admin_simple',
        defaults={
            'email': 'admin@simple.com',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
    
    # Test del cliente
    client = Client()
    client.force_login(admin_user)
    
    print(f"✅ Producto creado: {producto.nombre} (ID: {producto.id})")
    
    # Obtener la página
    try:
        url = reverse('dashboard:lista_productos_venta')
        print(f"URL: {url}")
        
        response = client.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Verificar elementos clave
            modal = soup.find('div', id='deleteModal')
            delete_buttons = soup.find_all('button', {'data-bs-toggle': 'modal'})
            
            print(f"🔍 Modal encontrado: {'✅' if modal else '❌'}")
            print(f"🔍 Botones eliminar: {len(delete_buttons)} encontrados")
            
            if modal and delete_buttons:
                print("✅ FRONTEND FUNCIONANDO CORRECTAMENTE")
                
                # Test de eliminación
                print("\n🗑️ Probando eliminación...")
                delete_url = reverse('dashboard:eliminar_producto_venta', kwargs={'producto_id': producto.id})
                delete_response = client.post(delete_url, follow=True)
                
                existe_despues = ProductoVenta.objects.filter(id=producto.id).exists()
                print(f"Producto eliminado: {'✅' if not existe_despues else '❌'}")
                
                if not existe_despues:
                    print("🎉 ¡ELIMINACIÓN EXITOSA!")
                    return True
            else:
                print("❌ Frontend con problemas")
                
        else:
            print(f"❌ Error en la página: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

def verificar_template_estructura():
    """Verificar la estructura del template manualmente"""
    print("\n📄 VERIFICANDO ESTRUCTURA DEL TEMPLATE")
    print("=" * 50)
    
    template_path = "dashboard/templates/dashboard/productos_venta/lista.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar posiciones clave
        lines = content.split('\n')
        
        modal_line = None
        endblock_line = None
        
        for i, line in enumerate(lines):
            if 'id="deleteModal"' in line and modal_line is None:
                modal_line = i + 1
            if '{% endblock %}' in line and endblock_line is None:
                endblock_line = i + 1
        
        print(f"Modal en línea: {modal_line}")
        print(f"Primer endblock en línea: {endblock_line}")
        
        if modal_line and endblock_line:
            if modal_line < endblock_line:
                print("✅ Modal está DENTRO del bloque content")
                return True
            else:
                print("❌ Modal está FUERA del bloque content")
                return False
        else:
            print("❌ No se encontraron elementos clave")
            return False
            
    except FileNotFoundError:
        print(f"❌ Template no encontrado: {template_path}")
        return False

def main():
    estructura_ok = verificar_template_estructura()
    frontend_ok = test_simple()
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN:")
    print(f"Estructura del template: {'✅' if estructura_ok else '❌'}")
    print(f"Funcionalidad frontend: {'✅' if frontend_ok else '❌'}")
    
    if estructura_ok and frontend_ok:
        print("\n🎉 ¡TODO FUNCIONANDO CORRECTAMENTE!")
        print("\n📝 PRÓXIMOS PASOS:")
        print("1. Ejecuta: python manage.py runserver")
        print("2. Ve a: http://127.0.0.1:8000/dashboard/productos-venta/")
        print("3. Prueba eliminar un producto desde la interfaz")
    else:
        print("\n⚠️ Hay problemas por resolver")

if __name__ == "__main__":
    main()
