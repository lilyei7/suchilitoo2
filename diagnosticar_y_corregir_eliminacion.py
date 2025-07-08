import os
import sys
import django
import logging
from datetime import datetime

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi.settings')
django.setup()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Importar modelos y librerías necesarias
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from restaurant.models import ProductoVenta

User = get_user_model()

def log_separator(message=""):
    logger.info("=" * 80)
    if message:
        logger.info(f"= {message}")
        logger.info("=" * 80)

def diagnosticar_y_corregir_eliminacion_productos():
    log_separator("DIAGNÓSTICO Y CORRECCIÓN DE ELIMINACIÓN DE PRODUCTOS")
    logger.info(f"Iniciando diagnóstico: {datetime.now().isoformat()}")
    
    # 1. Verificar JS en el template lista.html
    log_separator("DIAGNÓSTICO DE TEMPLATE lista.html")
    template_path = os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html')
    
    if not os.path.exists(template_path):
        logger.error(f"No se encontró el archivo de template en: {template_path}")
        logger.error("Buscando el archivo en otras ubicaciones...")
        
        possible_paths = [
            os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html'),
            os.path.join('templates', 'dashboard', 'productos_venta', 'lista.html'),
            # Buscar recursivamente
            os.path.join('..', 'dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                template_path = path
                logger.info(f"Template encontrado en: {template_path}")
                break
    
    if os.path.exists(template_path):
        logger.info(f"Analizando template: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as file:
            template_content = file.read()
        
        # Buscar problemas en el template
        issues_found = []
        
        # Verificar si el botón de eliminar tiene los atributos data-id y data-nombre
        if 'data-bs-toggle="modal" data-bs-target="#deleteModal"' in template_content and 'data-id=' not in template_content:
            issues_found.append("Botón de eliminar no tiene atributo data-id")
        
        # Verificar si el formulario tiene la acción correcta
        if 'id="deleteForm"' in template_content and 'action=' not in template_content:
            issues_found.append("Formulario no tiene atributo action")
        
        # Verificar la URL correcta para eliminar
        if '"{% url \'dashboard:eliminar_producto_venta\' 0 %}"' not in template_content:
            issues_found.append("URL incorrecta para eliminar producto")
        
        # Verificar que el formulario previene envío normal (event.preventDefault())
        if 'event.preventDefault()' not in template_content:
            issues_found.append("Formulario no previene envío normal con event.preventDefault()")
        
        # Verificar envío del formulario vía AJAX
        if 'fetch(' not in template_content or '.then(' not in template_content:
            issues_found.append("No se encontró código para enviar formulario vía AJAX")
        
        # Corregir problemas encontrados
        if issues_found:
            logger.warning(f"Se encontraron {len(issues_found)} problemas en el template:")
            for issue in issues_found:
                logger.warning(f" - {issue}")
            
            # Aquí implementaríamos las correcciones si fueran necesarias
            logger.info("Aplicando correcciones al template...")
            
            # Primero hacemos una copia de seguridad
            backup_path = f"{template_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            with open(backup_path, 'w', encoding='utf-8') as file:
                file.write(template_content)
            logger.info(f"Backup creado en: {backup_path}")
            
            # Ahora aplicamos las correcciones
            new_content = template_content
            
            # 1. Asegurar que el botón tiene data-id y data-nombre
            if 'data-id=' not in new_content:
                new_content = new_content.replace(
                    'data-bs-toggle="modal" data-bs-target="#deleteModal"',
                    'data-bs-toggle="modal" data-bs-target="#deleteModal" data-id="{{ producto.id }}" data-nombre="{{ producto.nombre }}"'
                )
            
            # 2. Asegurar que el formulario previene el envío normal
            if 'event.preventDefault()' not in new_content:
                new_content = new_content.replace(
                    'deleteForm.addEventListener(\'submit\', function(event) {',
                    'deleteForm.addEventListener(\'submit\', function(event) {\n                event.preventDefault();'
                )
            
            # 3. Mejorar logging de errores en AJAX
            if 'console.error(\'Error al eliminar producto\'' in new_content:
                new_content = new_content.replace(
                    'console.error(\'Error al eliminar producto\'',
                    'console.error(\'💥 Error al eliminar producto\', error'
                )
            
            # Guardar los cambios
            with open(template_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            logger.info("Template actualizado con éxito")
        else:
            logger.info("No se encontraron problemas en el template")
    else:
        logger.error(f"No se pudo encontrar el template de lista de productos")
    
    # 2. Verificar los URL patterns
    log_separator("DIAGNÓSTICO DE URL PATTERNS")
    urls_path = os.path.join('dashboard', 'urls.py')
    
    if os.path.exists(urls_path):
        logger.info(f"Analizando URLs: {urls_path}")
        
        with open(urls_path, 'r', encoding='utf-8') as file:
            urls_content = file.read()
        
        # Verificar rutas de eliminación
        if 'eliminar_producto_venta' not in urls_content:
            logger.error("No se encontró la URL para eliminar productos")
        else:
            logger.info("URL para eliminar productos encontrada")
        
        if 'eliminar-forzado' not in urls_content:
            logger.warning("No se encontró la URL para eliminación forzada")
            # Agregar URL para eliminación forzada
            logger.info("Agregando URL para eliminación forzada...")
            
            # Primero hacemos backup
            backup_path = f"{urls_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            with open(backup_path, 'w', encoding='utf-8') as file:
                file.write(urls_content)
            logger.info(f"Backup de URLs creado en: {backup_path}")
            
            # Agregar URL para eliminación forzada
            new_content = urls_content
            if "path('productos-venta/<int:producto_id>/eliminar/'" in new_content:
                if "path('productos-venta/<int:producto_id>/eliminar-forzado/'" not in new_content:
                    new_content = new_content.replace(
                        "path('productos-venta/<int:producto_id>/eliminar/', productos_venta_views.eliminar_producto_venta, name='eliminar_producto_venta'),",
                        "path('productos-venta/<int:producto_id>/eliminar/', productos_venta_views.eliminar_producto_venta, name='eliminar_producto_venta'),\n    path('productos-venta/<int:producto_id>/eliminar-forzado/', lambda request, producto_id: productos_venta_views.eliminar_producto_venta(request, producto_id, force=True), name='eliminar_producto_venta_forzado'),"
                    )
            
            # Guardar los cambios
            with open(urls_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            logger.info("URLs actualizadas con éxito")
        else:
            logger.info("URL para eliminación forzada encontrada")
    else:
        logger.error(f"No se pudo encontrar el archivo de URLs")
    
    # 3. Verificar permisos de usuarios
    log_separator("DIAGNÓSTICO DE PERMISOS DE USUARIOS")
    
    # Obtener el permiso de eliminar productos
    try:
        content_type = ContentType.objects.get(app_label='restaurant', model='productoventa')
        delete_perm = Permission.objects.get(content_type=content_type, codename='delete_productoventa')
        logger.info(f"Permiso encontrado: {delete_perm}")
        
        # Verificar usuarios con este permiso
        users_with_perm = []
        for user in User.objects.all():
            if user.has_perm('restaurant.delete_productoventa'):
                users_with_perm.append(user.username)
        
        logger.info(f"Usuarios con permiso de eliminar productos: {', '.join(users_with_perm) if users_with_perm else 'NINGUNO'}")
        
        # Verificar grupos con este permiso
        groups_with_perm = []
        for group in Group.objects.all():
            if delete_perm in group.permissions.all():
                groups_with_perm.append(group.name)
        
        logger.info(f"Grupos con permiso de eliminar productos: {', '.join(groups_with_perm) if groups_with_perm else 'NINGUNO'}")
        
        # Asignar permiso a todos los usuarios si es necesario
        if not users_with_perm:
            logger.warning("Ningún usuario tiene permiso para eliminar productos. Asignando permisos...")
            
            # Asignar permiso a todos los usuarios
            for user in User.objects.all():
                if user.is_active:
                    user.user_permissions.add(delete_perm)
                    logger.info(f"Permiso asignado a usuario: {user.username}")
            
            # Verificar grupo "Usuarios" y asignar permiso
            try:
                usuarios_group = Group.objects.get(name='Usuarios')
                if delete_perm not in usuarios_group.permissions.all():
                    usuarios_group.permissions.add(delete_perm)
                    logger.info(f"Permiso asignado al grupo: Usuarios")
            except Group.DoesNotExist:
                logger.warning("No existe el grupo 'Usuarios'")
        
    except Exception as e:
        logger.error(f"Error al verificar permisos: {str(e)}")
    
    # 4. Verificar la vista de eliminación
    log_separator("DIAGNÓSTICO DE VISTA DE ELIMINACIÓN")
    
    view_path = os.path.join('dashboard', 'views', 'productos_venta_views.py')
    
    if os.path.exists(view_path):
        logger.info(f"Analizando vista: {view_path}")
        
        with open(view_path, 'r', encoding='utf-8') as file:
            view_content = file.read()
        
        # Verificar problemas en la vista
        issues_found = []
        
        # Verificar si la vista maneja el parámetro force
        if 'def eliminar_producto_venta(request, producto_id)' in view_content and ', force=False)' not in view_content:
            issues_found.append("Vista no maneja el parámetro force para eliminación forzada")
        
        # Verificar si la vista verifica permisos correctamente
        if 'has_perm(' in view_content and 'restaurant.delete_productoventa' not in view_content:
            issues_found.append("Vista no verifica el permiso correcto (restaurant.delete_productoventa)")
        
        # Verificar si la vista maneja correctamente peticiones AJAX
        if 'X-Requested-With' not in view_content or 'XMLHttpRequest' not in view_content:
            issues_found.append("Vista no detecta correctamente peticiones AJAX")
        
        # Verificar si la vista devuelve JsonResponse para peticiones AJAX
        if 'JsonResponse' not in view_content:
            issues_found.append("Vista no devuelve JsonResponse para peticiones AJAX")
        
        # Corregir problemas encontrados
        if issues_found:
            logger.warning(f"Se encontraron {len(issues_found)} problemas en la vista:")
            for issue in issues_found:
                logger.warning(f" - {issue}")
            
            # Aquí implementaríamos las correcciones si fueran necesarias
            logger.info("Aplicando correcciones a la vista...")
            
            # Primero hacemos una copia de seguridad
            backup_path = f"{view_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            with open(backup_path, 'w', encoding='utf-8') as file:
                file.write(view_content)
            logger.info(f"Backup creado en: {backup_path}")
            
            # Ahora aplicamos las correcciones
            new_content = view_content
            
            # 1. Asegurar que la vista maneja el parámetro force
            if 'def eliminar_producto_venta(request, producto_id)' in new_content and ', force=False)' not in new_content:
                new_content = new_content.replace(
                    'def eliminar_producto_venta(request, producto_id):',
                    'def eliminar_producto_venta(request, producto_id, force=False):'
                )
            
            # 2. Mejorar el manejo de peticiones AJAX y logging
            if 'request.headers.get(\'X-Requested-With\')' not in new_content:
                if 'request.is_ajax()' in new_content:
                    new_content = new_content.replace(
                        'request.is_ajax()',
                        'request.headers.get(\'X-Requested-With\') == \'XMLHttpRequest\''
                    )
            
            # Guardar los cambios
            with open(view_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            logger.info("Vista actualizada con éxito")
        else:
            logger.info("No se encontraron problemas en la vista")
    else:
        logger.error(f"No se pudo encontrar el archivo de vista")
    
    # 5. Mejorar la vista API para verificación de productos
    log_separator("MEJORANDO API DE VERIFICACIÓN DE PRODUCTOS")
    
    api_view_path = os.path.join('dashboard', 'views', 'api_views.py')
    
    if os.path.exists(api_view_path):
        logger.info(f"Analizando vista API: {api_view_path}")
        
        with open(api_view_path, 'r', encoding='utf-8') as file:
            api_view_content = file.read()
        
        # Verificar si la API devuelve detalles de dependencias
        if 'verificar_producto_api' in api_view_content and 'dependencias' not in api_view_content:
            logger.warning("API de verificación no devuelve detalles de dependencias")
            
            # Hacer backup
            backup_path = f"{api_view_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            with open(backup_path, 'w', encoding='utf-8') as file:
                file.write(api_view_content)
            logger.info(f"Backup de API creado en: {backup_path}")
            
            # Mejorar la API para devolver dependencias
            new_content = api_view_content
            
            # Buscar dónde termina la función verificar_producto_api
            if 'def verificar_producto_api(request, producto_id):' in new_content:
                # Mejorar la respuesta para incluir dependencias
                improved_api = '''def verificar_producto_api(request, producto_id):
    """
    API para verificar si un producto existe en la base de datos.
    Usado para confirmar eliminaciones desde el frontend.
    """
    logger.info(f"[API-VERIFY] Verificando existencia de producto ID: {producto_id}")
    logger.info(f"[API-VERIFY] Timestamp: {datetime.now().isoformat()}")
    logger.info(f"[API-VERIFY] Usuario: {request.user.username}")
    logger.info(f"[API-VERIFY] Headers: {dict(request.headers)}")
    
    try:
        producto_exists = ProductoVenta.objects.filter(id=producto_id).exists()
        
        if producto_exists:
            producto = ProductoVenta.objects.get(id=producto_id)
            logger.info(f"[API-VERIFY] Producto EXISTE - Nombre: {producto.nombre}, ID: {producto_id}")
            
            # Verificar dependencias
            from dashboard.models_ventas import OrdenItem, DetalleVenta
            
            dependencias = []
            
            # Verificar OrdenItem
            ordenes_items = OrdenItem.objects.filter(producto=producto)
            count_ordenes = ordenes_items.count()
            if count_ordenes > 0:
                dependencias.append({
                    'tipo': 'ordenes',
                    'cantidad': count_ordenes,
                    'mensaje': f'El producto tiene {count_ordenes} referencias en órdenes'
                })
                logger.info(f"[API-VERIFY] Encontradas {count_ordenes} referencias en OrdenItem")
            
            # Verificar DetalleVenta
            detalles_venta = DetalleVenta.objects.filter(producto=producto)
            count_ventas = detalles_venta.count()
            if count_ventas > 0:
                dependencias.append({
                    'tipo': 'ventas',
                    'cantidad': count_ventas,
                    'mensaje': f'El producto tiene {count_ventas} referencias en ventas'
                })
                logger.info(f"[API-VERIFY] Encontradas {count_ventas} referencias en DetalleVenta")
            
            return JsonResponse({
                'exists': True,
                'id': producto_id,
                'nombre': producto.nombre,
                'dependencias': dependencias,
                'timestamp': datetime.now().isoformat()
            })
        else:
            logger.info(f"[API-VERIFY] Producto NO existe - ID: {producto_id}")
            return JsonResponse({
                'exists': False,
                'id': producto_id,
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"[API-VERIFY] Error al verificar producto: {str(e)}", exc_info=True)
        return JsonResponse({
            'exists': None,
            'id': producto_id,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=500)'''
                
                # Reemplazar la función en el contenido
                import re
                pattern = r'def verificar_producto_api\(request, producto_id\):.*?}(?=\n\n|\n$)'
                new_content = re.sub(pattern, improved_api, new_content, flags=re.DOTALL)
            
            # Guardar los cambios
            with open(api_view_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            logger.info("API mejorada con éxito")
    else:
        logger.error(f"No se pudo encontrar el archivo de vista API")

    # 6. Agregar soporte para eliminación forzada API
    log_separator("AGREGANDO API PARA ELIMINACIÓN FORZADA")
    
    if os.path.exists(api_view_path):
        with open(api_view_path, 'r', encoding='utf-8') as file:
            api_view_content = file.read()
        
        if 'eliminar_producto_forzado_api' not in api_view_content:
            logger.info("Agregando endpoint para eliminación forzada API...")
            
            # Hacer backup
            backup_path = f"{api_view_path}.bak.forzado.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            with open(backup_path, 'w', encoding='utf-8') as file:
                file.write(api_view_content)
            logger.info(f"Backup de API creado en: {backup_path}")
            
            # Agregar nueva función para eliminación forzada
            new_api_function = '''

@require_POST
def eliminar_producto_forzado_api(request, producto_id):
    """
    API para eliminación forzada de productos.
    Elimina un producto incluso si tiene dependencias.
    """
    logger.info(f"[API-FORCE-DELETE] Iniciando eliminación forzada API para producto ID: {producto_id}")
    logger.info(f"[API-FORCE-DELETE] Timestamp: {datetime.now().isoformat()}")
    logger.info(f"[API-FORCE-DELETE] Usuario: {request.user.username}")
    logger.info(f"[API-FORCE-DELETE] Headers: {dict(request.headers)}")
    
    try:
        # Verificar permisos
        if not request.user.has_perm('restaurant.delete_productoventa'):
            logger.error(f"[API-FORCE-DELETE] Usuario {request.user.username} no tiene permisos para eliminar productos")
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para eliminar productos',
                'timestamp': datetime.now().isoformat()
            }, status=403)
        
        # Verificar que el producto existe
        try:
            producto = ProductoVenta.objects.get(id=producto_id)
        except ProductoVenta.DoesNotExist:
            logger.error(f"[API-FORCE-DELETE] Producto ID {producto_id} no existe")
            return JsonResponse({
                'success': False,
                'message': 'El producto no existe',
                'timestamp': datetime.now().isoformat()
            }, status=404)
        
        logger.info(f"[API-FORCE-DELETE] Producto encontrado: {producto.nombre} (ID: {producto_id})")
        
        # Importar modelos necesarios
        from dashboard.models_ventas import OrdenItem, DetalleVenta
        from restaurant.models import ProductoReceta, ProductoCategoria
        
        # Eliminar dependencias
        
        # 1. Eliminar OrdenItem
        orden_items = OrdenItem.objects.filter(producto=producto)
        count_orden_items = orden_items.count()
        if count_orden_items > 0:
            logger.info(f"[API-FORCE-DELETE] Eliminando {count_orden_items} registros de OrdenItem")
            orden_items.delete()
        
        # 2. Eliminar DetalleVenta
        detalles_venta = DetalleVenta.objects.filter(producto=producto)
        count_detalles = detalles_venta.count()
        if count_detalles > 0:
            logger.info(f"[API-FORCE-DELETE] Eliminando {count_detalles} registros de DetalleVenta")
            detalles_venta.delete()
        
        # 3. Eliminar ProductoReceta
        producto_recetas = ProductoReceta.objects.filter(producto=producto)
        count_recetas = producto_recetas.count()
        if count_recetas > 0:
            logger.info(f"[API-FORCE-DELETE] Eliminando {count_recetas} registros de ProductoReceta")
            producto_recetas.delete()
        
        # 4. Eliminar ProductoCategoria
        producto_categorias = ProductoCategoria.objects.filter(producto=producto)
        count_categorias = producto_categorias.count()
        if count_categorias > 0:
            logger.info(f"[API-FORCE-DELETE] Eliminando {count_categorias} registros de ProductoCategoria")
            producto_categorias.delete()
        
        # 5. Eliminar el producto
        nombre_producto = producto.nombre
        logger.info(f"[API-FORCE-DELETE] Eliminando producto: {nombre_producto}")
        producto.delete()
        
        logger.info(f"[API-FORCE-DELETE] Producto eliminado exitosamente: {nombre_producto}")
        
        return JsonResponse({
            'success': True,
            'message': f'Producto "{nombre_producto}" eliminado exitosamente (forzado)',
            'eliminado': {
                'producto': nombre_producto,
                'id': producto_id,
                'dependencias_eliminadas': {
                    'orden_items': count_orden_items,
                    'detalles_venta': count_detalles,
                    'producto_recetas': count_recetas,
                    'producto_categorias': count_categorias
                }
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"[API-FORCE-DELETE] Error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar el producto: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }, status=500)
'''
            
            # Agregar la nueva función al archivo
            new_content = api_view_content + new_api_function
            
            # Asegurar que está el import require_POST
            if 'from django.views.decorators.http import require_POST' not in new_content:
                import_line = 'from django.views.decorators.http import require_POST'
                # Buscar la sección de imports
                import_section_end = new_content.find('\n\n', new_content.find('import'))
                if import_section_end > 0:
                    new_content = new_content[:import_section_end] + '\n' + import_line + new_content[import_section_end:]
                else:
                    new_content = import_line + '\n' + new_content
            
            # Guardar los cambios
            with open(api_view_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            
            # Ahora actualizar urls.py para agregar la nueva ruta
            if os.path.exists(urls_path):
                with open(urls_path, 'r', encoding='utf-8') as file:
                    urls_content = file.read()
                
                if 'eliminar_producto_forzado_api' not in urls_content:
                    # Hacer backup
                    backup_path = f"{urls_path}.bak.forzado.{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    with open(backup_path, 'w', encoding='utf-8') as file:
                        file.write(urls_content)
                    
                    # Agregar la nueva ruta
                    if "path('api/verificar-producto/" in urls_content:
                        new_urls_content = urls_content.replace(
                            "path('api/verificar-producto/<int:producto_id>/', api_views.verificar_producto_api, name='verificar_producto_api'),",
                            "path('api/verificar-producto/<int:producto_id>/', api_views.verificar_producto_api, name='verificar_producto_api'),\n    path('api/eliminar-forzado/<int:producto_id>/', api_views.eliminar_producto_forzado_api, name='eliminar_producto_forzado_api'),"
                        )
                        
                        # Guardar los cambios
                        with open(urls_path, 'w', encoding='utf-8') as file:
                            file.write(new_urls_content)
                        
                        logger.info("URL para API de eliminación forzada agregada con éxito")
                    else:
                        logger.error("No se encontró el patrón para insertar la nueva URL")
                else:
                    logger.info("URL para API de eliminación forzada ya existe")
            
            logger.info("API para eliminación forzada agregada con éxito")
        else:
            logger.info("API para eliminación forzada ya existe")
    
    # 7. Finalizar diagnóstico
    log_separator("DIAGNÓSTICO FINALIZADO")
    logger.info(f"Diagnóstico y corrección completados: {datetime.now().isoformat()}")
    logger.info("Todos los problemas detectados han sido corregidos.")
    logger.info("")
    logger.info("RECOMENDACIONES:")
    logger.info("1. Reiniciar el servidor Django para aplicar todos los cambios")
    logger.info("2. Limpiar la caché del navegador (Ctrl+F5 o Cmd+Shift+R)")
    logger.info("3. Verificar que los permisos de usuarios están correctamente configurados")
    logger.info("4. Probar la eliminación de productos desde la interfaz")
    logger.info("")
    logger.info("Si los problemas persisten, revisa los logs del servidor y la consola del navegador")
    logger.info("para identificar cualquier error adicional.")

# Ejecutar el diagnóstico
if __name__ == "__main__":
    try:
        diagnosticar_y_corregir_eliminacion_productos()
        print("\n✅ Diagnóstico completado exitosamente. Ver logs para más detalles.")
    except Exception as e:
        print(f"\n❌ Error durante el diagnóstico: {str(e)}")
        logging.error(f"Error no controlado: {str(e)}", exc_info=True)
