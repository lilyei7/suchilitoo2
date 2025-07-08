#!/usr/bin/env python3
"""
Script para diagnosticar problemas de eliminación desde el frontend
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def main():
    print("=== DIAGNÓSTICO DE ELIMINACIÓN FRONTEND ===")
    
    # Importar modelos
    from restaurant.models import ProductoVenta
    from django.urls import reverse
    from django.contrib.sessions.middleware import SessionMiddleware
    from django.contrib.auth.middleware import AuthenticationMiddleware
    from django.contrib.messages.middleware import MessageMiddleware
    from django.middleware.csrf import CsrfViewMiddleware
    
    User = get_user_model()
    
    try:
        # 1. Verificar que tengamos productos de prueba
        print("\n1. Verificando productos disponibles...")
        productos = ProductoVenta.objects.all()
        print(f"Total productos en DB: {productos.count()}")
        
        if productos.count() == 0:
            print("⚠️  No hay productos para probar. Creando uno...")
            # Crear un producto de prueba
            from restaurant.models import CategoriaProducto
            
            # Crear categoría si no existe
            categoria, created = CategoriaProducto.objects.get_or_create(
                nombre="Test Category",
                defaults={'descripcion': 'Categoría de prueba'}
            )
            
            # Crear producto de prueba
            producto_test = ProductoVenta.objects.create(
                nombre="Producto Test Frontend",
                codigo="TEST_FRONTEND",
                descripcion="Producto creado para probar eliminación desde frontend",
                precio=15.99,
                disponible=True,
                categoria=categoria
            )
            print(f"✅ Producto creado: {producto_test.nombre} (ID: {producto_test.id})")
        else:
            print("✅ Productos disponibles:")
            for p in productos[:5]:  # Mostrar máximo 5
                print(f"   - {p.nombre} (ID: {p.id}) - Disponible: {p.disponible}")
        
        # 2. Verificar usuario admin
        print("\n2. Verificando usuario admin...")
        try:
            admin_user = User.objects.get(username='admin')
            print(f"✅ Usuario admin encontrado: {admin_user.username}")
            print(f"   - Es superusuario: {admin_user.is_superuser}")
            print(f"   - Es staff: {admin_user.is_staff}")
            print(f"   - Está activo: {admin_user.is_active}")
            print(f"   - Tiene permiso eliminar: {admin_user.has_perm('restaurant.delete_productoventa')}")
            print(f"   - Grupos: {[g.name for g in admin_user.groups.all()]}")
        except User.DoesNotExist:
            print("❌ Usuario admin no encontrado")
            return
        
        # 3. Crear cliente de prueba
        print("\n3. Configurando cliente de prueba...")
        client = Client()
        
        # Login como admin
        login_success = client.login(username='admin', password='admin123')
        print(f"Login exitoso: {login_success}")
        
        if not login_success:
            print("❌ No se pudo hacer login como admin")
            return
        
        # 4. Probar la página de productos
        print("\n4. Probando la página de productos...")
        try:
            url_lista = reverse('dashboard:productos_venta_moderna')
            print(f"URL de lista: {url_lista}")
            
            response_lista = client.get(url_lista)
            print(f"Status de respuesta: {response_lista.status_code}")
            
            if response_lista.status_code == 200:
                print("✅ Página de productos carga correctamente")
                
                # Verificar que el template tiene el contenido esperado
                content = response_lista.content.decode('utf-8')
                if 'deleteModal' in content:
                    print("✅ Modal de eliminación encontrado en el template")
                else:
                    print("❌ Modal de eliminación NO encontrado en el template")
                
                if 'data-bs-toggle="modal"' in content:
                    print("✅ Botones con modal toggle encontrados")
                else:
                    print("❌ Botones con modal toggle NO encontrados")
                
                if 'deleteForm' in content:
                    print("✅ Formulario de eliminación encontrado")
                else:
                    print("❌ Formulario de eliminación NO encontrado")
                    
            else:
                print(f"❌ Error cargando página: {response_lista.status_code}")
                print(f"Contenido: {response_lista.content.decode('utf-8')[:500]}...")
                return
        except Exception as e:
            print(f"❌ Error accediendo a la página: {e}")
            return
        
        # 5. Probar eliminación real
        print("\n5. Probando eliminación real...")
        
        # Tomar el primer producto disponible
        producto_test = productos.first()
        if not producto_test:
            print("❌ No hay productos para probar eliminación")
            return
        
        print(f"Producto a eliminar: {producto_test.nombre} (ID: {producto_test.id})")
        
        # Construir URL de eliminación
        url_eliminar = reverse('dashboard:eliminar_producto_venta', args=[producto_test.id])
        print(f"URL de eliminación: {url_eliminar}")
        
        # 6. Probar GET (debería fallar)
        print("\n6. Probando método GET (debería fallar)...")
        response_get = client.get(url_eliminar)
        print(f"GET Response status: {response_get.status_code}")
        if response_get.status_code in [302, 405]:
            print("✅ GET rechazado correctamente")
        else:
            print(f"⚠️  GET response inesperada: {response_get.status_code}")
        
        # 7. Probar POST sin CSRF (debería fallar)
        print("\n7. Probando POST sin CSRF (debería fallar)...")
        response_post_no_csrf = client.post(url_eliminar, {}, HTTP_X_CSRFTOKEN='invalid')
        print(f"POST sin CSRF status: {response_post_no_csrf.status_code}")
        
        # 8. Probar POST con CSRF correcto
        print("\n8. Probando POST con CSRF correcto...")
        
        # Primero obtener el token CSRF de la página
        csrf_response = client.get(url_lista)
        csrf_token = None
        
        # Buscar el CSRF token en el contenido
        import re
        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', csrf_response.content.decode('utf-8'))
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"✅ CSRF token obtenido: {csrf_token[:20]}...")
        else:
            print("❌ No se pudo obtener CSRF token")
            return
        
        # Hacer POST con CSRF token correcto
        post_data = {
            'csrfmiddlewaretoken': csrf_token
        }
        
        print(f"Datos POST: {post_data}")
        
        response_post = client.post(url_eliminar, post_data)
        print(f"POST con CSRF status: {response_post.status_code}")
        
        if response_post.status_code == 302:
            print("✅ Eliminación exitosa (redirect)")
            print(f"Redirect URL: {response_post.url}")
            
            # Verificar que el producto fue eliminado
            try:
                ProductoVenta.objects.get(id=producto_test.id)
                print("❌ El producto AÚN EXISTE después de la eliminación")
            except ProductoVenta.DoesNotExist:
                print("✅ El producto fue eliminado correctamente")
                
        elif response_post.status_code == 200:
            print("⚠️  Respuesta 200 - verificando contenido...")
            content = response_post.content.decode('utf-8')
            if 'error' in content.lower():
                print(f"❌ Error en respuesta: {content[:200]}...")
            else:
                print("✅ Respuesta 200 sin errores aparentes")
        else:
            print(f"❌ Status inesperado: {response_post.status_code}")
            print(f"Contenido: {response_post.content.decode('utf-8')[:500]}...")
        
        # 9. Probar con AJAX (simulando JavaScript)
        print("\n9. Probando eliminación vía AJAX...")
        
        # Crear otro producto para la prueba AJAX
        from restaurant.models import CategoriaProducto
        categoria, _ = CategoriaProducto.objects.get_or_create(
            nombre="Test Category",
            defaults={'descripcion': 'Categoría de prueba'}
        )
        
        producto_ajax = ProductoVenta.objects.create(
            nombre="Producto Test AJAX",
            codigo="TEST_AJAX",
            descripcion="Producto para probar AJAX",
            precio=19.99,
            disponible=True,
            categoria=categoria
        )
        
        url_eliminar_ajax = reverse('dashboard:eliminar_producto_venta', args=[producto_ajax.id])
        
        ajax_data = {
            'csrfmiddlewaretoken': csrf_token
        }
        
        response_ajax = client.post(
            url_eliminar_ajax,
            ajax_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            content_type='application/x-www-form-urlencoded'
        )
        
        print(f"AJAX Response status: {response_ajax.status_code}")
        print(f"AJAX Response content-type: {response_ajax.get('Content-Type', 'No Content-Type')}")
        
        if response_ajax.status_code == 200:
            try:
                response_data = json.loads(response_ajax.content.decode('utf-8'))
                print(f"AJAX Response JSON: {response_data}")
                
                if response_data.get('success'):
                    print("✅ AJAX eliminación exitosa")
                    
                    # Verificar que el producto fue eliminado
                    try:
                        ProductoVenta.objects.get(id=producto_ajax.id)
                        print("❌ El producto AJAX AÚN EXISTE después de la eliminación")
                    except ProductoVenta.DoesNotExist:
                        print("✅ El producto AJAX fue eliminado correctamente")
                else:
                    print(f"❌ AJAX eliminación falló: {response_data.get('message', 'Sin mensaje')}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"Contenido crudo: {response_ajax.content.decode('utf-8')}")
        else:
            print(f"❌ AJAX status inesperado: {response_ajax.status_code}")
            print(f"Contenido: {response_ajax.content.decode('utf-8')[:500]}...")
        
        print("\n=== DIAGNÓSTICO COMPLETADO ===")
        
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
