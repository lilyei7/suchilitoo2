#!/usr/bin/env python
"""
Script para probar la eliminación de productos y verificar logs
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

User = get_user_model()

def crear_producto_test():
    """Crear un producto de prueba para eliminar"""
    categoria, _ = CategoriaProducto.objects.get_or_create(
        nombre="Test Logs Category",
        defaults={"descripcion": "Categoría para pruebas de logs"}
    )
    
    codigo_unico = f"LOGS{random.randint(1000, 9999)}"
    producto = ProductoVenta.objects.create(
        codigo=codigo_unico,
        nombre="Producto Test Logs",
        descripcion="Producto para probar logs de eliminación",
        precio=25.99,
        categoria=categoria,
        disponible=True
    )
    
    print(f"✅ Producto creado: {producto.nombre} (ID: {producto.id}, Código: {producto.codigo})")
    return producto

def crear_usuario_admin():
    """Crear o obtener usuario admin"""
    admin_user, created = User.objects.get_or_create(
        username='admin_logs',
        defaults={
            'email': 'admin@logs.com',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Usuario admin creado: {admin_user.username}")
    else:
        print(f"✅ Usuario admin encontrado: {admin_user.username}")
    
    return admin_user

def test_eliminacion_con_logs():
    """Probar eliminación y mostrar logs"""
    print("🚀 INICIANDO PRUEBA DE ELIMINACIÓN CON LOGS")
    print("=" * 60)
    
    # Crear datos de prueba
    producto = crear_producto_test()
    admin_user = crear_usuario_admin()
    
    # Cliente de prueba
    client = Client()
    client.force_login(admin_user)
    
    print(f"\n📋 DATOS DE LA PRUEBA:")
    print(f"- Usuario: {admin_user.username}")
    print(f"- Producto: {producto.nombre} (ID: {producto.id})")
    print(f"- URL de eliminación: /dashboard/productos-venta/{producto.id}/eliminar/")
    
    print(f"\n📡 ENVIANDO PETICIÓN POST PARA ELIMINAR...")
    print("⚠️  OBSERVA LOS LOGS EN LA TERMINAL DEL SERVIDOR DJANGO")
    print("⚠️  Los logs aparecerán con emojis para facilitar el seguimiento")
    
    # Realizar la eliminación
    url = reverse('dashboard:eliminar_producto_venta', kwargs={'producto_id': producto.id})
    
    print(f"\n🔗 URL exacta: {url}")
    print(f"🔄 Enviando petición POST...")
    
    try:
        response = client.post(url, follow=True)
        
        print(f"\n📥 RESPUESTA RECIBIDA:")
        print(f"- Status code: {response.status_code}")
        print(f"- URL final: {response.request['PATH_INFO']}")
        print(f"- Content type: {response.get('Content-Type', 'N/A')}")
        
        # Verificar si el producto fue eliminado
        existe_despues = ProductoVenta.objects.filter(id=producto.id).exists()
        print(f"- Producto existe después: {existe_despues}")
        
        if response.status_code == 200 and not existe_despues:
            print("\n🎉 ¡ELIMINACIÓN EXITOSA!")
        elif response.status_code != 200:
            print(f"\n❌ Error en la respuesta: {response.status_code}")
        elif existe_despues:
            print(f"\n❌ El producto no fue eliminado")
        
    except Exception as e:
        print(f"\n💥 Error durante la prueba: {e}")
    
    print(f"\n" + "=" * 60)
    print("📝 INSTRUCCIONES:")
    print("1. Revisa los logs en la terminal del servidor Django")
    print("2. Busca los logs que empiecen con 🚀🚀🚀")
    print("3. Sigue la secuencia de emojis para entender el flujo")
    print("4. Los logs te dirán exactamente dónde está el problema")

if __name__ == "__main__":
    test_eliminacion_con_logs()
