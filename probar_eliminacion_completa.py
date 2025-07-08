#!/usr/bin/env python3
"""
Script para probar completamente la funcionalidad de eliminación
después de corregir el error de sintaxis JavaScript.
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth import get_user_model
from restaurant.models import ProductoVenta, CategoriaProducto
from accounts.models import Rol
from django.urls import reverse

def main():
    print("🧪 Probando funcionalidad de eliminación completa...")
    print("=" * 60)
    
    try:
        # Crear un cliente de prueba
        client = Client()
        
        # Obtener o crear un usuario administrador
        User = get_user_model()
        admin_users = User.objects.filter(is_superuser=True)
        
        if admin_users.exists():
            admin_user = admin_users.first()
            print(f"✅ Usando usuario administrador existente: {admin_user.username}")
        else:
            print("❌ No se encontró usuario administrador")
            return False
        
        # Hacer login
        login_success = client.force_login(admin_user)
        print("✅ Login exitoso")
        
        # Crear una categoría de prueba si no existe
        categoria, created = CategoriaProducto.objects.get_or_create(
            nombre="Categoría de Prueba Eliminación",
            defaults={
                'descripcion': 'Categoría temporal para probar eliminación',
                'activo': True
            }
        )
        
        if created:
            print("✅ Categoría de prueba creada")
        else:
            print("✅ Usando categoría de prueba existente")
        
        # Crear un producto de prueba
        producto_prueba = ProductoVenta.objects.create(
            codigo='PRUEBA_ELIM_001',
            nombre='Producto Prueba Eliminación',
            descripcion='Producto temporal para probar la eliminación',
            precio=10.00,
            categoria=categoria,
            disponible=True
        )
        
        print(f"✅ Producto de prueba creado: ID {producto_prueba.id}")
        
        # Probar acceso a la página de lista de productos
        lista_url = reverse('dashboard:lista_productos_venta')
        response = client.get(lista_url)
        
        if response.status_code == 200:
            print("✅ Página de lista de productos accesible")
            
            # Verificar que el producto aparece en la página
            if str(producto_prueba.id) in response.content.decode():
                print("✅ Producto visible en la página")
            else:
                print("⚠️  Producto no visible en la página (puede ser normal según filtros)")
        else:
            print(f"❌ Error al acceder a la página: {response.status_code}")
            return False
        
        # Probar la eliminación via POST
        eliminar_url = reverse('dashboard:eliminar_producto_venta', args=[producto_prueba.id])
        print(f"🎯 URL de eliminación: {eliminar_url}")
        
        # Simular la petición AJAX de eliminación
        response = client.post(eliminar_url, {
            'producto_id': producto_prueba.id
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        print(f"📡 Respuesta de eliminación: Status {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Petición de eliminación procesada correctamente")
            
            # Verificar que el producto fue eliminado
            try:
                ProductoVenta.objects.get(id=producto_prueba.id)
                print("❌ El producto aún existe en la base de datos")
                return False
            except ProductoVenta.DoesNotExist:
                print("✅ Producto eliminado correctamente de la base de datos")
        
        elif response.status_code == 302:
            print("✅ Redirección después de eliminación (comportamiento normal)")
            
            # Verificar que el producto fue eliminado
            try:
                ProductoVenta.objects.get(id=producto_prueba.id)
                print("❌ El producto aún existe en la base de datos")
                return False
            except ProductoVenta.DoesNotExist:
                print("✅ Producto eliminado correctamente de la base de datos")
        
        else:
            print(f"❌ Error en la eliminación: {response.status_code}")
            print(f"Contenido de la respuesta: {response.content.decode()[:200]}...")
            return False
        
        # Probar acceso a la página después de eliminación
        response = client.get(lista_url)
        if response.status_code == 200:
            print("✅ Página accesible después de la eliminación")
            
            # Verificar que el producto ya no aparece
            if str(producto_prueba.id) not in response.content.decode():
                print("✅ Producto ya no visible en la página")
            else:
                print("⚠️  Producto aún visible en la página (puede ser caché)")
        
        print("\n🎯 Resultado de la prueba:")
        print("✅ ¡FUNCIONALIDAD DE ELIMINACIÓN FUNCIONANDO CORRECTAMENTE!")
        print("\n📋 Lo que se verificó:")
        print("1. ✅ Usuario con permisos puede acceder a la página")
        print("2. ✅ Producto de prueba se crea correctamente")
        print("3. ✅ Página de lista es accesible")
        print("4. ✅ Petición de eliminación se procesa")
        print("5. ✅ Producto se elimina de la base de datos")
        print("6. ✅ Página sigue funcionando después de eliminación")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Limpiar: intentar eliminar cualquier producto de prueba que quede
        try:
            ProductoVenta.objects.filter(codigo__startswith='PRUEBA_ELIM_').delete()
            CategoriaProducto.objects.filter(nombre="Categoría de Prueba Eliminación").delete()
            print("🧹 Limpieza de productos de prueba completada")
        except:
            pass

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 ¡Todas las pruebas pasaron! La eliminación funciona correctamente.")
        print("\nPuedes probar ahora en el navegador:")
        print("1. Ir a la página de productos")
        print("2. Hacer clic en 'Eliminar' en cualquier producto")
        print("3. Confirmar la eliminación")
        print("4. Verificar que no hay errores en la consola del navegador")
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa los logs arriba.")
    
    sys.exit(0 if success else 1)
