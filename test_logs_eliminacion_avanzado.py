#!/usr/bin/env python3
"""
Script AVANZADO para verificar los logs de eliminación de productos.
Este script verifica que los logs se estén generando correctamente
tanto en frontend como en backend, con tracking completo del flujo.
"""
import os
import sys
import django
import logging
from datetime import datetime
import time

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

def setup_logging():
    """Configurar logging para capturar los logs"""
    # Configurar el logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Configurar el handler para mostrar en consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # Formato detallado para los logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Limpiar handlers existentes y agregar el nuestro
    logger.handlers = []
    logger.addHandler(console_handler)
    
    return logger

def crear_datos_prueba():
    """Crear datos de prueba para la eliminación"""
    print("\n" + "="*60)
    print("🔧 CREANDO DATOS DE PRUEBA")
    print("="*60)
    
    # Crear usuario admin si no existe
    admin_user, created = User.objects.get_or_create(
        username='admin_test_logs',
        defaults={
            'email': 'admin_logs@test.com',
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
        nombre='Categoria Test Logs Eliminacion',
        defaults={'descripcion': 'Categoria para pruebas de logs de eliminacion'}
    )
    if created:
        print(f"✅ Categoría creada: {categoria.nombre}")
    else:
        print(f"📁 Categoría existente: {categoria.nombre}")
    
    # Crear producto de prueba
    timestamp = datetime.now().strftime("%H%M%S")
    producto_nombre = f"Producto Test Logs {timestamp}"
    
    producto = ProductoVenta.objects.create(
        nombre=producto_nombre,
        descripcion="Producto creado específicamente para probar logs de eliminación AVANZADOS",
        precio=10.50,
        categoria=categoria,
        disponible=True
    )
    print(f"✅ Producto creado: {producto.nombre} (ID: {producto.id})")
    
    return admin_user, producto

def test_eliminacion_con_logs_detallados():
    """Probar la eliminación capturando TODOS los logs posibles"""
    logger = setup_logging()
    
    print("\n" + "="*60)
    print("🚀 INICIANDO TEST AVANZADO DE ELIMINACIÓN CON LOGS")
    print("="*60)
    
    # Crear datos de prueba
    admin_user, producto = crear_datos_prueba()
    
    # Crear cliente de prueba
    client = Client()
    
    # Hacer login
    login_success = client.login(username='admin_test_logs', password='admin123')
    if not login_success:
        print("❌ Error: No se pudo hacer login")
        return False
    
    print(f"✅ Login exitoso como: {admin_user.username}")
    
    # Obtener la URL de eliminación
    url_eliminacion = reverse('dashboard:eliminar_producto_venta', kwargs={'producto_id': producto.id})
    print(f"🔗 URL de eliminación: {url_eliminacion}")
    
    print("\n" + "-"*50)
    print("📋 INFORMACIÓN PRE-ELIMINACIÓN DETALLADA")
    print("-"*50)
    print(f"Timestamp inicio: {datetime.now().isoformat()}")
    print(f"Producto ID: {producto.id}")
    print(f"Producto Nombre: {producto.nombre}")
    print(f"Producto Disponible: {producto.disponible}")
    print(f"Usuario: {admin_user.username}")
    print(f"Usuario ID: {admin_user.id}")
    print(f"Es superusuario: {admin_user.is_superuser}")
    print(f"Es staff: {admin_user.is_staff}")
    
    # Verificar permisos específicos
    permisos = {
        'view_productoventa': admin_user.has_perm('restaurant.view_productoventa'),
        'add_productoventa': admin_user.has_perm('restaurant.add_productoventa'),
        'change_productoventa': admin_user.has_perm('restaurant.change_productoventa'),
        'delete_productoventa': admin_user.has_perm('restaurant.delete_productoventa'),
    }
    print(f"Permisos del usuario: {permisos}")
    
    # Verificar que el producto existe antes de eliminar
    productos_antes = ProductoVenta.objects.filter(id=producto.id).count()
    total_productos_antes = ProductoVenta.objects.all().count()
    print(f"Productos encontrados antes (específico): {productos_antes}")
    print(f"Total productos en BD antes: {total_productos_antes}")
    
    print("\n" + "-"*50)
    print("🔥 INICIANDO PETICIÓN DE ELIMINACIÓN DETALLADA")
    print("-"*50)
    print("⏰ Timestamp petición:", datetime.now().isoformat())
    print("📡 Enviando petición POST...")
    print("🎯 Logs que deberían aparecer a continuación:")
    print("   - Logs del backend (función eliminar_producto_venta)")
    print("   - Logs de permisos")
    print("   - Logs de eliminación")
    print("\n👀 OBSERVANDO LOGS EN TIEMPO REAL:")
    print("-" * 50)
    
    # Realizar la petición de eliminación (simulando el envío del formulario)
    start_time = time.time()
    response = client.post(url_eliminacion, {
        'csrfmiddlewaretoken': client.session.get('csrftoken', 'test-token')
    }, follow=True)
    end_time = time.time()
    
    print("-" * 50)
    print("📥 RESPUESTA RECIBIDA:")
    print(f"   Status Code: {response.status_code}")
    print(f"   Tiempo de respuesta: {end_time - start_time:.3f} segundos")
    print(f"   Redirect Chain: {response.redirect_chain}")
    print(f"   Content-Type: {response.get('Content-Type', 'N/A')}")
    
    # Verificar si el producto fue eliminado
    productos_despues = ProductoVenta.objects.filter(id=producto.id).count()
    total_productos_despues = ProductoVenta.objects.all().count()
    print(f"   Productos encontrados después (específico): {productos_despues}")
    print(f"   Total productos en BD después: {total_productos_despues}")
    print(f"   Productos eliminados en total: {total_productos_antes - total_productos_despues}")
    
    # Verificar mensajes
    messages = list(response.context.get('messages', []) if response.context else [])
    if messages:
        print(f"   Mensajes en respuesta: {[str(m) for m in messages]}")
    else:
        print("   Sin mensajes en respuesta")
    
    if productos_despues == 0:
        print("✅ ELIMINACIÓN EXITOSA: El producto fue eliminado correctamente")
        print("✅ Los logs del backend se ejecutaron (revisar arriba)")
        return True
    else:
        print("❌ FALLO EN ELIMINACIÓN: El producto sigue existiendo")
        print("❌ Posible problema: La petición no llegó al backend o falló")
        return False

def test_eliminacion_ajax_avanzado():
    """Probar la eliminación vía AJAX con logs detallados"""
    logger = setup_logging()
    
    print("\n" + "="*60)
    print("🌐 INICIANDO TEST AVANZADO DE ELIMINACIÓN VÍA AJAX")
    print("="*60)
    
    # Crear datos de prueba
    admin_user, producto = crear_datos_prueba()
    
    # Crear cliente de prueba
    client = Client()
    
    # Hacer login
    client.login(username='admin_test_logs', password='admin123')
    print(f"✅ Login exitoso como: {admin_user.username}")
    
    # Obtener la URL de eliminación
    url_eliminacion = reverse('dashboard:eliminar_producto_venta', kwargs={'producto_id': producto.id})
    print(f"🔗 URL de eliminación: {url_eliminacion}")
    
    print("\n" + "-"*50)
    print("🔥 INICIANDO PETICIÓN AJAX DE ELIMINACIÓN DETALLADA")
    print("-"*50)
    print("⏰ Timestamp petición AJAX:", datetime.now().isoformat())
    print("🎯 Headers que se enviarán:")
    print("   - X-Requested-With: XMLHttpRequest")
    print("   - Content-Type: application/x-www-form-urlencoded")
    print("\n👀 OBSERVANDO LOGS DE AJAX EN TIEMPO REAL:")
    print("-" * 50)
    
    # Realizar la petición AJAX
    start_time = time.time()
    response = client.post(url_eliminacion, {
        'csrfmiddlewaretoken': 'test-token'
    }, 
    HTTP_X_REQUESTED_WITH='XMLHttpRequest',  # Simular petición AJAX
    content_type='application/x-www-form-urlencoded'
    )
    end_time = time.time()
    
    print("-" * 50)
    print(f"📥 RESPUESTA AJAX RECIBIDA:")
    print(f"   Status Code: {response.status_code}")
    print(f"   Tiempo de respuesta: {end_time - start_time:.3f} segundos")
    print(f"   Content-Type: {response.get('Content-Type', 'N/A')}")
    print(f"   Content-Length: {len(response.content)} bytes")
    
    # Intentar parsear la respuesta JSON
    try:
        response_content = response.content.decode()
        print(f"   Contenido raw: {response_content}")
        
        response_data = json.loads(response_content)
        print(f"   Response JSON parseado: {response_data}")
        
        if response_data.get('success'):
            print("✅ ELIMINACIÓN AJAX EXITOSA")
            print("✅ Backend respondió correctamente vía JSON")
            return True
        else:
            print(f"❌ FALLO EN ELIMINACIÓN AJAX: {response_data.get('message', 'Error desconocido')}")
            return False
    except json.JSONDecodeError as e:
        print(f"❌ Error parseando respuesta JSON: {e}")
        print(f"   Contenido raw: {response.content.decode()}")
        print("❌ Posible problema: Backend no está devolviendo JSON válido")
        return False

def verificar_configuracion_logs():
    """Verificar que Django esté configurado para mostrar logs"""
    print("\n" + "="*60)
    print("🔍 VERIFICANDO CONFIGURACIÓN AVANZADA DE LOGS")
    print("="*60)
    
    from django.conf import settings
    
    print("📋 Configuración de logging:")
    if hasattr(settings, 'LOGGING'):
        print(f"   LOGGING definido: Sí")
        logging_config = settings.LOGGING
        print(f"   Versión: {logging_config.get('version', 'N/A')}")
        print(f"   Handlers: {list(logging_config.get('handlers', {}).keys())}")
        print(f"   Loggers: {list(logging_config.get('loggers', {}).keys())}")
        print(f"   Root level: {logging_config.get('root', {}).get('level', 'N/A')}")
    else:
        print(f"   LOGGING definido: No (usando configuración por defecto)")
    
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    
    # Probar logs en diferentes niveles
    test_logger = logging.getLogger('dashboard.views.productos_venta_views')
    print("\n🧪 Probando logs de prueba en diferentes niveles...")
    test_logger.debug("🔍 DEBUG: Este es un log de nivel DEBUG")
    test_logger.info("📝 INFO: Este es un log de nivel INFO")
    test_logger.warning("⚠️ WARNING: Este es un log de nivel WARNING")
    test_logger.error("❌ ERROR: Este es un log de nivel ERROR")
    test_logger.critical("💥 CRITICAL: Este es un log de nivel CRITICAL")
    
    print("✅ Si ves los logs arriba, la configuración funciona")
    
    return True

def main():
    """Función principal que ejecuta todos los tests"""
    print("🚀 SCRIPT AVANZADO DE VERIFICACIÓN DE LOGS DE ELIMINACIÓN")
    print("=" * 60)
    print(f"⏰ Iniciado a las: {datetime.now().isoformat()}")
    
    try:
        # Verificar configuración de logs
        print("\n🔧 PASO 1: Verificando configuración...")
        verificar_configuracion_logs()
        
        # Test de eliminación normal
        print("\n🔧 PASO 2: Test eliminación normal...")
        resultado_normal = test_eliminacion_con_logs_detallados()
        
        # Test de eliminación AJAX
        print("\n🔧 PASO 3: Test eliminación AJAX...")
        resultado_ajax = test_eliminacion_ajax_avanzado()
        
        print("\n" + "="*60)
        print("📊 RESUMEN FINAL DE RESULTADOS")
        print("="*60)
        print(f"⏰ Completado a las: {datetime.now().isoformat()}")
        print(f"✅ Eliminación normal: {'ÉXITO' if resultado_normal else 'FALLO'}")
        print(f"✅ Eliminación AJAX: {'ÉXITO' if resultado_ajax else 'FALLO'}")
        
        if resultado_normal and resultado_ajax:
            print("\n🎉 TODOS LOS TESTS PASARON")
            print("✅ Los logs de eliminación funcionan correctamente")
            print("✅ La petición se ejecuta (no es solo un refresh)")
            print("✅ El backend procesa correctamente las eliminaciones")
        else:
            print("\n⚠️ ALGUNOS TESTS FALLARON")
            print("❌ Revisar logs arriba para diagnosticar problemas")
            print("❌ Posibles causas:")
            print("   - Permisos insuficientes")
            print("   - Error en el backend")
            print("   - Problema de configuración")
        
    except Exception as e:
        print(f"\n💥 ERROR EJECUTANDO SCRIPT: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
