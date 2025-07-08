#!/usr/bin/env python
"""
Script para verificar el contenido exacto que se envía al navegador
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from restaurant.models import ProductoVenta, CategoriaProducto

def verificar_contenido_navegador():
    """Verificar exactamente qué contenido se está enviando al navegador"""
    print("=" * 80)
    print("VERIFICACIÓN DETALLADA DEL CONTENIDO DEL MENÚ")
    print("=" * 80)
    
    client = Client()
    
    # 1. Login con el usuario de prueba
    print("1. Haciendo login...")
    login_data = {
        'username': 'mesero_test',
        'password': '123456'
    }
    
    response = client.post('/mesero/login/', login_data, follow=True)
    if response.status_code != 200:
        print(f"❌ Error en login: {response.status_code}")
        return
    
    print("✅ Login exitoso")
    
    # 2. Obtener la página del menú
    print("\n2. Obteniendo página del menú...")
    response = client.get('/mesero/menu/')
    
    if response.status_code != 200:
        print(f"❌ Error al obtener menú: {response.status_code}")
        return
    
    print(f"✅ Página del menú obtenida (Status: {response.status_code})")
    
    # 3. Verificar productos en la base de datos
    print("\n3. Verificando productos en la base de datos...")
    productos = ProductoVenta.objects.filter(disponible=True)
    print(f"Productos disponibles: {productos.count()}")
    
    for producto in productos:
        categoria = producto.categoria.nombre if producto.categoria else 'Sin Categoría'
        print(f"  - {producto.nombre} (${producto.precio}) - Categoría: {categoria}")
    
    # 4. Analizar el contenido HTML
    print("\n4. Analizando contenido HTML...")
    content = response.content.decode('utf-8')
    
    # Buscar elementos clave
    elementos_clave = [
        ('productos_por_categoria', 'productos_por_categoria' in content),
        ('categoria-header', 'categoria-header' in content),
        ('productos-grid', 'productos-grid' in content),
        ('producto-card', 'producto-card' in content),
        ('btn-agregar', 'btn-agregar' in content),
        ('Edamame', 'Edamame' in content),
        ('Dragon Roll', 'Dragon Roll' in content),
        ('Gyozas', 'Gyozas' in content),
        ('BEBIDAS', 'BEBIDAS' in content),
        ('ENTRADAS', 'ENTRADAS' in content),
    ]
    
    print("Elementos encontrados en el HTML:")
    for elemento, encontrado in elementos_clave:
        estado = "✅" if encontrado else "❌"
        print(f"  {estado} {elemento}: {encontrado}")
    
    # 5. Buscar errores específicos
    print("\n5. Buscando posibles errores...")
    
    errores_posibles = [
        ('Error de template', 'TemplateDoesNotExist' in content or 'TemplateSyntaxError' in content),
        ('Sin productos mensaje', 'Sin productos disponibles' in content),
        ('Error 500', 'Internal Server Error' in content),
        ('Error JavaScript', 'SyntaxError' in content or 'ReferenceError' in content),
        ('CSS no cargado', len([line for line in content.split('\n') if 'style' in line]) < 5),
    ]
    
    for error, presente in errores_posibles:
        if presente:
            print(f"⚠️  {error}: Detectado")
        else:
            print(f"✅ {error}: No detectado")
    
    # 6. Verificar contexto específico
    print("\n6. Verificando estructura del HTML...")
    
    # Contar elementos específicos
    count_categoria_headers = content.count('categoria-header')
    count_producto_cards = content.count('producto-card')
    count_btn_agregar = content.count('btn-agregar')
    
    print(f"Encabezados de categoría encontrados: {count_categoria_headers}")
    print(f"Tarjetas de productos encontradas: {count_producto_cards}")
    print(f"Botones agregar encontrados: {count_btn_agregar}")
    
    # 7. Mostrar una muestra del HTML cerca de donde deberían estar los productos
    print("\n7. Muestra del HTML (área de productos)...")
    if 'menu-container' in content:
        inicio = content.find('menu-container')
        fin = min(inicio + 1000, len(content))
        muestra = content[inicio:fin]
        print("HTML alrededor del menu-container:")
        print("-" * 40)
        print(muestra[:500] + "..." if len(muestra) > 500 else muestra)
        print("-" * 40)
    else:
        print("❌ No se encontró 'menu-container' en el HTML")
    
    # 8. Verificar si hay JavaScript errors
    print("\n8. Verificando JavaScript...")
    if 'agregarProducto' in content:
        print("✅ Función agregarProducto encontrada")
    else:
        print("❌ Función agregarProducto NO encontrada")
    
    # 9. Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN DEL DIAGNÓSTICO")
    print("=" * 80)
    
    if count_producto_cards > 0:
        print(f"✅ Se encontraron {count_producto_cards} tarjetas de productos")
        print("✅ El problema podría ser visual (CSS) o JavaScript")
        print("\n🔧 POSIBLES SOLUCIONES:")
        print("   1. Abre las herramientas de desarrollador (F12)")
        print("   2. Ve a la pestaña 'Console' para ver errores JavaScript")
        print("   3. Ve a la pestaña 'Network' para ver si faltan archivos CSS/JS")
        print("   4. Verifica que los estilos CSS se estén aplicando")
    else:
        print("❌ NO se encontraron tarjetas de productos en el HTML")
        print("❌ El problema está en el backend (views.py o template)")
        print("\n🔧 POSIBLES SOLUCIONES:")
        print("   1. Verificar que la vista obtener_productos_menu() funcione")
        print("   2. Verificar que el template reciba productos_por_categoria")
        print("   3. Revisar errores en el servidor Django")
    
    print(f"\n📏 Tamaño total del HTML: {len(content)} caracteres")
    print(f"📊 Productos en BD: {productos.count()}")
    
    # 10. Guardar HTML para inspección manual
    print("\n10. Guardando HTML para inspección...")
    with open('menu_debug.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ HTML guardado en 'menu_debug.html' para inspección manual")

if __name__ == '__main__':
    verificar_contenido_navegador()
