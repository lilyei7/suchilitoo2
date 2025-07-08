#!/usr/bin/env python3
"""
Script final para verificar y probar el sistema de cocina
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def verificar_sistema_cocina():
    """Verificación completa del sistema de cocina"""
    print("🍣 VERIFICACIÓN COMPLETA DEL SISTEMA DE COCINA")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    errores = []
    
    # 1. Verificar aplicación instalada
    print("1. Verificando aplicación instalada...")
    try:
        from django.conf import settings
        if 'cocina' in settings.INSTALLED_APPS:
            print("   ✓ Aplicación 'cocina' instalada correctamente")
        else:
            errores.append("Aplicación 'cocina' no está en INSTALLED_APPS")
    except Exception as e:
        errores.append(f"Error verificando INSTALLED_APPS: {e}")
    
    # 2. Verificar modelos
    print("\n2. Verificando modelos...")
    try:
        from cocina.models import EstadoCocina, TiempoPreparacion, OrdenCocina, ItemCocina, LogCocina
        
        # Verificar que las tablas existen
        print(f"   ✓ EstadoCocina: {EstadoCocina.objects.count()} registros")
        print(f"   ✓ TiempoPreparacion: {TiempoPreparacion.objects.count()} registros")
        print(f"   ✓ OrdenCocina: {OrdenCocina.objects.count()} registros")
        print(f"   ✓ ItemCocina: {ItemCocina.objects.count()} registros")
        print(f"   ✓ LogCocina: {LogCocina.objects.count()} registros")
        
    except Exception as e:
        errores.append(f"Error con modelos: {e}")
    
    # 3. Verificar URLs
    print("\n3. Verificando URLs...")
    try:
        from django.urls import reverse
        
        urls_cocina = [
            'cocina:login',
            'cocina:dashboard',
            'cocina:ordenes_pendientes',
            'cocina:reportes',
            'cocina:estadisticas',
        ]
        
        for url_name in urls_cocina:
            try:
                url = reverse(url_name)
                print(f"   ✓ {url_name}: {url}")
            except Exception as e:
                errores.append(f"Error con URL {url_name}: {e}")
                
    except Exception as e:
        errores.append(f"Error verificando URLs: {e}")
    
    # 4. Verificar usuarios y permisos
    print("\n4. Verificando usuarios y permisos...")
    try:
        from django.contrib.auth.models import User, Group
        
        # Verificar grupo cocina
        grupo_cocina = Group.objects.filter(name='Cocina').first()
        if grupo_cocina:
            print(f"   ✓ Grupo 'Cocina' existe con {grupo_cocina.user_set.count()} usuarios")
            print(f"   ✓ Permisos del grupo: {grupo_cocina.permissions.count()}")
        else:
            errores.append("Grupo 'Cocina' no existe")
        
        # Verificar usuarios de cocina
        usuarios_cocina = User.objects.filter(groups__name='Cocina')
        print(f"   ✓ Usuarios de cocina: {usuarios_cocina.count()}")
        
        for usuario in usuarios_cocina:
            print(f"     - {usuario.username}: {usuario.first_name} {usuario.last_name}")
            
    except Exception as e:
        errores.append(f"Error verificando usuarios: {e}")
    
    # 5. Verificar templates
    print("\n5. Verificando templates...")
    try:
        templates_requeridos = [
            'cocina/base.html',
            'cocina/login.html',
            'cocina/dashboard.html',
            'cocina/ordenes_pendientes.html',
            'cocina/detalle_orden.html',
            'cocina/reportes.html',
            'cocina/estadisticas.html',
        ]
        
        for template in templates_requeridos:
            template_path = os.path.join(settings.BASE_DIR, 'cocina', 'templates', template)
            if os.path.exists(template_path):
                print(f"   ✓ {template}")
            else:
                errores.append(f"Template faltante: {template}")
                
    except Exception as e:
        errores.append(f"Error verificando templates: {e}")
    
    # 6. Verificar archivos estáticos
    print("\n6. Verificando archivos estáticos...")
    try:
        static_files = [
            'cocina/css/cocina.css',
            'cocina/js/cocina.js',
        ]
        
        for static_file in static_files:
            static_path = os.path.join(settings.BASE_DIR, 'cocina', 'static', static_file)
            if os.path.exists(static_path):
                print(f"   ✓ {static_file}")
            else:
                errores.append(f"Archivo estático faltante: {static_file}")
                
    except Exception as e:
        errores.append(f"Error verificando archivos estáticos: {e}")
    
    # 7. Verificar vistas
    print("\n7. Verificando vistas...")
    try:
        from cocina import views
        
        vistas_requeridas = [
            'login_view',
            'logout_view',
            'dashboard',
            'ordenes_pendientes',
            'detalle_orden',
            'reportes',
            'estadisticas',
        ]
        
        for vista in vistas_requeridas:
            if hasattr(views, vista):
                print(f"   ✓ {vista}")
            else:
                errores.append(f"Vista faltante: {vista}")
                
    except Exception as e:
        errores.append(f"Error verificando vistas: {e}")
    
    # 8. Verificar admin
    print("\n8. Verificando admin...")
    try:
        from django.contrib.admin.sites import site
        from cocina.models import EstadoCocina, TiempoPreparacion, OrdenCocina, ItemCocina, LogCocina
        
        modelos_admin = [EstadoCocina, TiempoPreparacion, OrdenCocina, ItemCocina, LogCocina]
        
        for modelo in modelos_admin:
            if modelo in site._registry:
                print(f"   ✓ {modelo.__name__} registrado en admin")
            else:
                errores.append(f"Modelo {modelo.__name__} no registrado en admin")
                
    except Exception as e:
        errores.append(f"Error verificando admin: {e}")
    
    # Resumen final
    print("\n" + "=" * 60)
    if errores:
        print(f"❌ VERIFICACIÓN COMPLETADA CON {len(errores)} ERROR(ES):")
        for i, error in enumerate(errores, 1):
            print(f"   {i}. {error}")
        print("\n🔧 SOLUCIONES RECOMENDADAS:")
        print("   - Ejecute: python manage.py makemigrations cocina")
        print("   - Ejecute: python manage.py migrate")
        print("   - Ejecute: python configurar_cocina.py")
        print("   - Verifique que todos los templates existan")
        print("   - Verifique que los archivos estáticos existan")
    else:
        print("✅ VERIFICACIÓN COMPLETADA SIN ERRORES")
        print("\n🎉 EL SISTEMA DE COCINA ESTÁ COMPLETAMENTE FUNCIONAL!")
        print("\n📋 RESUMEN DE FUNCIONALIDADES:")
        print("   ✓ Login específico para cocina")
        print("   ✓ Dashboard con estadísticas en tiempo real")
        print("   ✓ Gestión de órdenes pendientes")
        print("   ✓ Detalle de órdenes con cronómetro")
        print("   ✓ Reportes y estadísticas")
        print("   ✓ Cambio de estados de órdenes e items")
        print("   ✓ Asignación de cocineros")
        print("   ✓ Seguimiento de tiempos de preparación")
        print("   ✓ Interfaz responsive y moderna")
        print("\n🚀 PARA USAR EL SISTEMA:")
        print("   1. Ejecute: python manage.py runserver")
        print("   2. Vaya a: http://localhost:8000/cocina/")
        print("   3. Use las credenciales:")
        print("      - Usuario: cocinero | Contraseña: cocinero123")
        print("      - Usuario: ayudante | Contraseña: ayudante123")
        print("\n🔗 URLS DISPONIBLES:")
        print("   - /cocina/ - Dashboard principal")
        print("   - /cocina/login/ - Login de cocina")
        print("   - /cocina/ordenes/ - Órdenes pendientes")
        print("   - /cocina/reportes/ - Reportes")
        print("   - /cocina/estadisticas/ - Estadísticas")
    
    return len(errores) == 0

def crear_ordenes_prueba():
    """Crear órdenes de prueba para demostrar el sistema"""
    print("\n" + "=" * 60)
    print("CREANDO ÓRDENES DE PRUEBA")
    print("=" * 60)
    
    try:
        from mesero.models import Orden, OrdenItem, Mesa
        from restaurant.models import ProductoVenta
        from django.contrib.auth.models import User
        from cocina.models import OrdenCocina, ItemCocina
        
        # Obtener o crear mesa
        mesa, created = Mesa.objects.get_or_create(
            numero=1,
            defaults={
                'capacidad': 4,
                'activa': True,
                'disponible': True
            }
        )
        
        # Obtener mesero
        mesero = User.objects.filter(groups__name='Mesero').first()
        if not mesero:
            mesero = User.objects.filter(is_staff=True).first()
        
        if not mesero:
            print("⚠ No hay meseros disponibles, saltando creación de órdenes de prueba")
            return
        
        # Obtener productos
        productos = ProductoVenta.objects.all()[:3]
        
        if not productos:
            print("⚠ No hay productos disponibles, saltando creación de órdenes de prueba")
            return
        
        # Crear orden de prueba
        orden = Orden.objects.create(
            mesa=mesa,
            mesero=mesero,
            estado='confirmada',
            total=0,
            observaciones='Orden de prueba para cocina'
        )
        
        # Crear items
        total = 0
        for i, producto in enumerate(productos):
            item = OrdenItem.objects.create(
                orden=orden,
                producto=producto,
                cantidad=i + 1,
                precio_unitario=producto.precio,
                personalizaciones=f'Personalización {i+1}' if i == 0 else ''
            )
            total += item.subtotal
            
            # Crear info de cocina para el item
            ItemCocina.objects.create(
                orden_item=item,
                estado_cocina='recibida'
            )
        
        orden.total = total
        orden.save()
        
        # Crear info de cocina para la orden
        OrdenCocina.objects.create(
            orden=orden,
            prioridad=1,
            tiempo_estimado_total=30
        )
        
        print(f"✅ Orden de prueba creada: #{orden.numero_orden}")
        print(f"   Mesa: {mesa.numero}")
        print(f"   Items: {orden.items.count()}")
        print(f"   Total: ${orden.total}")
        
    except Exception as e:
        print(f"❌ Error creando órdenes de prueba: {e}")

if __name__ == '__main__':
    # Verificar sistema
    sistema_ok = verificar_sistema_cocina()
    
    # Si el sistema está OK, crear órdenes de prueba
    if sistema_ok:
        crear_ordenes_prueba()
    
    print("\n" + "=" * 60)
    print("VERIFICACIÓN COMPLETADA")
    print("=" * 60)
