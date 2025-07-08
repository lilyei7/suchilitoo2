import os
import re

def agregar_url_diagnostico():
    # Definir ruta del archivo
    urls_path = r'c:\Users\olcha\Desktop\sushi_restaurant - Copy (2)\suchilitoo2\dashboard\urls.py'
    
    # Verificar que el archivo existe
    if not os.path.exists(urls_path):
        print(f"Error: El archivo {urls_path} no existe.")
        return False
    
    # Leer el contenido
    with open(urls_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Crear una copia de seguridad
    backup_path = urls_path + '.backup'
    with open(backup_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Copia de seguridad creada en: {backup_path}")
    
    # Buscar dónde añadir la nueva URL
    # Comprobamos si la URL ya existe
    if "path('productos-venta/diagnostico/" in content:
        print("La URL de diagnóstico ya existe en urls.py.")
        return True
    
    # Buscar la última ruta de productos_venta
    import_line = "from dashboard.views import productos_venta_views as views"
    if import_line not in content:
        print("No se encontró la importación de vistas productos_venta en urls.py.")
        
        # Intentamos buscar un patrón más genérico
        productos_urls = re.findall(r"path\('productos-venta/.*?',.*?\),", content)
        if not productos_urls:
            print("No se encontraron rutas de productos-venta en urls.py.")
            return False
    
    # Preparar la nueva URL
    nueva_url = "    path('productos-venta/diagnostico/', views.diagnostico_view, name='diagnostico_view'),"
    
    # Intentar insertar después de la última ruta de productos_venta
    pattern = r"(path\('productos-venta/.*?',.*?\),)"
    last_match = None
    for match in re.finditer(pattern, content):
        last_match = match
    
    if last_match:
        insertion_point = last_match.end()
        content_modified = content[:insertion_point] + "\n" + nueva_url + content[insertion_point:]
        
        # Guardar el contenido modificado
        with open(urls_path, 'w', encoding='utf-8') as file:
            file.write(content_modified)
        
        print("✅ URL de diagnóstico añadida correctamente a urls.py")
    else:
        print("No se pudo encontrar un punto de inserción adecuado en urls.py")
        return False
    
    # Ahora crear la vista
    views_path = r'c:\Users\olcha\Desktop\sushi_restaurant - Copy (2)\suchilitoo2\dashboard\views\productos_venta_views.py'
    
    if os.path.exists(views_path):
        # Leer el contenido
        with open(views_path, 'r', encoding='utf-8') as file:
            views_content = file.read()
        
        # Comprobar si la vista ya existe
        if "def diagnostico_view" in views_content:
            print("La vista de diagnóstico ya existe en productos_venta_views.py.")
            return True
        
        # Crear copia de seguridad
        views_backup = views_path + '.backup'
        with open(views_backup, 'w', encoding='utf-8') as file:
            file.write(views_content)
        print(f"Copia de seguridad de views creada en: {views_backup}")
        
        # Añadir la vista de diagnóstico
        if "from django.contrib.auth.decorators import login_required" not in views_content:
            views_content = "from django.contrib.auth.decorators import login_required\n" + views_content
        
        nueva_vista = '''

@login_required
def diagnostico_view(request):
    """
    Vista para página de diagnóstico de JavaScript
    """
    print("DEBUG: Cargando página de diagnóstico de JavaScript")
    
    return render(request, 'dashboard/productos_venta/diagnostico.html', {
        'sidebar_active': 'productos_venta',
    })
'''
        
        # Añadir la vista al final del archivo
        with open(views_path, 'a', encoding='utf-8') as file:
            file.write(nueva_vista)
        
        print("✅ Vista de diagnóstico añadida correctamente a productos_venta_views.py")
        return True
    else:
        print(f"Error: El archivo de vistas {views_path} no existe.")
        return False

# Ejecutar la función
if __name__ == "__main__":
    agregar_url_diagnostico()
