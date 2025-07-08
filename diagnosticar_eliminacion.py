#!/usr/bin/env python
"""
Script para diagnosticar problemas con la eliminación de productos de venta
"""

import os
import sys
import django

# Configurar Django
sys.path.append('c:\\Users\\olcha\\Desktop\\sushi_restaurant - Copy (2)\\suchilitoo2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from restaurant.models import ProductoVenta
from django.test import Client
from django.contrib.auth import authenticate

User = get_user_model()

def diagnosticar_eliminacion():
    print("=== DIAGNÓSTICO DE ELIMINACIÓN DE PRODUCTOS ===\n")
    
    # 1. Verificar que existan productos para eliminar
    print("1. VERIFICANDO PRODUCTOS DISPONIBLES:")
    productos = ProductoVenta.objects.all()
    print(f"   Total de productos: {productos.count()}")
    
    if productos.exists():
        for i, producto in enumerate(productos[:3], 1):
            print(f"   {i}. ID: {producto.id}, Nombre: {producto.nombre}, Activo: {producto.disponible}")
    else:
        print("   ❌ No hay productos en la base de datos")
        return
    
    # 2. Verificar usuarios y permisos
    print("\n2. VERIFICANDO USUARIOS Y PERMISOS:")
    usuarios = User.objects.filter(is_active=True)
    print(f"   Total de usuarios activos: {usuarios.count()}")
    
    for usuario in usuarios:
        print(f"\n   Usuario: {usuario.username}")
        print(f"   - Superusuario: {usuario.is_superuser}")
        print(f"   - Staff: {usuario.is_staff}")
        print(f"   - Activo: {usuario.is_active}")
        
        # Verificar permisos específicos
        permisos_relevantes = [
            'restaurant.delete_productoventa',
            'restaurant.change_productoventa',
            'restaurant.view_productoventa',
            'restaurant.add_productoventa'
        ]
        
        print("   - Permisos:")
        for permiso in permisos_relevantes:
            tiene_permiso = usuario.has_perm(permiso)
            print(f"     * {permiso}: {'✓' if tiene_permiso else '❌'}")
        
        # Verificar grupos
        grupos = usuario.groups.all()
        if grupos:
            print(f"   - Grupos: {[grupo.name for grupo in grupos]}")
        else:
            print("   - Grupos: Ninguno")
    
    # 3. Verificar URL y vista
    print("\n3. VERIFICANDO CONFIGURACIÓN DE URL:")
    try:
        # Probar con el primer producto disponible
        primer_producto = productos.first()
        url_eliminar = reverse('dashboard:eliminar_producto_venta', kwargs={'producto_id': primer_producto.id})
        print(f"   URL de eliminación: {url_eliminar}")
        print(f"   ✓ URL generada correctamente para producto ID {primer_producto.id}")
    except Exception as e:
        print(f"   ❌ Error generando URL: {e}")
        return
    
    # 4. Simular solicitud de eliminación
    print("\n4. SIMULANDO SOLICITUD DE ELIMINACIÓN:")
    
    # Obtener un usuario con permisos
    usuario_admin = None
    for usuario in usuarios:
        if usuario.is_superuser or usuario.has_perm('restaurant.delete_productoventa'):
            usuario_admin = usuario
            break
    
    if not usuario_admin:
        print("   ❌ No se encontró ningún usuario con permisos de eliminación")
        
        # Crear un usuario admin si no existe
        print("   Creando usuario admin temporal...")
        try:
            usuario_admin = User.objects.create_user(
                username='admin_temp',
                password='admin123',
                is_superuser=True,
                is_staff=True
            )
            print(f"   ✓ Usuario admin temporal creado: {usuario_admin.username}")
        except Exception as e:
            print(f"   ❌ Error creando usuario admin: {e}")
            return
    
    print(f"   Usando usuario: {usuario_admin.username}")
    
    # Crear cliente de prueba
    client = Client()
    login_success = client.login(username=usuario_admin.username, password='admin123' if usuario_admin.username == 'admin_temp' else 'password')
    
    if not login_success:
        print("   ❌ No se pudo hacer login con el usuario")
        return
    
    print("   ✓ Login exitoso")
    
    # Probar solicitud GET (debería fallar)
    print("   Probando solicitud GET (debería fallar):")
    response_get = client.get(url_eliminar)
    print(f"   - Status Code GET: {response_get.status_code}")
    
    # Probar solicitud POST (debería funcionar)
    print("   Probando solicitud POST:")
    response_post = client.post(url_eliminar, {
        'csrfmiddlewaretoken': client.cookies.get('csrftoken', 'dummy')
    })
    print(f"   - Status Code POST: {response_post.status_code}")
    print(f"   - Redirección: {response_post.get('Location', 'N/A')}")
    
    # Verificar si el producto fue eliminado
    producto_existe = ProductoVenta.objects.filter(id=primer_producto.id).exists()
    print(f"   - Producto aún existe: {producto_existe}")
    
    if response_post.status_code in [200, 302] and not producto_existe:
        print("   ✓ Eliminación exitosa")
    else:
        print("   ❌ Problema en la eliminación")
        
        # Mostrar contenido de la respuesta si hay error
        if hasattr(response_post, 'content'):
            content = response_post.content.decode('utf-8')[:500]
            print(f"   Contenido de respuesta (primeros 500 chars): {content}")
    
    # 5. Verificar logs si están habilitados
    print("\n5. RECOMENDACIONES:")
    print("   - Verificar que el botón de eliminación esté usando método POST")
    print("   - Verificar que el token CSRF esté incluido")
    print("   - Verificar que el usuario tenga los permisos necesarios")
    print("   - Revisar los logs de Django para errores específicos")
    print("   - Verificar que la URL sea accesible desde el navegador")

if __name__ == '__main__':
    diagnosticar_eliminacion()
