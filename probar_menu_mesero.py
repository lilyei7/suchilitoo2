#!/usr/bin/env python3
"""
Script para verificar que las vistas del mesero funcionan correctamente
y muestran los productos reales de la base de datos.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from restaurant.models import ProductoVenta, CategoriaProducto

def main():
    print("🧪 Probando las vistas del mesero con datos reales...")
    print("=" * 60)
    
    try:
        # Crear un cliente de prueba
        client = Client()
        
        # Obtener un usuario para hacer login
        User = get_user_model()
        users = User.objects.filter(is_active=True)
        
        if not users.exists():
            print("❌ No hay usuarios activos en la base de datos")
            return False
        
        user = users.first()
        print(f"✅ Usando usuario: {user.username}")
        
        # Hacer login
        client.force_login(user)
        print("✅ Login exitoso")
        
        # Probar la vista del menú
        print("\n📋 Probando vista del menú...")
        menu_url = reverse('mesero:menu')
        response = client.get(menu_url)
        
        if response.status_code == 200:
            print("✅ Vista del menú accesible")
            
            # Verificar que el contexto contiene productos reales
            context = response.context
            productos_por_categoria = context.get('productos_por_categoria', {})
            total_productos = context.get('total_productos', 0)
            total_categorias = context.get('total_categorias', 0)
            
            print(f"📊 Estadísticas del menú:")
            print(f"   - Categorías: {total_categorias}")
            print(f"   - Productos: {total_productos}")
            
            if total_productos > 0:
                print("✅ El menú muestra productos reales de la base de datos")
                
                # Mostrar las categorías y productos
                for categoria, productos in productos_por_categoria.items():
                    print(f"\n🏷️  {categoria} ({len(productos)} productos):")
                    for producto in productos[:3]:  # Solo mostrar primeros 3
                        print(f"     • {producto['nombre']} - ${producto['precio']:.2f}")
                        if producto.get('descripcion'):
                            desc = producto['descripcion'][:50] + "..." if len(producto['descripcion']) > 50 else producto['descripcion']
                            print(f"       📝 {desc}")
            else:
                print("⚠️  El menú no muestra productos")
                
        else:
            print(f"❌ Error al acceder al menú: {response.status_code}")
            return False
        
        # Probar la vista de nueva orden
        print("\n📝 Probando vista de nueva orden...")
        mesa_id = 5
        nueva_orden_url = reverse('mesero:nueva_orden', args=[mesa_id])
        response = client.get(nueva_orden_url)
        
        if response.status_code == 200:
            print("✅ Vista de nueva orden accesible")
            
            # Verificar que usa los mismos productos
            context = response.context
            productos_nueva_orden = context.get('productos_por_categoria', {})
            
            if productos_nueva_orden:
                print("✅ Nueva orden también muestra productos reales")
                
                # Verificar que son los mismos productos que en el menú
                if productos_nueva_orden == productos_por_categoria:
                    print("✅ Los productos en ambas vistas son idénticos")
                else:
                    print("⚠️  Los productos difieren entre vistas")
            else:
                print("❌ Nueva orden no muestra productos")
        else:
            print(f"❌ Error al acceder a nueva orden: {response.status_code}")
            return False
        
        # Verificar que no hay productos hardcodeados
        print("\n🔍 Verificando que no hay productos hardcodeados...")
        
        # Obtener productos reales de la BD
        productos_reales = list(ProductoVenta.objects.filter(disponible=True).values_list('nombre', flat=True))
        
        productos_en_menu = []
        for categoria, productos in productos_por_categoria.items():
            for producto in productos:
                productos_en_menu.append(producto['nombre'])
        
        productos_hardcodeados = [
            'Gyozas', 'Edamame', 'Dragon Roll', 'Rainbow Roll', 
            'Ramen Tonkotsu', 'Teriyaki de Salmón', 'Mochi de Matcha', 
            'Tempura de Helado'
        ]
        
        productos_hardcodeados_encontrados = []
        for hardcoded in productos_hardcodeados:
            if hardcoded in productos_en_menu and hardcoded not in productos_reales:
                productos_hardcodeados_encontrados.append(hardcoded)
        
        if productos_hardcodeados_encontrados:
            print(f"⚠️  Se encontraron productos posiblemente hardcodeados: {productos_hardcodeados_encontrados}")
        else:
            print("✅ No se encontraron productos hardcodeados")
        
        print("\n🎯 RESULTADO:")
        if total_productos > 0 and not productos_hardcodeados_encontrados:
            print("✅ ¡PERFECTO! Las vistas del mesero muestran SOLO productos reales de la base de datos")
            print(f"📊 Mostrando {total_productos} productos en {total_categorias} categorías")
            return True
        else:
            print("❌ Hay problemas con los datos mostrados")
            return False
            
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 ¡Las vistas del mesero funcionan perfectamente con datos reales!")
    else:
        print("\n❌ Se encontraron problemas que necesitan corrección")
    
    sys.exit(0 if success else 1)
