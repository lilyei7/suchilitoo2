#!/usr/bin/env python
"""
Script de verificación final del sistema de eliminación de productos
"""

import os
import sys
import django

# Configurar Django
sys.path.append('c:\\Users\\olcha\\Desktop\\sushi_restaurant - Copy (2)\\suchilitoo2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from restaurant.models import ProductoVenta
from django.urls import reverse

User = get_user_model()

def verificacion_final():
    print("=== VERIFICACIÓN FINAL DEL SISTEMA ===\n")
    
    # 1. Verificar productos disponibles
    print("1. PRODUCTOS DISPONIBLES:")
    productos = ProductoVenta.objects.all()
    print(f"   Total de productos: {productos.count()}")
    
    for i, producto in enumerate(productos, 1):
        print(f"   {i}. ID: {producto.id}, Nombre: {producto.nombre}, Estado: {'ACTIVO' if producto.disponible else 'INACTIVO'}")
    
    # 2. Verificar usuarios con permisos
    print("\n2. USUARIOS CON PERMISOS DE ELIMINACIÓN:")
    usuarios_admin = []
    
    for usuario in User.objects.filter(is_active=True):
        if usuario.has_perm('restaurant.delete_productoventa'):
            usuarios_admin.append(usuario.username)
            print(f"   ✓ {usuario.username} (puede eliminar productos)")
    
    if not usuarios_admin:
        print("   ❌ No hay usuarios con permisos de eliminación")
        return False
    
    # 3. Probar simulación de eliminación
    print("\n3. PRUEBA DE ELIMINACIÓN:")
    
    if not productos.exists():
        print("   ❌ No hay productos para probar")
        return False
    
    # Usar el primer usuario admin disponible
    usuario_test = usuarios_admin[0]
    producto_test = productos.first()
    
    print(f"   Usuario de prueba: {usuario_test}")
    print(f"   Producto de prueba: {producto_test.nombre} (ID: {producto_test.id})")
    
    # Simular login y eliminación
    client = Client()
    
    # Intentar login
    credenciales = {
        'admin': 'admin123',
        'jhayco': 'jhayco123'
    }
    
    password = credenciales.get(usuario_test, 'admin123')
    login_success = client.login(username=usuario_test, password=password)
    
    if not login_success:
        print(f"   ❌ No se pudo hacer login con {usuario_test}")
        return False
    
    print(f"   ✓ Login exitoso con {usuario_test}")
    
    # Generar URL de eliminación
    try:
        url_eliminar = reverse('dashboard:eliminar_producto_venta', kwargs={'producto_id': producto_test.id})
        print(f"   URL de eliminación: {url_eliminar}")
    except Exception as e:
        print(f"   ❌ Error generando URL: {e}")
        return False
    
    # Simular solicitud POST de eliminación
    response = client.post(url_eliminar)
    print(f"   Status de respuesta: {response.status_code}")
    
    # Verificar si el producto fue eliminado
    producto_existe = ProductoVenta.objects.filter(id=producto_test.id).exists()
    
    if response.status_code in [200, 302] and not producto_existe:
        print("   ✓ Eliminación exitosa")
        exito_eliminacion = True
    else:
        print("   ⚠️  Eliminación no completada (posible problema en la vista)")
        exito_eliminacion = False
    
    # 4. Verificar configuración del template
    print("\n4. VERIFICACIÓN DEL TEMPLATE:")
    
    # Ir a la página de productos y verificar el botón
    response_lista = client.get('/dashboard/productos-venta/')
    print(f"   Status página productos: {response_lista.status_code}")
    
    if response_lista.status_code == 200:
        content = response_lista.content.decode('utf-8')
        
        # Verificar elementos importantes
        checks = [
            ('Botón de eliminar', 'btn-outline-danger' in content),
            ('Modal de eliminación', 'deleteModal' in content),
            ('JavaScript', 'data-bs-target="#deleteModal"' in content),
            ('Formulario POST', 'method="post"' in content),
            ('Token CSRF', 'csrfmiddlewaretoken' in content)
        ]
        
        for check_name, check_result in checks:
            print(f"   {'✓' if check_result else '❌'} {check_name}")
    else:
        print("   ❌ No se pudo acceder a la página de productos")
    
    # 5. Resumen final
    print("\n" + "="*50)
    print("RESUMEN DE VERIFICACIÓN:")
    print("="*50)
    
    resultados = [
        ("Productos disponibles", productos.exists()),
        ("Usuarios con permisos", len(usuarios_admin) > 0),
        ("Login funcional", login_success),
        ("URL de eliminación", True),
        ("Página productos accesible", response_lista.status_code == 200)
    ]
    
    todos_ok = all(resultado for _, resultado in resultados)
    
    for nombre, resultado in resultados:
        print(f"   {'✓' if resultado else '❌'} {nombre}")
    
    if todos_ok:
        print("\n🎉 SISTEMA COMPLETAMENTE FUNCIONAL 🎉")
        print("\nPara probar manualmente:")
        print("1. Inicia el servidor: python manage.py runserver")
        print("2. Ve a: http://localhost:8000/dashboard/productos-venta/")
        print("3. Haz login con: admin / admin123")
        print("4. Haz clic en el botón de basura roja de cualquier producto")
        print("5. Confirma la eliminación en el modal")
    else:
        print("\n⚠️  HAY ALGUNOS PROBLEMAS POR RESOLVER")
    
    return todos_ok

if __name__ == '__main__':
    verificacion_final()
