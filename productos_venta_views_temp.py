from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, F, Value, DecimalField
from django.urls import reverse
from restaurant.models import ProductoVenta, CategoriaProducto, Receta, ProductoReceta, ProductoCategoria
from decimal import Decimal
import json
import logging

@login_required
@permission_required('restaurant.view_productoventa', raise_exception=True)
def lista_productos_venta(request):
    """Vista que muestra la lista de productos de venta"""
    productos = ProductoVenta.objects.all().order_by('categoria__nombre', 'nombre')
    categorias = CategoriaProducto.objects.filter(activo=True).order_by('nombre')
    
    # Filtros por categoría o búsqueda
    categoria_id = request.GET.get('categoria')
    query = request.GET.get('q')
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | 
            Q(codigo__icontains=query) | 
            Q(descripcion__icontains=query)
        )
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_id,
        'query': query,
    }
    
    return render(request, 'dashboard/productos_venta/lista.html', context)

@login_required
@permission_required('restaurant.add_productoventa', raise_exception=True)
def crear_producto_venta(request):
    """Vista para crear un nuevo producto de venta"""
    categorias = CategoriaProducto.objects.filter(activo=True).order_by('nombre')
    recetas_disponibles = Receta.objects.filter(activo=True).order_by('producto__nombre')
    
    if request.method == 'POST':
        # Obtener datos del formulario
        codigo = request.POST.get('codigo')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        categoria_id = request.POST.get('categoria')
        disponible = request.POST.get('disponible') == 'on'
        calorias = request.POST.get('calorias', 0)
        imagen = request.FILES.get('imagen')
        
        # Recetas seleccionadas (puede ser múltiple)
        recetas_ids = request.POST.getlist('recetas')
        
        try:
            # Crear el producto
            producto = ProductoVenta.objects.create(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                precio=Decimal(precio),
                categoria_id=categoria_id,
                disponible=disponible,
                calorias=calorias,
                imagen=imagen
            )
            
            # Asociar las recetas seleccionadas
            for receta_id in recetas_ids:
                receta = Receta.objects.get(id=receta_id)
                ProductoReceta.objects.create(
                    producto=producto,
                    receta=receta
                )
            
            # Calcular costo basado en las recetas
            producto.calcular_costo_desde_recetas()
            
            messages.success(request, f'Producto "{nombre}" creado exitosamente.')
            return redirect('dashboard:lista_productos_venta')
            
        except Exception as e:
            messages.error(request, f'Error al crear el producto: {str(e)}')
    
    context = {
        'categorias': categorias,
        'recetas_disponibles': recetas_disponibles,
    }
    
    return render(request, 'dashboard/productos_venta/crear.html', context)

@login_required
@permission_required('restaurant.change_productoventa', raise_exception=True)
def editar_producto_venta(request, producto_id):
    """Vista para editar un producto de venta existente"""
    producto = get_object_or_404(ProductoVenta, id=producto_id)
    categorias = CategoriaProducto.objects.filter(activo=True).order_by('nombre')
    recetas_disponibles = Receta.objects.filter(activo=True).order_by('producto__nombre')
    
    # Obtener las recetas actualmente asociadas
    recetas_asociadas = ProductoReceta.objects.filter(producto=producto).values_list('receta_id', flat=True)
    
    if request.method == 'POST':
        # Obtener datos del formulario
        codigo = request.POST.get('codigo')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        categoria_id = request.POST.get('categoria')
        disponible = request.POST.get('disponible') == 'on'
        calorias = request.POST.get('calorias', 0)
        imagen = request.FILES.get('imagen')
        
        # Recetas seleccionadas (puede ser múltiple)
        recetas_ids = request.POST.getlist('recetas')
        
        try:
            # Actualizar el producto
            producto.codigo = codigo
            producto.nombre = nombre
            producto.descripcion = descripcion
            producto.precio = Decimal(precio)
            producto.categoria_id = categoria_id
            producto.disponible = disponible
            producto.calorias = calorias
            if imagen:
                producto.imagen = imagen
            producto.save()
            
            # Actualizar las recetas asociadas
            # Primero eliminar todas las asociaciones existentes
            ProductoReceta.objects.filter(producto=producto).delete()
            
            # Luego crear las nuevas asociaciones
            for receta_id in recetas_ids:
                receta = Receta.objects.get(id=receta_id)
                ProductoReceta.objects.create(
                    producto=producto,
                    receta=receta
                )
            
            # Recalcular costo basado en las recetas
            producto.calcular_costo_desde_recetas()
            
            messages.success(request, f'Producto "{nombre}" actualizado exitosamente.')
            return redirect('dashboard:lista_productos_venta')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el producto: {str(e)}')
    
    context = {
        'producto': producto,
        'categorias': categorias,
        'recetas_disponibles': recetas_disponibles,
        'recetas_asociadas': list(recetas_asociadas),
    }
    
    return render(request, 'dashboard/productos_venta/editar.html', context)

@login_required
def eliminar_producto_venta(request, producto_id):
    """Vista para eliminar un producto de venta"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"=== ELIMINACIÓN INICIADA ===")
        logger.info(f"Producto ID recibido: {producto_id} (tipo: {type(producto_id)})")
        logger.info(f"Producto ID como string: '{str(producto_id)}'")
        logger.info(f"Producto ID es numérico: {str(producto_id).isdigit()}")
        
        # Convertir producto_id a entero de forma segura
        try:
            producto_id_int = int(producto_id)
            logger.info(f"Producto ID convertido a int: {producto_id_int}")
        except (ValueError, TypeError) as e:
            logger.error(f"Error al convertir producto_id a int: {e}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'ID de producto inválido'
                }, status=400)
            messages.error(request, 'ID de producto inválido')
            return redirect('dashboard:productos_venta_moderna')
        
        logger.info(f"Usuario: {request.user.username} (ID: {request.user.id})")
        logger.info(f"Usuario autenticado: {request.user.is_authenticated}")
        logger.info(f"Usuario activo: {request.user.is_active}")
        logger.info(f"Método HTTP: {request.method}")
        logger.info(f"Headers AJAX: {request.headers.get('X-Requested-With')}")
        logger.info(f"Content-Type: {request.headers.get('Content-Type')}")
        logger.info(f"POST data: {dict(request.POST)}")
        logger.info(f"GET data: {dict(request.GET)}")
        logger.info(f"User-Agent: {request.headers.get('User-Agent')}")
        logger.info(f"Referer: {request.headers.get('Referer')}")
        
        # Verificar que sea POST
        if request.method != 'POST':
            logger.error(f"Método no permitido: {request.method}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Método no permitido'
                }, status=405)
            return redirect('dashboard:productos_venta_moderna')
        
    except Exception as e:
        logger.error(f"Error en el inicio de la función: {str(e)}", exc_info=True)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error en el inicio: {str(e)}'
            }, status=500)
        messages.error(request, f'Error en el inicio: {str(e)}')
        return redirect('dashboard:productos_venta_moderna')
    
    try:
        logger.info("=== INICIANDO VERIFICACIÓN DE PERMISOS ===")
        # Verificar permisos manualmente
        logger.info(f"Verificando permisos para usuario: {request.user.username}")
        logger.info(f"Es superusuario: {request.user.is_superuser}")
        logger.info(f"Es staff: {request.user.is_staff}")
        
        try:
            user_groups = [group.name for group in request.user.groups.all()]
            logger.info(f"Grupos del usuario: {user_groups}")
        except Exception as e:
            logger.error(f"Error obteniendo grupos del usuario: {e}")
            user_groups = []
        
        try:
            has_delete_perm = request.user.has_perm('restaurant.delete_productoventa')
            logger.info(f"Tiene permiso delete_productoventa: {has_delete_perm}")
        except Exception as e:
            logger.error(f"Error verificando permisos: {e}")
            has_delete_perm = False
        
        if not has_delete_perm:
            logger.error(f"Usuario sin permisos: {request.user.username}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Sin permisos para eliminar productos'
                }, status=403)
            messages.error(request, 'Sin permisos para eliminar productos')
            return redirect('dashboard:productos_venta_moderna')
        
        logger.info("=== PERMISOS VERIFICADOS EXITOSAMENTE ===")
        
        # Buscar el producto
        logger.info("=== INICIANDO BÚSQUEDA DE PRODUCTO ===")
        logger.info(f"Buscando producto con ID: {producto_id_int}")
        
        try:
            # Verificar si el modelo ProductoVenta existe
            logger.info(f"Modelo ProductoVenta: {ProductoVenta}")
            logger.info(f"Manager de ProductoVenta: {ProductoVenta.objects}")
            
            # Intentar obtener el producto
            producto = ProductoVenta.objects.get(id=producto_id_int)
            logger.info(f"Producto encontrado exitosamente:")
            logger.info(f"  - ID: {producto.id}")
            logger.info(f"  - Nombre: {producto.nombre}")
            logger.info(f"  - Código: {getattr(producto, 'codigo', 'N/A')}")
            logger.info(f"  - Categoría: {getattr(producto, 'categoria', 'N/A')}")
            
        except ProductoVenta.DoesNotExist as e:
            logger.error(f"Producto no existe con ID {producto_id_int}: {e}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Producto no encontrado'
                }, status=404)
            messages.error(request, 'Producto no encontrado')
            return redirect('dashboard:productos_venta_moderna')
        except Exception as e:
            logger.error(f"Error inesperado buscando producto: {e}", exc_info=True)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error buscando producto: {str(e)}'
                }, status=500)
            messages.error(request, f'Error buscando producto: {str(e)}')
            return redirect('dashboard:productos_venta_moderna')
        
        logger.info("=== PRODUCTO ENCONTRADO EXITOSAMENTE ===")
        
        # Eliminar el producto y sus relaciones
        nombre_producto = producto.nombre
        logger.info(f"=== INICIANDO PROCESO DE ELIMINACIÓN ===")
        logger.info(f"Producto a eliminar: {nombre_producto} (ID: {producto.id})")
        
        try:
            # Importar los modelos necesarios
            from dashboard.models_ventas import OrdenItem, DetalleVenta
            from django.db import connection
            
            # 0. Verificar si existen referencias protegidas (que bloquearían la eliminación)
            logger.info("0. Verificando referencias protegidas...")
            
            # Verificar OrdenItem
            ordenes_items = OrdenItem.objects.filter(producto=producto)
            count_ordenes = ordenes_items.count()
            logger.info(f"   Encontradas {count_ordenes} referencias en OrdenItem")
            
            if count_ordenes > 0:
                logger.warning(f"   El producto tiene {count_ordenes} referencias en órdenes")
                error_message = f'No se puede eliminar el producto "{nombre_producto}" porque tiene {count_ordenes} referencias en órdenes de venta. Elimine primero las órdenes relacionadas o contacte al administrador.'
                logger.error(error_message)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_message
                    }, status=400)
                messages.error(request, error_message)
                return redirect('dashboard:productos_venta_moderna')
            
            # Verificar DetalleVenta
            detalles_venta = DetalleVenta.objects.filter(producto=producto)
            count_ventas = detalles_venta.count()
            logger.info(f"   Encontradas {count_ventas} referencias en DetalleVenta")
            
            if count_ventas > 0:
                logger.warning(f"   El producto tiene {count_ventas} referencias en ventas")
                error_message = f'No se puede eliminar el producto "{nombre_producto}" porque tiene {count_ventas} referencias en ventas realizadas. No es posible eliminar productos que ya han sido vendidos por razones de auditoría.'
                logger.error(error_message)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_message
                    }, status=400)
                messages.error(request, error_message)
                return redirect('dashboard:productos_venta_moderna')
            
            # Verificar tablas huérfanas (tablas que no tienen modelo Django pero referencian ProductoVenta)
            logger.info("   Verificando tablas huérfanas...")
            with connection.cursor() as cursor:
                # Lista de tablas conocidas que podrían tener referencias huérfanas
                tablas_huerfanas = ['mesero_ordenitem', 'mesero_orden']
                
                for tabla in tablas_huerfanas:
                    try:
                        cursor.execute(f'SELECT COUNT(*) FROM {tabla} WHERE producto_id = %s', [producto.id])
                        count = cursor.fetchone()[0]
                        if count > 0:
                            logger.warning(f"   Encontradas {count} referencias huérfanas en {tabla}")
                            
                            # Preguntar al usuario si desea eliminar los datos huérfanos
                            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                                return JsonResponse({
                                    'success': False,
                                    'message': f'El producto tiene {count} referencias en una tabla huérfana ({tabla}). Contacte al administrador para limpiar estos datos antes de eliminar el producto.',
                                    'orphan_table': tabla,
                                    'orphan_count': count
                                }, status=400)
                            messages.error(request, f'El producto tiene referencias en una tabla huérfana ({tabla}). Contacte al administrador.')
                            return redirect('dashboard:productos_venta_moderna')
                        else:
                            logger.debug(f"   Tabla {tabla}: sin referencias ({count})")
                    except Exception as e:
                        logger.debug(f"   Tabla {tabla} no existe o error verificando: {e}")
                        continue
            
            logger.info("   No se encontraron referencias protegidas, procediendo con la eliminación")
            
            # Verificar el modelo ProductoReceta
            logger.info(f"Modelo ProductoReceta: {ProductoReceta}")
            logger.info(f"Manager de ProductoReceta: {ProductoReceta.objects}")
            
            # 1. Eliminar las relaciones ProductoReceta
            logger.info("1. Eliminando relaciones ProductoReceta...")
            relaciones_producto = ProductoReceta.objects.filter(producto=producto)
            count_relaciones = relaciones_producto.count()
            logger.info(f"   Encontradas {count_relaciones} relaciones ProductoReceta para eliminar")
            
            if count_relaciones > 0:
                for relacion in relaciones_producto:
                    logger.info(f"   - Eliminando relación: Producto {relacion.producto.nombre} -> Receta {relacion.receta.id if relacion.receta else 'N/A'}")
                
                relaciones_producto.delete()
                logger.info(f"   Eliminadas {count_relaciones} relaciones ProductoReceta exitosamente")
            else:
                logger.info("   No hay relaciones ProductoReceta para eliminar")
            
            # 2. Eliminar las relaciones ProductoCategoria
            logger.info("2. Eliminando relaciones ProductoCategoria...")
            categorias_producto = ProductoCategoria.objects.filter(producto=producto)
            count_categorias = categorias_producto.count()
            logger.info(f"   Encontradas {count_categorias} relaciones ProductoCategoria para eliminar")
            
            if count_categorias > 0:
                for categoria in categorias_producto:
                    logger.info(f"   - Eliminando categoría: Producto {categoria.producto.nombre} -> Categoría {categoria.categoria.nombre}")
                
                categorias_producto.delete()
                logger.info(f"   Eliminadas {count_categorias} relaciones ProductoCategoria exitosamente")
            else:
                logger.info("   No hay relaciones ProductoCategoria para eliminar")
            
            # 3. Manejar la receta asociada (OneToOneField)
            logger.info("3. Manejando la receta asociada...")
            try:
                # Intentar obtener la receta directamente mediante el campo OneToOneField
                receta = producto.receta
                if receta:
                    logger.info(f"   - Receta encontrada: {receta}")
                    # Desenlazar la receta del producto antes de eliminar el producto
                    receta.producto = None
                    receta.save()
                    logger.info("   - Receta desenlazada del producto exitosamente")
                else:
                    logger.info("   No hay receta directamente asociada")
            except Receta.DoesNotExist:
                logger.info("   No hay receta directamente asociada (DoesNotExist)")
            except Exception as e:
                logger.warning(f"   Error al manejar la receta: {e}")
            
            # 4. Ahora eliminar el producto
            logger.info(f"4. Eliminando producto: {nombre_producto}")
            producto.delete()
            logger.info(f"   Producto eliminado exitosamente: {nombre_producto}")
            
        except Exception as e:
            logger.error(f"Error durante el proceso de eliminación: {str(e)}", exc_info=True)
            logger.error(f"Tipo de error: {type(e).__name__}")
            logger.error(f"Args del error: {e.args}")
            raise e  # Re-lanzar la exception para que sea capturada por el except principal
        
        # Respuesta AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            response_data = {
                'success': True,
                'message': f'Producto "{nombre_producto}" eliminado exitosamente.'
            }
            logger.info(f"=== ENVIANDO RESPUESTA AJAX EXITOSA ===")
            logger.info(f"Response data: {response_data}")
            return JsonResponse(response_data)
        
        # Respuesta normal
        logger.info(f"=== ENVIANDO RESPUESTA NORMAL EXITOSA ===")
        messages.success(request, f'Producto "{nombre_producto}" eliminado exitosamente.')
        return redirect('dashboard:productos_venta_moderna')
        
    except Exception as e:
        logger.error(f"=== ERROR CAPTURADO EN EL EXCEPT PRINCIPAL ===")
        logger.error(f"Error inesperado: {str(e)}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        logger.error(f"Módulo del error: {type(e).__module__}")
        logger.error(f"Args del error: {e.args}")
        logger.error(f"Traceback completo:", exc_info=True)
        
        # Verificar si es un error de base de datos
        if 'IntegrityError' in str(type(e)):
            logger.error("ERROR DE INTEGRIDAD DE BASE DE DATOS DETECTADO")
            error_message = f'Error de integridad de base de datos: {str(e)}'
        elif 'OperationalError' in str(type(e)):
            logger.error("ERROR OPERACIONAL DE BASE DE DATOS DETECTADO")
            error_message = f'Error operacional de base de datos: {str(e)}'
        else:
            error_message = f'Error interno del servidor: {str(e)}'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            logger.error("Enviando respuesta de error vía AJAX")
            return JsonResponse({
                'success': False,
                'message': error_message
            }, status=500)
        
        logger.error("Enviando respuesta de error vía redirect")
        messages.error(request, f'Error al eliminar el producto: {str(e)}')
        return redirect('dashboard:productos_venta_moderna')

@login_required
def ver_detalle_producto(request, producto_id):
    """Vista para ver el detalle de un producto de venta"""
    producto = get_object_or_404(ProductoVenta, id=producto_id)
    recetas = ProductoReceta.objects.filter(producto=producto).select_related('receta')
    
    context = {
        'producto': producto,
        'recetas': recetas,
    }
    
    return render(request, 'dashboard/productos_venta/detalle.html', context)

@login_required
def cambiar_estado_producto(request, producto_id):
    """Vista para cambiar el estado de disponibilidad de un producto"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            producto = get_object_or_404(ProductoVenta, id=producto_id)
            producto.disponible = not producto.disponible
            producto.save()
            
            return JsonResponse({
                'success': True,
                'disponible': producto.disponible,
                'mensaje': f'Producto {producto.nombre} {"habilitado" if producto.disponible else "deshabilitado"}'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def obtener_recetas(request):
    """Vista para obtener la lista de recetas disponibles en formato JSON"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        recetas = Receta.objects.filter(activo=True).select_related('producto')
        
        data = [{
            'id': receta.id,
            'nombre': receta.producto.nombre if receta.producto else 'Sin nombre',
            'tiempo_preparacion': receta.tiempo_preparacion,
            'porciones': receta.porciones,
            'producto_id': receta.producto.id if receta.producto else None
        } for receta in recetas]
        
        return JsonResponse({'recetas': data})
    
    return JsonResponse({'error': 'Solicitud inválida'}, status=400)
