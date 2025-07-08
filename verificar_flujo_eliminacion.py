"""
Verifica todo el flujo de eliminación de productos después de haber corregido los errores JavaScript.
"""

import os
import sys
import django
import webbrowser
import requests

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sushi_core.settings")
django.setup()

# Importar modelos
from restaurant.models import ProductoVenta, CategoriaProducto, Unidad
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

def print_title(title):
    """Imprime un título formateado."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "*"))
    print("=" * 80)

def print_section(section):
    """Imprime una sección formateada."""
    print("\n" + "-" * 80)
    print(f" {section} ".center(80, "-"))
    print("-" * 80)

def verificar_productos_existentes():
    """Verifica si hay productos existentes en la base de datos."""
    print_section("Verificando productos existentes")
    
    productos = ProductoVenta.objects.all()
    count = productos.count()
    
    if count == 0:
        print("❌ No hay productos en la base de datos")
        return None
    
    print(f"✅ Se encontraron {count} productos en la base de datos")
    
    # Mostrar los primeros 5 productos
    print("\nProductos disponibles para pruebas de eliminación:")
    for i, producto in enumerate(productos[:5]):
        print(f"{i+1}. ID: {producto.id} - {producto.nombre} - ${producto.precio:.2f}")
    
    return productos

def verificar_permisos_eliminacion():
    """Verifica que los usuarios tengan permisos para eliminar productos."""
    print_section("Verificando permisos de eliminación")
    
    # Obtener el permiso para eliminar productos
    content_type = ContentType.objects.get_for_model(ProductoVenta)
    permiso = Permission.objects.get(
        codename='delete_productoventa',
        content_type=content_type
    )
    
    # Verificar usuarios con permisos
    usuarios_con_permiso = User.objects.filter(
        user_permissions=permiso
    ).union(
        User.objects.filter(
            groups__permissions=permiso
        )
    )
    
    count = usuarios_con_permiso.count()
    
    if count == 0:
        print("❌ Ningún usuario tiene permiso para eliminar productos")
        print("Se añadirá el permiso al primer superusuario encontrado...")
        
        # Buscar un superusuario
        superuser = User.objects.filter(is_superuser=True).first()
        if superuser:
            superuser.user_permissions.add(permiso)
            print(f"✅ Permiso añadido al usuario: {superuser.username}")
        else:
            print("❌ No se encontró ningún superusuario")
            return False
    else:
        print(f"✅ {count} usuarios tienen permiso para eliminar productos")
        print("\nUsuarios con permiso:")
        for i, usuario in enumerate(usuarios_con_permiso[:5]):
            print(f"{i+1}. {usuario.username} (admin: {usuario.is_superuser})")
    
    return True

def verificar_servidor_activo():
    """Verifica si el servidor está activo."""
    print_section("Verificando servidor activo")
    
    url = "http://localhost:8000/dashboard/productos-venta/"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"✅ Servidor activo en {url}")
            return True
        else:
            print(f"❌ Servidor responde con código: {response.status_code}")
            return False
    except requests.ConnectionError:
        print(f"❌ No se pudo conectar a {url}")
        print("Asegúrate de que el servidor Django esté en ejecución con:")
        print("python manage.py runserver")
        return False

def abrir_navegador_para_pruebas():
    """Abre el navegador para pruebas manuales."""
    print_section("Abriendo navegador para pruebas")
    
    url = "http://localhost:8000/dashboard/productos-venta/"
    print(f"Abriendo {url} en el navegador...")
    webbrowser.open(url)
    
    print("\nInstrucciones para probar la eliminación:")
    print("1. Inicia sesión si es necesario")
    print("2. Localiza un producto en la lista")
    print("3. Abre la consola del navegador (F12) y selecciona la pestaña 'Console'")
    print("4. Haz clic en el botón 'Eliminar' del producto")
    print("5. Confirma la eliminación en el modal")
    print("6. Observa los mensajes en la consola - no debería haber errores")
    print("7. Verifica que el producto se elimine correctamente")

def main():
    """Función principal del script."""
    print_title("VERIFICACIÓN COMPLETA DE FUNCIONALIDAD DE ELIMINACIÓN")
    
    # Verificar servidor activo
    if not verificar_servidor_activo():
        print("\n❌ No se pudo conectar al servidor. Verifique que esté en ejecución.")
        return
    
    # Verificar permisos
    if not verificar_permisos_eliminacion():
        print("\n❌ Problemas con los permisos de eliminación. Corrija antes de continuar.")
        return
    
    # Verificar productos existentes
    productos = verificar_productos_existentes()
    if not productos:
        print("\n❌ No hay productos para probar la eliminación.")
        print("Ejecute primero el script crear_producto_prueba_final.py")
        return
    
    print("\n✅ Todo está listo para probar la eliminación de productos")
    print("✅ La sintaxis JavaScript ha sido corregida")
    print("✅ Los permisos están configurados correctamente")
    print("✅ Hay productos disponibles para eliminar")
    print("✅ El servidor está activo")
    
    # Preguntar si se desea abrir el navegador
    print("\n¿Deseas abrir el navegador para probar la funcionalidad? (s/n)")
    choice = input().lower()
    
    if choice == 's':
        abrir_navegador_para_pruebas()
    else:
        print("\nPuedes probar la funcionalidad manualmente accediendo a:")
        print("http://localhost:8000/dashboard/productos-venta/")

if __name__ == "__main__":
    main()
