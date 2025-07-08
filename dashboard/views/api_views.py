from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from restaurant.models import ProductoVenta
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)

@login_required
@require_GET
def verificar_producto_api(request, producto_id):
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
            return JsonResponse({
                'exists': True,
                'id': producto_id,
                'nombre': producto.nombre,
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
        logger.error(f"[API-VERIFY] Error verificando producto ID {producto_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({
            'error': str(e),
            'exists': None,
            'id': producto_id,
            'timestamp': datetime.now().isoformat()
        }, status=500)

@login_required
@require_POST
def eliminar_forzado_api(request, producto_id):
    """
    API para forzar la eliminación de un producto, incluso si hay errores.
    Usado como último recurso para eliminaciones problemáticas.
    """
    logger.info(f"[API-FORCE-DELETE] Iniciando eliminación forzada de producto ID: {producto_id}")
    logger.info(f"[API-FORCE-DELETE] Timestamp: {datetime.now().isoformat()}")
    logger.info(f"[API-FORCE-DELETE] Usuario: {request.user.username}")
    logger.info(f"[API-FORCE-DELETE] Headers: {dict(request.headers)}")
    
    try:
        # Verificar si el usuario tiene permisos
        if not request.user.has_perm('restaurant.delete_productoventa'):
            logger.error(f"[API-FORCE-DELETE] Usuario sin permisos: {request.user.username}")
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para eliminar productos',
                'id': producto_id
            }, status=403)
        
        # Verificar si el producto existe
        try:
            producto = ProductoVenta.objects.get(id=producto_id)
            nombre_producto = producto.nombre
            logger.info(f"[API-FORCE-DELETE] Producto encontrado: {nombre_producto} (ID: {producto_id})")
        except ProductoVenta.DoesNotExist:
            logger.info(f"[API-FORCE-DELETE] Producto no existe ID: {producto_id}")
            return JsonResponse({
                'success': True,
                'message': 'El producto ya fue eliminado anteriormente',
                'id': producto_id
            })
        
        # Eliminar relaciones primero
        try:
            # ProductoReceta
            from restaurant.models import ProductoReceta
            relaciones = ProductoReceta.objects.filter(producto=producto)
            count = relaciones.count()
            if count > 0:
                relaciones.delete()
                logger.info(f"[API-FORCE-DELETE] Eliminadas {count} relaciones ProductoReceta")
            
            # ProductoCategoria
            from restaurant.models import ProductoCategoria
            categorias = ProductoCategoria.objects.filter(producto=producto)
            count = categorias.count()
            if count > 0:
                categorias.delete()
                logger.info(f"[API-FORCE-DELETE] Eliminadas {count} relaciones ProductoCategoria")
            
            # Receta (relación inversa)
            from restaurant.models import Receta
            recetas = Receta.objects.filter(producto=producto)
            count = recetas.count()
            if count > 0:
                recetas.update(producto=None)
                logger.info(f"[API-FORCE-DELETE] Actualizadas {count} relaciones Receta")
        except Exception as e:
            logger.warning(f"[API-FORCE-DELETE] Error limpiando relaciones: {e}")
        
        # Eliminar el producto con SQL directo si es necesario
        try:
            # Primero intentar con el ORM
            producto.delete()
            logger.info(f"[API-FORCE-DELETE] Producto eliminado exitosamente con ORM")
        except Exception as e:
            logger.error(f"[API-FORCE-DELETE] Error eliminando con ORM: {e}")
            
            # Intentar con SQL directo
            try:
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM restaurant_productoventa WHERE id = %s", [producto_id])
                    logger.info(f"[API-FORCE-DELETE] Producto eliminado con SQL directo, filas afectadas: {cursor.rowcount}")
            except Exception as sql_error:
                logger.error(f"[API-FORCE-DELETE] Error con SQL directo: {sql_error}")
                raise sql_error
        
        # Verificar si fue eliminado
        if not ProductoVenta.objects.filter(id=producto_id).exists():
            logger.info(f"[API-FORCE-DELETE] ÉXITO: Producto eliminado completamente")
            return JsonResponse({
                'success': True,
                'message': f'Producto "{nombre_producto}" eliminado exitosamente',
                'id': producto_id
            })
        else:
            logger.error(f"[API-FORCE-DELETE] FALLO: El producto sigue existiendo después de los intentos de eliminación")
            return JsonResponse({
                'success': False,
                'message': 'El producto no pudo ser eliminado. Contacte al administrador.',
                'id': producto_id
            }, status=500)
    except Exception as e:
        logger.error(f"[API-FORCE-DELETE] Error general: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}',
            'id': producto_id
        }, status=500)
