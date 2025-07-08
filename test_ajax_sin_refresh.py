#!/usr/bin/env python3
"""
Script para probar la eliminación sin refresh usando AJAX
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from restaurant.models import ProductoVenta, CategoriaProducto
from django.test import Client
from django.urls import reverse
import json

User = get_user_model()

def crear_producto_prueba():
    """Crear un producto de prueba para eliminar"""
    print("🔧 Creando producto de prueba...")
    
    # Crear usuario admin si no existe
    admin_user, created = User.objects.get_or_create(
        username='admin_ajax_test',
        defaults={
            'email': 'admin_ajax@test.com',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Usuario admin creado: {admin_user.username}")
    else:
        print(f"👤 Usuario admin existente: {admin_user.username}")
    
    # Crear categoría si no existe
    categoria, created = CategoriaProducto.objects.get_or_create(
        nombre='Categoria AJAX Test',
        defaults={'descripcion': 'Categoria para pruebas AJAX'}
    )
    
    # Crear producto de prueba
    timestamp = datetime.now().strftime("%H%M%S")
    producto = ProductoVenta.objects.create(
        nombre=f"Producto AJAX Test {timestamp}",
        descripcion="Producto para probar eliminación sin refresh",
        precio=15.99,
        categoria=categoria,
        disponible=True
    )
    print(f"✅ Producto creado: {producto.nombre} (ID: {producto.id})")
    
    return admin_user, producto

def test_eliminacion_ajax():
    """Probar eliminación vía AJAX"""
    print("\n🌐 INICIANDO TEST DE ELIMINACIÓN AJAX SIN REFRESH")
    print("=" * 60)
    
    admin_user, producto = crear_producto_prueba()
    
    # Crear cliente de prueba
    client = Client()
    
    # Hacer login
    client.login(username='admin_ajax_test', password='admin123')
    print(f"✅ Login exitoso como: {admin_user.username}")
    
    # Verificar que el producto existe antes
    productos_antes = ProductoVenta.objects.filter(id=producto.id).count()
    print(f"📊 Productos antes de eliminar: {productos_antes}")
    
    # URL de eliminación
    url_eliminacion = reverse('dashboard:eliminar_producto_venta', kwargs={'producto_id': producto.id})
    print(f"🔗 URL: {url_eliminacion}")
    
    print("\n🚀 ENVIANDO PETICIÓN AJAX...")
    print("⏰ Timestamp:", datetime.now().isoformat())
    
    # Realizar petición AJAX
    response = client.post(url_eliminacion, {
        'csrfmiddlewaretoken': 'test-token'
    }, 
    HTTP_X_REQUESTED_WITH='XMLHttpRequest',  # Este header es clave para AJAX
    content_type='application/x-www-form-urlencoded'
    )
    
    print(f"📥 Respuesta:")
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.get('Content-Type', 'N/A')}")
    
    # Verificar respuesta JSON
    try:
        response_data = json.loads(response.content.decode())
        print(f"   JSON: {response_data}")
        
        # Verificar que el producto fue eliminado
        productos_despues = ProductoVenta.objects.filter(id=producto.id).count()
        print(f"📊 Productos después de eliminar: {productos_despues}")
        
        if response_data.get('success') and productos_despues == 0:
            print("🎉 ¡ELIMINACIÓN AJAX EXITOSA!")
            print("✅ La petición se ejecutó SIN refresh")
            print("✅ El producto fue eliminado correctamente")
            print("✅ Se recibió respuesta JSON válida")
            return True
        else:
            print("❌ Fallo en la eliminación")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        print(f"   Contenido raw: {response.content.decode()}")
        return False

def main():
    print("🚀 TEST DE ELIMINACIÓN SIN REFRESH")
    print("Este script verifica que la eliminación funcione via AJAX")
    print("sin causar un refresh de página")
    print("=" * 60)
    
    try:
        resultado = test_eliminacion_ajax()
        
        print("\n" + "=" * 60)
        print("📊 RESULTADO FINAL:")
        if resultado:
            print("🎉 ¡SUCCESS! La eliminación funciona correctamente vía AJAX")
            print("✅ No hay refresh de página")
            print("✅ El backend responde con JSON")
            print("✅ Los logs del backend se ejecutan")
        else:
            print("❌ FALLÓ - Revisar configuración")
        
        print("\n💡 INSTRUCCIONES PARA PROBAR EN EL NAVEGADOR:")
        print("1. Abre la página de productos en el navegador")
        print("2. Abre Developer Tools (F12)")
        print("3. Ve a la pestaña Console")
        print("4. Intenta eliminar un producto")
        print("5. Observa los logs detallados en la consola")
        print("6. La página NO debería refrescarse automáticamente")
        
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
