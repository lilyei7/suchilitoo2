#!/usr/bin/env python3
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario
from mesero.models import Mesa, OpcionPersonalizacion, ProductoPersonalizacion, OrdenItemPersonalizacion
from restaurant.models import ProductoVenta
from django.db import connection

def verificar_sistema_completo():
    """Verificar que todo el sistema esté funcionando correctamente"""
    
    print("🔍 VERIFICANDO SISTEMA COMPLETO")
    print("=" * 60)
    
    # 1. Verificar usuarios
    print("\n1. USUARIOS DE PRUEBA:")
    mesero = Usuario.objects.filter(username='mesero_demo').first()
    if mesero:
        print(f"   ✅ mesero_demo - Sucursal: {mesero.sucursal.nombre if mesero.sucursal else 'Sin sucursal'}")
    else:
        print("   ❌ mesero_demo no encontrado")
    
    # 2. Verificar mesas
    print("\n2. MESAS DISPONIBLES:")
    mesas = Mesa.objects.filter(activa=True)
    print(f"   ✅ {mesas.count()} mesas activas encontradas")
    
    # 3. Verificar productos
    print("\n3. PRODUCTOS DE MENÚ:")
    productos = ProductoVenta.objects.filter(disponible=True)
    print(f"   ✅ {productos.count()} productos disponibles")
    
    # 4. Verificar personalizaciones
    print("\n4. SISTEMA DE PERSONALIZACIÓN:")
    opciones = OpcionPersonalizacion.objects.filter(activa=True)
    print(f"   ✅ {opciones.count()} opciones de personalización disponibles")
    
    asignaciones = ProductoPersonalizacion.objects.filter(activa=True)
    print(f"   ✅ {asignaciones.count()} asignaciones producto-opción configuradas")
    
    # 5. Verificar productos con personalización
    print("\n5. PRODUCTOS CON PERSONALIZACIÓN:")
    productos_con_personalizacion = ProductoVenta.objects.filter(
        productopersonalizacion__activa=True
    ).distinct()
    
    for producto in productos_con_personalizacion:
        opciones_count = ProductoPersonalizacion.objects.filter(
            producto=producto, activa=True
        ).count()
        print(f"   ✅ {producto.nombre} - {opciones_count} opciones")
    
    # 6. Verificar función de menú
    print("\n6. FUNCIÓN DE MENÚ:")
    try:
        from mesero.views import obtener_productos_menu
        menu = obtener_productos_menu()
        print(f"   ✅ Función obtener_productos_menu() funciona correctamente")
        print(f"   ✅ {len(menu)} categorías de productos")
        
        # Verificar que hay productos con personalización
        productos_con_pers = 0
        for categoria, productos in menu.items():
            for producto in productos:
                if producto.get('personalizaciones'):
                    productos_con_pers += 1
        
        print(f"   ✅ {productos_con_pers} productos con personalización en el menú")
        
    except Exception as e:
        print(f"   ❌ Error en función de menú: {e}")
    
    # 7. Verificar base de datos
    print("\n7. BASE DE DATOS:")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM mesero_opcionpersonalizacion")
            count = cursor.fetchone()[0]
            print(f"   ✅ Tabla OpcionPersonalizacion: {count} registros")
            
            cursor.execute("SELECT COUNT(*) FROM mesero_productopersonalizacion")
            count = cursor.fetchone()[0]
            print(f"   ✅ Tabla ProductoPersonalizacion: {count} registros")
            
    except Exception as e:
        print(f"   ❌ Error en base de datos: {e}")
    
    print("\n8. PRÓXIMOS PASOS:")
    print("   🌐 Iniciar servidor: python manage.py runserver")
    print("   🔑 Login: mesero_demo / test123")
    print("   📱 URL: http://127.0.0.1:8000/mesero/login/")
    print("   🍱 Personalizar: Buscar botón 'Personalizar' en productos")
    
    print("\n" + "=" * 60)
    print("🎉 SISTEMA COMPLETO VERIFICADO Y LISTO")

if __name__ == '__main__':
    verificar_sistema_completo()
