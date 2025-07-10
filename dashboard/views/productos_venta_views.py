from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, F, Value, DecimalField
from django.urls import reverse
from restaurant.models import ProductoVenta, CategoriaProducto, Receta, ProductoReceta, ProductoCategoria, RecetaInsumo
from decimal import Decimal
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@login_required
@permission_required('restaurant.view_productoventa', raise_exception=True)
def lista_productos_venta(request):
    """Vista que muestra la lista de productos de venta - TODOS los productos (activos e inactivos)"""
    try:
        # IMPORTANTE: Obtener TODOS los productos, incluyendo los inactivos
        # Usar .all() explícitamente para asegurar que no hay filtros
        productos = ProductoVenta.objects.select_related('categoria').all()
        
        # Log para debugging
        logger.info(f"=== VISTA PRODUCTOS VENTA ===")
        logger.info(f"Query SQL: {productos.query}")
        logger.info(f"Total productos encontrados: {productos.count()}")
        
        # Verificar cada producto
        for producto in productos:
            logger.info(f"Producto: {producto.nombre} - Disponible: {producto.disponible}")
        
        # Aplicar ordenamiento
        productos = productos.order_by('categoria__nombre', 'nombre')
        
        # Filtros opcionales (solo por categoría o búsqueda, NO por disponibilidad)
        categoria_id = request.GET.get('categoria')
        query = request.GET.get('q')
        
        if categoria_id:
            logger.info(f"Aplicando filtro por categoría: {categoria_id}")
            productos = productos.filter(categoria_id=categoria_id)
            
        if query:
            logger.info(f"Aplicando búsqueda: {query}")
            productos = productos.filter(
                Q(nombre__icontains=query) | 
                Q(codigo__icontains=query) | 
                Q(descripcion__icontains=query)
            )
        
        # Obtener categorías activas
        categorias = CategoriaProducto.objects.filter(activo=True).order_by('nombre')
        
        # Contar productos después de filtros opcionales
        productos_final = list(productos)  # Forzar evaluación del queryset
        total_productos = len(productos_final)
        activos = len([p for p in productos_final if p.disponible])
        inactivos = total_productos - activos
        
        logger.info(f"Resultado final:")
        logger.info(f"- Total productos: {total_productos}")
        logger.info(f"- Productos activos: {activos}")
        logger.info(f"- Productos inactivos: {inactivos}")
        
        # Log de productos finales
        for producto in productos_final:
            estado = "ACTIVO" if producto.disponible else "INACTIVO"
            logger.info(f"- {producto.nombre} ({estado})")
        
        # Preparar contexto
        context = {
            'productos': productos_final,  # Usar la lista evaluada
            'categorias': categorias,
            'categoria_seleccionada': categoria_id,
            'query': query,
            'total_activos': activos,
            'total_inactivos': inactivos,
            'total_productos': total_productos,
        }
        
        return render(request, 'dashboard/productos_venta/lista.html', context)
        
    except Exception as e:
        logger.error(f"Error en lista_productos_venta: {str(e)}")
        logger.error(f"Traceback:", exc_info=True)
        messages.error(request, f"Error al cargar la lista de productos: {str(e)}")
        return redirect('dashboard:principal')
    
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
            
            # 🆕 CREAR RECETA DIRECTA (OneToOneField) SI HAY RECETAS ASIGNADAS
            # Esto asegura que el sistema del mesero pueda encontrar la receta
            if recetas_ids:
                # Usar la primera receta como receta directa
                primera_receta = Receta.objects.get(id=recetas_ids[0])
                
                # Crear una copia de la receta directamente asociada al producto
                receta_directa = Receta.objects.create(
                    producto=producto,
                    tiempo_preparacion=primera_receta.tiempo_preparacion,
                    porciones=primera_receta.porciones,
                    instrucciones=primera_receta.instrucciones,
                    notas=primera_receta.notas,
                    activo=primera_receta.activo
                )
                
                # Copiar los insumos de la primera receta a la receta directa
                for receta_insumo in primera_receta.insumos.all():
                    RecetaInsumo.objects.create(
                        receta=receta_directa,
                        insumo=receta_insumo.insumo,
                        cantidad=receta_insumo.cantidad,
                        orden=receta_insumo.orden,
                        opcional=receta_insumo.opcional,
                        notas=receta_insumo.notas
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
def eliminar_producto_venta(request, producto_id, force=False):
    """Vista para eliminar un producto de venta"""
    # Leer el parámetro force desde el POST si viene por AJAX o formulario
    force = request.POST.get('force', 'false').lower() == 'true'
    logger = logging.getLogger(__name__)
    
    # Logs inmediatos al inicio de la función
    logger.info(f"")
    logger.info(f"🚀🚀🚀 FUNCIÓN ELIMINAR_PRODUCTO_VENTA INICIADA 🚀🚀🚀")
    logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
    logger.info(f"🔗 URL completa: {request.build_absolute_uri()}")
    logger.info(f"📡 Método HTTP: {request.method}")
    logger.info(f"👤 Usuario: {request.user.username if request.user.is_authenticated else 'Anónimo'}")
    logger.info(f"🆔 Producto ID recibido: {producto_id} (tipo: {type(producto_id)})")
    logger.info(f"📝 POST data keys: {list(request.POST.keys())}")
    logger.info(f"🔧 Content-Type: {request.content_type}")
    logger.info(f"🌐 User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')}")
    logger.info(f"📍 Referer: {request.META.get('HTTP_REFERER', 'N/A')}")
    logger.info(f"🔄 X-Requested-With: {request.headers.get('X-Requested-With', 'N/A')}")
    logger.info(f"🎯 Request Path: {request.path}")
    logger.info(f"🎯 Request Path Info: {request.path_info}")
    logger.info(f"🔐 CSRF Token presente: {'csrfmiddlewaretoken' in request.POST}")
    logger.info(f"📊 Todos los headers de la request:")
    for header_name, header_value in request.META.items():
        if header_name.startswith('HTTP_'):
            logger.info(f"     {header_name}: {header_value}")
    logger.info(f"📊 Todos los datos POST:")
    for key, value in request.POST.items():
        logger.info(f"     {key}: {value}")
    logger.info(f"💻 Remote Address: {request.META.get('REMOTE_ADDR', 'N/A')}")
    logger.info(f"💻 Server Name: {request.META.get('SERVER_NAME', 'N/A')}")
    logger.info(f"💻 Server Port: {request.META.get('SERVER_PORT', 'N/A')}")
    logger.info(f"")
    
    
    # Verificar si el producto_id viene del body en caso de que la URL no tenga el ID correcto
    if not producto_id or producto_id == '0':
        logger.warning(f"Producto ID en URL es inválido: {producto_id}")
        # Intentar obtener del body
        producto_id_body = request.POST.get('producto_id')
        if producto_id_body:
            logger.info(f"Producto ID encontrado en el body: {producto_id_body}")
            producto_id = producto_id_body
        else:
            # Intentar obtener de los headers
            producto_id_header = request.headers.get('X-Producto-ID')
            if producto_id_header:
                logger.info(f"Producto ID encontrado en los headers: {producto_id_header}")
                producto_id = producto_id_header
            else:
                logger.error(f"No se pudo encontrar un ID de producto válido ni en URL, ni en body, ni en headers")
    
    logger.info(f"Producto ID final utilizado: {producto_id}")
    
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
            return redirect('dashboard:lista_productos_venta')
        
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
            logger.error(f"❌ Método no permitido: {request.method} - SE ESPERABA POST")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Método no permitido'
                }, status=405)
            return redirect('dashboard:lista_productos_venta')
        else:
            logger.info(f"✅ Método POST confirmado - continuando...")
        
    except Exception as e:
        logger.error(f"Error en el inicio de la función: {str(e)}", exc_info=True)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error en el inicio: {str(e)}'
            }, status=500)
        messages.error(request, f'Error en el inicio: {str(e)}')
        return redirect('dashboard:lista_productos_venta')
    
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
            return redirect('dashboard:lista_productos_venta')
        
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
            return redirect('dashboard:lista_productos_venta')
        except Exception as e:
            logger.error(f"Error inesperado buscando producto: {e}", exc_info=True)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error buscando producto: {str(e)}'
                }, status=500)
            messages.error(request, f'Error buscando producto: {str(e)}')
            return redirect('dashboard:lista_productos_venta')
        
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
            
            if count_ordenes > 0 and not force:
                logger.warning(f"   El producto tiene {count_ordenes} referencias en órdenes")
                error_message = f'No se puede eliminar el producto "{nombre_producto}" porque tiene {count_ordenes} referencias en órdenes de venta. Elimine primero las órdenes relacionadas o contacte al administrador.'
                logger.error(error_message)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_message,
                        'dependencias': {
                            'tipo': 'ordenes',
                            'cantidad': count_ordenes,
                            'producto_id': producto.id,
                            'producto_nombre': nombre_producto
                        },
                        'requiere_forzado': True
                    }, status=400)
                messages.error(request, error_message)
                return redirect('dashboard:lista_productos_venta')
            
            # Verificar DetalleVenta
            detalles_venta = DetalleVenta.objects.filter(producto=producto)
            count_ventas = detalles_venta.count()
            logger.info(f"   Encontradas {count_ventas} referencias en DetalleVenta")
            
            if count_ventas > 0 and not force:
                logger.warning(f"   El producto tiene {count_ventas} referencias en ventas")
                error_message = f'No se puede eliminar el producto "{nombre_producto}" porque tiene {count_ventas} referencias en ventas realizadas. No es posible eliminar productos que ya han sido vendidos por razones de auditoría.'
                logger.error(error_message)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_message,
                        'dependencias': {
                            'tipo': 'ventas',
                            'cantidad': count_ventas,
                            'producto_id': producto.id,
                            'producto_nombre': nombre_producto
                        },
                        'requiere_forzado': True
                    }, status=400)
                messages.error(request, error_message)
                return redirect('dashboard:lista_productos_venta')
            
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
                            if not force:
                                # Si no es forzado, bloquear y avisar
                                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                                    return JsonResponse({
                                        'success': False,
                                        'message': f'El producto tiene {count} referencias en una tabla huérfana ({tabla}). Contacte al administrador para limpiar estos datos antes de eliminar el producto.',
                                        'dependencias': {
                                            'tipo': 'huerfana',
                                            'tabla': tabla,
                                            'cantidad': count,
                                            'producto_id': producto.id,
                                            'producto_nombre': nombre_producto
                                        },
                                        'requiere_forzado': True
                                    }, status=400)
                                messages.error(request, f'El producto tiene referencias en una tabla huérfana ({tabla}). Contacte al administrador.')
                                return redirect('dashboard:lista_productos_venta')
                            else:
                                # Si es forzado, eliminar los registros huérfanos
                                logger.warning(f"   Eliminando {count} registros huérfanos en {tabla} (FORZADO)")
                                cursor.execute(f'DELETE FROM {tabla} WHERE producto_id = %s', [producto.id])
                                logger.info(f"   Eliminados {count} registros huérfanos en {tabla}")
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
            logger.info(f"🗑️ A punto de ejecutar producto.delete()...")
            producto.delete()
            logger.info(f"✅ Producto eliminado exitosamente: {nombre_producto}")
            logger.info(f"🎉 ELIMINACIÓN COMPLETADA CON ÉXITO")
            
        except Exception as e:
            logger.error(f"💥 Error durante el proceso de eliminación: {str(e)}", exc_info=True)
            logger.error(f"Tipo de error: {type(e).__name__}")
            logger.error(f"Args del error: {e.args}")
            raise e  # Re-lanzar la exception para que sea capturada por el except principal
        
        # Respuesta AJAX
        logger.info(f"🔍 Verificando tipo de respuesta...")
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        logger.info(f"📡 Es petición AJAX: {is_ajax}")
        
        if is_ajax:
            response_data = {
                'success': True,
                'message': f'Producto "{nombre_producto}" eliminado exitosamente.'
            }
            logger.info(f"=== ENVIANDO RESPUESTA AJAX EXITOSA ===")
            logger.info(f"📤 Response data: {response_data}")
            ajax_response = JsonResponse(response_data)
            logger.info(f"📦 Respuesta AJAX creada exitosamente")
            return ajax_response
        
        # Respuesta normal
        logger.info(f"=== ENVIANDO RESPUESTA NORMAL EXITOSA ===")
        logger.info(f"📨 Agregando mensaje de éxito...")
        messages.success(request, f'Producto "{nombre_producto}" eliminado exitosamente.')
        logger.info(f"🔄 Ejecutando redirect a lista_productos_venta...")
        redirect_response = redirect('dashboard:lista_productos_venta')
        logger.info(f"📍 Redirect creado exitosamente")
        logger.info(f"🎊 FUNCIÓN TERMINA CON ÉXITO - ENVIANDO RESPUESTA NORMAL")
        return redirect_response
        
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
        return redirect('dashboard:lista_productos_venta')

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
    logger = logging.getLogger(__name__)
    
    logger.info(f"========== CAMBIO DE ESTADO INICIADO ==========")
    logger.info(f"Producto ID recibido: {producto_id} (tipo: {type(producto_id)})")
    logger.info(f"Método: {request.method}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Content-Type: {request.headers.get('Content-Type')}")
    logger.info(f"X-Requested-With: {request.headers.get('X-Requested-With')}")
    logger.info(f"POST data: {dict(request.POST)}")
    logger.info(f"FILES data: {dict(request.FILES)}")
    logger.info(f"Query params: {dict(request.GET)}")
    
    # Intentar leer el body como JSON o FormData
    try:
        body_unicode = request.body.decode('utf-8')
        logger.info(f"Body recibido (longitud): {len(body_unicode)}")
        if body_unicode:
            logger.info(f"Body recibido (contenido): {body_unicode}")
            try:
                body_data = json.loads(body_unicode)
                logger.info(f"Body parseado como JSON: {body_data}")
            except json.JSONDecodeError as e:
                logger.warning(f"El body no es un JSON válido: {e}")
                # Si no es JSON, podría ser FormData
                if 'Content-Type' in request.headers and 'multipart/form-data' in request.headers.get('Content-Type'):
                    logger.info(f"Detectado FormData en la solicitud")
    except Exception as e:
        logger.warning(f"Error al procesar el body: {e}")
    
    if request.method == 'POST':
        try:
            logger.info(f"Obteniendo producto con ID: {producto_id}")
            # Obtener el producto
            producto = get_object_or_404(ProductoVenta, id=producto_id)
            logger.info(f"Producto encontrado: {producto.nombre}, estado actual disponible={producto.disponible}")
            
            # Determinar el nuevo estado
            nuevo_estado = None
            
            # 1. Primero intentar desde POST directo (formulario)
            if 'disponible' in request.POST:
                disponible_post = request.POST.get('disponible')
                logger.info(f"Disponible desde POST: {disponible_post} (tipo: {type(disponible_post)})")
                
                # Convertir string a boolean
                if disponible_post.lower() in ['true', '1', 't', 'y', 'yes', 'on']:
                    nuevo_estado = True
                    logger.info(f"Valor POST convertido a True")
                elif disponible_post.lower() in ['false', '0', 'f', 'n', 'no', 'off']:
                    nuevo_estado = False
                    logger.info(f"Valor POST convertido a False")
                else:
                    logger.warning(f"Valor de disponible no reconocido: {disponible_post}")
            else:
                logger.info("No se encontró 'disponible' en el POST data")
            
            # 2. Intentar desde JSON si no se encontró en POST
            if nuevo_estado is None and request.headers.get('Content-Type') == 'application/json':
                try:
                    data = json.loads(request.body)
                    logger.info(f"Datos JSON recibidos: {data}")
                    
                    if 'disponible' in data:
                        if isinstance(data['disponible'], bool):
                            nuevo_estado = data['disponible']
                            logger.info(f"Disponible desde JSON (bool): {nuevo_estado}")
                        else:
                            # Convertir a booleano si viene como string
                            disponible_val = str(data['disponible']).lower()
                            logger.info(f"Disponible desde JSON (string): {disponible_val}")
                            
                            if disponible_val in ['true', '1', 't', 'y', 'yes', 'on']:
                                nuevo_estado = True
                                logger.info(f"Valor JSON convertido a True")
                            elif disponible_val in ['false', '0', 'f', 'n', 'no', 'off']:
                                nuevo_estado = False
                                logger.info(f"Valor JSON convertido a False")
                            else:
                                logger.warning(f"Valor JSON no reconocido: {disponible_val}")
                    else:
                        logger.info("No se encontró 'disponible' en el JSON")
                except Exception as e:
                    logger.warning(f"Error al procesar JSON: {e}")
            
            # 3. Si no se encontró un valor explícito, invertir el estado actual
            if nuevo_estado is None:
                nuevo_estado = not producto.disponible
                logger.info(f"No se encontró un valor explícito. Invirtiendo estado actual: {nuevo_estado}")
            
            # Actualizar el producto
            logger.info(f"Estado final a aplicar: disponible={nuevo_estado}")
            producto.disponible = nuevo_estado
            producto.save()
            logger.info(f"Producto guardado. Nuevo estado: disponible={producto.disponible}")
            
            # Preparar respuesta
            response_data = {
                'success': True,
                'disponible': producto.disponible,
                'mensaje': f'Producto {producto.nombre} {"habilitado" if producto.disponible else "deshabilitado"}'
            }
            logger.info(f"Respuesta preparada: {response_data}")
            
            # Si es una petición AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                logger.info(f"Enviando respuesta JSON")
                response = JsonResponse(response_data)
                logger.info(f"Respuesta JSON creada: {response.status_code}")
                return response
            
            # Si es un formulario normal, redirigir a la lista
            logger.info(f"Enviando redirección con mensaje de éxito")
            messages.success(request, response_data['mensaje'])
            return redirect('dashboard:lista_productos_venta')
            
        except Exception as e:
            logger.error(f"Error al cambiar estado: {str(e)}", exc_info=True)
            
            error_data = {
                'success': False, 
                'error': str(e),
                'message': f'Error al cambiar estado: {str(e)}'
            }
            logger.error(f"Datos de error: {error_data}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                logger.info(f"Enviando respuesta JSON de error")
                return JsonResponse(error_data, status=500)
            
            logger.info(f"Enviando redirección con mensaje de error")
            messages.error(request, error_data['message'])
            return redirect('dashboard:lista_productos_venta')
    
    logger.warning("Método no permitido")
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    messages.error(request, 'Método no permitido')
    return redirect('dashboard:lista_productos_venta')

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

@login_required
@permission_required('restaurant.change_productoventa', raise_exception=True)
def desactivar_producto_venta(request, producto_id):
    """Vista para desactivar un producto de venta sin eliminarlo"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"=== DESACTIVACIÓN INICIADA ===")
        logger.info(f"Producto ID recibido: {producto_id}")
        logger.info(f"Método: {request.method}")
        logger.info(f"Headers: Content-Type={request.headers.get('Content-Type')}, X-Requested-With={request.headers.get('X-Requested-With')}")
        
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
            return redirect('dashboard:lista_productos_venta')
        
        # Verificar que sea POST
        if request.method != 'POST':
            logger.error(f"Método no permitido: {request.method}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Método no permitido'
                }, status=405)
            return redirect('dashboard:lista_productos_venta')
        
        # Buscar el producto
        try:
            producto = ProductoVenta.objects.get(id=producto_id_int)
            logger.info(f"Producto encontrado: {producto.nombre} (ID: {producto.id})")
            
            # Obtener datos del JSON si está disponible
            if request.headers.get('Content-Type') == 'application/json':
                try:
                    data = json.loads(request.body)
                    logger.info(f"Datos JSON recibidos: {data}")
                    # Si se proporcionó disponible en el JSON, úsalo
                    if 'disponible' in data:
                        disponible = data.get('disponible')
                        logger.info(f"Valor disponible del JSON: {disponible}")
                        producto.disponible = disponible
                    else:
                        # Si no hay campo disponible, simplemente desactivar
                        logger.info("No se proporcionó campo disponible en el JSON")
                        producto.disponible = False
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON inválido recibido: {e}")
                    producto.disponible = False
            else:
                # Si no hay JSON, simplemente desactivar
                logger.info("No se recibió Content-Type application/json")
                producto.disponible = False
                
            producto.save()
            logger.info(f"Producto {'activado' if producto.disponible else 'desactivado'} exitosamente: {producto.nombre}")
        except ProductoVenta.DoesNotExist:
            logger.error(f"Producto no existe con ID {producto_id_int}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Producto no encontrado'
                }, status=404)
            messages.error(request, 'Producto no encontrado')
            return redirect('dashboard:lista_productos_venta')
            
        
        # Respuesta AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            logger.info(f"Enviando respuesta AJAX: success=true, disponible={producto.disponible}")
            return JsonResponse({
                'success': True,
                'message': f'Producto "{producto.nombre}" {"activado" if producto.disponible else "desactivado"} exitosamente.',
                'disponible': producto.disponible,
                'mensaje': f'Producto {producto.nombre} {"habilitado" if producto.disponible else "deshabilitado"}'
            })
        
        # Respuesta normal
        logger.info(f"Enviando respuesta normal: redirect to lista_productos_venta")
        messages.success(request, f'Producto "{producto.nombre}" {"activado" if producto.disponible else "desactivado"} exitosamente.')
        return redirect('dashboard:lista_productos_venta')
        
    except Exception as e:
        logger.error(f"Error durante la desactivación: {str(e)}", exc_info=True)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error al desactivar el producto: {str(e)}'
            }, status=500)
        messages.error(request, f'Error al desactivar el producto: {str(e)}')
        return redirect('dashboard:lista_productos_venta')


@login_required
def diagnostico_view(request):
    """
    Vista para página de diagnóstico de JavaScript
    """
    print("DEBUG: Cargando página de diagnóstico de JavaScript")
    logger.info("Cargando página de diagnóstico de JavaScript")
    
    return render(request, 'dashboard/productos_venta/diagnostico.html', {
        'sidebar_active': 'productos_venta',
    })
