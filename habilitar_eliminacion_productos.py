#!/usr/bin/env python
"""
Script para habilitar la eliminación forzada de productos desde el frontend
"""

import os
import django
import sys
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Importar modelos necesarios
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from restaurant.models import ProductoVenta

# Obtener el modelo de usuario personalizado
User = get_user_model()

def print_separator(title=None):
    """Imprime un separador con título opcional"""
    if title:
        print("\n" + "="*20 + f" {title} " + "="*20)
    else:
        print("\n" + "="*50)

def modificar_vista_eliminar():
    """Modifica la vista de eliminación para permitir forzar la eliminación"""
    print_separator("MODIFICANDO VISTA DE ELIMINACIÓN")
    
    try:
        # Ruta al archivo de vistas
        ruta_vista = os.path.join('dashboard', 'views', 'productos_venta_views.py')
        
        if not os.path.exists(ruta_vista):
            print(f"ERROR: No se encontró el archivo {ruta_vista}")
            return False
        
        # Leer el contenido del archivo
        with open(ruta_vista, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Buscar las restricciones que bloquean la eliminación
        if 'if count_ordenes > 0:' in contenido and 'if count_ventas > 0:' in contenido:
            print("✓ Se encontraron las restricciones que bloquean la eliminación")
            print("Modificando para permitir forzar la eliminación...")
            
            # Buscar la sección de verificación de OrdenItem
            inicio_orden_item = contenido.find('# Verificar OrdenItem')
            if inicio_orden_item == -1:
                print("ERROR: No se encontró la sección de verificación de OrdenItem")
                return False
                
            fin_bloque_orden = contenido.find('# Verificar DetalleVenta', inicio_orden_item)
            if fin_bloque_orden == -1:
                print("ERROR: No se encontró el final del bloque de OrdenItem")
                return False
                
            bloque_orden = contenido[inicio_orden_item:fin_bloque_orden]
            
            # Modificar el bloque para añadir un parámetro force
            if 'force=False' not in contenido:
                # Buscar la definición de la función
                inicio_funcion = contenido.find('def eliminar_producto_venta(request, producto_id):')
                if inicio_funcion == -1:
                    print("ERROR: No se encontró la definición de la función eliminar_producto_venta")
                    return False
                
                # Modificar la definición para añadir el parámetro force
                nueva_definicion = 'def eliminar_producto_venta(request, producto_id, force=False):'
                contenido = contenido.replace('def eliminar_producto_venta(request, producto_id):', nueva_definicion)
                print("✓ Se añadió el parámetro force a la definición de la función")
                
                # Modificar los bloques de verificación para respetar el parámetro force
                nuevo_bloque_orden = bloque_orden.replace('if count_ordenes > 0:', 'if count_ordenes > 0 and not force:')
                contenido = contenido.replace(bloque_orden, nuevo_bloque_orden)
                print("✓ Se modificó el bloque de verificación de OrdenItem")
                
                # Buscar la sección de verificación de DetalleVenta
                inicio_detalle_venta = contenido.find('# Verificar DetalleVenta')
                if inicio_detalle_venta == -1:
                    print("ERROR: No se encontró la sección de verificación de DetalleVenta")
                    return False
                    
                fin_bloque_venta = contenido.find('# Verificar tablas huérfanas', inicio_detalle_venta)
                if fin_bloque_venta == -1:
                    print("ERROR: No se encontró el final del bloque de DetalleVenta")
                    return False
                    
                bloque_venta = contenido[inicio_detalle_venta:fin_bloque_venta]
                nuevo_bloque_venta = bloque_venta.replace('if count_ventas > 0:', 'if count_ventas > 0 and not force:')
                contenido = contenido.replace(bloque_venta, nuevo_bloque_venta)
                print("✓ Se modificó el bloque de verificación de DetalleVenta")
                
                # Guardar los cambios
                with open(ruta_vista, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                print("✓ Se guardaron los cambios en el archivo de vistas")
                
                return True
            else:
                print("La vista ya ha sido modificada anteriormente")
                return True
        else:
            print("No se encontraron las restricciones esperadas en el archivo")
            return False
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def modificar_urls():
    """Añade una URL para la eliminación forzada"""
    print_separator("MODIFICANDO URLS")
    
    try:
        # Ruta al archivo de URLs
        ruta_urls = os.path.join('dashboard', 'urls.py')
        
        if not os.path.exists(ruta_urls):
            print(f"ERROR: No se encontró el archivo {ruta_urls}")
            return False
        
        # Leer el contenido del archivo
        with open(ruta_urls, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar si ya existe la URL de eliminación forzada
        if "path('productos-venta/<int:producto_id>/eliminar-forzado/'" not in contenido:
            print("Añadiendo URL para eliminación forzada...")
            
            # Buscar la sección de URLs de productos de venta
            linea_eliminar = "path('productos-venta/<int:producto_id>/eliminar/', productos_venta_views.eliminar_producto_venta, name='eliminar_producto_venta'),"
            if linea_eliminar not in contenido:
                print("ERROR: No se encontró la URL de eliminación normal")
                return False
            
            # Añadir la URL de eliminación forzada después de la URL de eliminación normal
            nueva_linea = linea_eliminar + "\n    path('productos-venta/<int:producto_id>/eliminar-forzado/', lambda request, producto_id: productos_venta_views.eliminar_producto_venta(request, producto_id, force=True), name='eliminar_producto_venta_forzado'),"
            contenido = contenido.replace(linea_eliminar, nueva_linea)
            
            # Guardar los cambios
            with open(ruta_urls, 'w', encoding='utf-8') as f:
                f.write(contenido)
            print("✓ Se añadió la URL para eliminación forzada")
            
            return True
        else:
            print("La URL de eliminación forzada ya existe")
            return True
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def modificar_template():
    """Añade un botón de eliminación forzada al modal"""
    print_separator("MODIFICANDO TEMPLATE")
    
    try:
        # Ruta al archivo de template
        ruta_template = os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html')
        
        if not os.path.exists(ruta_template):
            print(f"ERROR: No se encontró el archivo {ruta_template}")
            return False
        
        # Leer el contenido del archivo
        with open(ruta_template, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar si ya existe el botón de eliminación forzada
        if 'id="btnEliminarForzado"' in contenido:
            print("El botón de eliminación forzada ya existe en el modal")
            
            # Asegurarse de que el código JavaScript para eliminar forzadamente funcione
            if "fetch(`/dashboard/productos-venta/${productoId}/eliminar-forzado/" not in contenido:
                print("Actualizando el código JavaScript para la eliminación forzada...")
                
                # Buscar la función btnEliminarForzado
                inicio_btn = contenido.find('document.getElementById(\'btnEliminarForzado\').addEventListener(\'click\', function() {')
                if inicio_btn == -1:
                    print("ERROR: No se encontró la función del botón de eliminación forzada")
                    return False
                
                fin_btn = contenido.find('});', inicio_btn)
                if fin_btn == -1:
                    print("ERROR: No se encontró el final de la función del botón de eliminación forzada")
                    return False
                
                bloque_btn = contenido[inicio_btn:fin_btn]
                
                # Reemplazar la URL en el fetch
                if 'fetch(`/dashboard/api/eliminar-forzado/${productoId}/' in bloque_btn:
                    nuevo_bloque = bloque_btn.replace(
                        'fetch(`/dashboard/api/eliminar-forzado/${productoId}/',
                        'fetch(`/dashboard/productos-venta/${productoId}/eliminar-forzado/'
                    )
                    contenido = contenido.replace(bloque_btn, nuevo_bloque)
                    
                    # Guardar los cambios
                    with open(ruta_template, 'w', encoding='utf-8') as f:
                        f.write(contenido)
                    print("✓ Se actualizó la URL para la eliminación forzada")
                    
                    return True
                else:
                    print("No se encontró la URL de la API en el bloque del botón")
                    return False
            else:
                print("El código JavaScript para la eliminación forzada ya está actualizado")
                return True
        else:
            print("Añadiendo botón de eliminación forzada al modal...")
            
            # Buscar el botón normal de eliminación
            boton_normal = '<button type="submit" class="btn btn-danger">Eliminar</button>'
            if boton_normal not in contenido:
                print("ERROR: No se encontró el botón normal de eliminación")
                return False
            
            # Añadir el botón de eliminación forzada
            nuevo_boton = boton_normal + '\n                    <button type="button" id="btnEliminarForzado" class="btn btn-warning ml-2">Forzar Eliminación</button>'
            contenido = contenido.replace(boton_normal, nuevo_boton)
            
            # Añadir el código JavaScript para el botón
            script_tag = '</script>\n{% endblock %}'
            if script_tag not in contenido:
                print("ERROR: No se encontró el final del bloque de script")
                return False
            
            # Añadir el código JavaScript antes del cierre del script
            codigo_js = """
    // Añadir manejador para el botón de eliminación forzada
    document.getElementById('btnEliminarForzado').addEventListener('click', function() {
        const productoId = document.getElementById('deleteForm').action.split('/').filter(Boolean).pop();
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch(`/dashboard/productos-venta/${productoId}/eliminar-forzado/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                response.json().then(data => {
                    alert('Error: ' + data.message);
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al comunicarse con el servidor');
        });
    });
"""
            contenido = contenido.replace(script_tag, codigo_js + script_tag)
            
            # Guardar los cambios
            with open(ruta_template, 'w', encoding='utf-8') as f:
                f.write(contenido)
            print("✓ Se añadió el botón de eliminación forzada y su código JavaScript")
            
            return True
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def asignar_permiso_usuarios():
    """Asigna el permiso de eliminación a todos los usuarios"""
    print_separator("ASIGNANDO PERMISOS A USUARIOS")
    
    try:
        # Obtener el permiso
        content_type = ContentType.objects.get_for_model(ProductoVenta)
        permiso = Permission.objects.get(
            codename='delete_productoventa',
            content_type=content_type
        )
        
        # Obtener todos los usuarios activos
        usuarios = User.objects.filter(is_active=True)
        print(f"Total de usuarios activos: {usuarios.count()}")
        
        # Asignar el permiso a cada usuario
        count = 0
        for usuario in usuarios:
            if not usuario.has_perm('restaurant.delete_productoventa'):
                usuario.user_permissions.add(permiso)
                count += 1
                print(f"✓ Permiso asignado a {usuario.username}")
            else:
                print(f"- {usuario.username} ya tiene el permiso")
        
        # Asignar el permiso al grupo de Usuarios
        try:
            grupo_usuarios = Group.objects.get(name='Usuarios')
            if permiso not in grupo_usuarios.permissions.all():
                grupo_usuarios.permissions.add(permiso)
                print(f"✓ Permiso asignado al grupo Usuarios")
            else:
                print(f"- El grupo Usuarios ya tiene el permiso")
        except Group.DoesNotExist:
            print("- El grupo Usuarios no existe")
        
        print(f"\nTotal: {count} usuarios actualizados")
        return True
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print_separator("HABILITACIÓN DE ELIMINACIÓN DE PRODUCTOS")
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Django version: {django.get_version()}")
    print(f"Python version: {sys.version}")
    
    # Ejecutar las modificaciones
    resultado_vista = modificar_vista_eliminar()
    print(f"\nModificación de vista: {'✓ COMPLETADA' if resultado_vista else '✗ FALLIDA'}")
    
    resultado_urls = modificar_urls()
    print(f"Modificación de URLs: {'✓ COMPLETADA' if resultado_urls else '✗ FALLIDA'}")
    
    resultado_template = modificar_template()
    print(f"Modificación de template: {'✓ COMPLETADA' if resultado_template else '✗ FALLIDA'}")
    
    resultado_permisos = asignar_permiso_usuarios()
    print(f"Asignación de permisos: {'✓ COMPLETADA' if resultado_permisos else '✗ FALLIDA'}")
    
    # Resumen final
    print_separator("RESUMEN")
    if resultado_vista and resultado_urls and resultado_template and resultado_permisos:
        print("✅ TODAS LAS MODIFICACIONES SE COMPLETARON EXITOSAMENTE")
        print("\nAhora puede eliminar productos desde el front-end, incluso aquellos con dependencias.")
        print("Utilice el botón 'Forzar Eliminación' para productos con dependencias.")
    else:
        print("⚠️ ALGUNAS MODIFICACIONES FALLARON")
        print("\nRevise los mensajes de error anteriores y corrija manualmente.")
    
    print("\nPara probar la funcionalidad:")
    print("1. Inicie sesión con un usuario administrador")
    print("2. Vaya a la lista de productos")
    print("3. Intente eliminar un producto (activo o inactivo)")
    print("4. Si el producto tiene dependencias, use el botón 'Forzar Eliminación'")

if __name__ == "__main__":
    main()
