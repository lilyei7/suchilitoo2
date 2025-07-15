from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
import decimal
import traceback
from django.db import connection
from restaurant.models import Receta, CategoriaProducto, ProductoVenta, RecetaInsumo, Insumo
from django.db.models import Avg, Count, Sum
from decimal import Decimal
import logging
from dashboard.utils.permissions import require_module_access

logger = logging.getLogger(__name__)

@login_required
@require_module_access('recetas')
def recetas_view(request):
    """Vista principal para mostrar las recetas"""
    try:
        # Verificar si la petición es AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'
        logger.info(f"Petición recetas_view con AJAX={is_ajax}")
        
        # Actualizar nombres de recetas antiguas si tienen el valor por defecto
        for receta in Receta.objects.filter(nombre="Receta").all():
            # Asignar nombres personalizados basados en el ID
            if receta.id == 1:
                receta.nombre = "Te 1LT Envasado"
            elif receta.id == 2:
                receta.nombre = "Favorito Especial"
            # Guardar los cambios en la base de datos
            receta.save()
            logger.info(f"Actualizado nombre de receta ID {receta.id} a '{receta.nombre}'")
        
        # Obtener todas las recetas activas después de actualizar nombres
        recetas = Receta.objects.filter(activo=True)
        
        # Calcular estadísticas básicas que no dependen de decimales
        total_recetas = recetas.count()
        tiempo_promedio = recetas.aggregate(Avg('tiempo_preparacion'))['tiempo_preparacion__avg'] or 0
        
        # Preparar listado de recetas para el template
        recetas_data = []
        costo_total_todas = 0.0
        
        # Iterar por recetas de forma segura usando IDs para evitar errores en cascada
        for receta_id in recetas.values_list('id', flat=True):
            try:
                # Obtener la receta individualmente para evitar problemas con el queryset
                receta = Receta.objects.get(id=receta_id)
                
                # Calcular costo total de la receta manualmente y de forma segura
                costo_total = 0.0
                num_ingredientes = 0
                
                try:
                    # Obtener ingredientes sin join para mayor seguridad
                    ingredientes = RecetaInsumo.objects.filter(receta_id=receta_id)
                    
                    if not ingredientes.exists():
                        logger.info(f"La receta {receta_id} no tiene ingredientes")
                    
                    for ingrediente in ingredientes:
                        try:
                            # Verificar que los datos sean válidos antes de calcular
                            if not ingrediente.insumo_id:
                                logger.warning(f"Ingrediente de receta {receta_id} sin insumo asociado")
                                continue
                                
                            # Obtener insumo de forma segura
                            insumo = Insumo.objects.filter(id=ingrediente.insumo_id).first()
                            if not insumo:
                                logger.warning(f"No se encontró el insumo {ingrediente.insumo_id} para la receta {receta_id}")
                                continue
                                
                            # Convertir a float de forma segura
                            try:
                                precio = float(insumo.precio_unitario or 0)
                            except (ValueError, TypeError, decimal.InvalidOperation):
                                precio = 0.0
                                
                            try:
                                cantidad = float(ingrediente.cantidad or 0)
                            except (ValueError, TypeError, decimal.InvalidOperation):
                                cantidad = 0.0
                                
                            # Calcular costo de este ingrediente
                            costo_ingrediente = precio * cantidad
                            costo_total += costo_ingrediente
                            num_ingredientes += 1
                        except Exception as e:
                            logger.error(f"Error procesando ingrediente para receta {receta_id}: {e}")
                            continue
                except Exception as e:
                    logger.error(f"Error obteniendo ingredientes para receta {receta_id}: {e}")
                
                # Añadir al costo total acumulado
                costo_total_todas += costo_total
                
                # Obtener el precio de venta con manejo seguro de errores
                precio_venta = 0.0
                nombre_producto = None
                
                try:
                    # Usar un cursor directo para evitar usar el ORM y problemas con decimales
                    cursor = connection.cursor()
                    
                    # Primero intentar obtener usando la relación en receta
                    cursor.execute(
                        "SELECT p.id, p.nombre FROM restaurant_productoventa p "
                        "JOIN restaurant_receta r ON p.id = r.producto_id "
                        "WHERE r.id = %s LIMIT 1", 
                        [receta.id]
                    )
                    row = cursor.fetchone()
                    if row:
                        producto_id = row[0]
                        nombre_producto = row[1]
                        
                        # Obtener el precio directamente
                        cursor.execute(
                            "SELECT CAST(precio as REAL) FROM restaurant_productoventa WHERE id = %s",
                            [producto_id]
                        )
                        precio_row = cursor.fetchone()
                        if precio_row and precio_row[0] is not None:
                            precio_venta = float(precio_row[0])
                    
                    # Si no se encuentra, intentar por el campo directo
                    elif hasattr(receta, 'producto_id') and receta.producto_id:
                        cursor.execute(
                            "SELECT id, nombre, CAST(precio as REAL) FROM restaurant_productoventa WHERE id = %s LIMIT 1",
                            [receta.producto_id]
                        )
                        row = cursor.fetchone()
                        if row:
                            producto_id = row[0]
                            nombre_producto = row[1]
                            if row[2] is not None:
                                precio_venta = float(row[2])
                    
                    cursor.close()
                except Exception as e:
                    logger.error(f"Error obteniendo precio venta para receta {receta_id}: {e}")
                
                # Usar el nombre real de la receta si existe
                nombre = receta.nombre if receta.nombre else (nombre_producto or f"Receta {receta_id}")
                categoria = 'Sin categoría'
                try:
                    # Intentar obtener la categoría directamente con SQL
                    cursor = connection.cursor()
                    cursor.execute(
                        "SELECT c.nombre FROM restaurant_categoriaproducto c "
                        "JOIN restaurant_productoventa p ON c.id = p.categoria_id "
                        "JOIN restaurant_receta r ON p.id = r.producto_id "
                        "WHERE r.id = %s LIMIT 1",
                        [receta_id]
                    )
                    cat_row = cursor.fetchone()
                    if cat_row and cat_row[0]:
                        categoria = cat_row[0]
                    cursor.close()
                except Exception as e:
                    logger.error(f"Error obteniendo categoría para receta {receta_id}: {e}")
                
                # Si no hay producto asociado, marcar como disponible por defecto
                disponible = True
                try:
                    cursor = connection.cursor()
                    cursor.execute(
                        "SELECT disponible FROM restaurant_productoventa p "
                        "JOIN restaurant_receta r ON p.id = r.producto_id "
                        "WHERE r.id = %s LIMIT 1",
                        [receta_id]
                    )
                    disp_row = cursor.fetchone()
                    if disp_row:
                        disponible = bool(disp_row[0])
                    cursor.close()
                except Exception as e:
                    logger.error(f"Error obteniendo disponibilidad para receta {receta_id}: {e}")
                
                # Crear el objeto de datos para esta receta
                receta_data = {
                    'id': receta_id,
                    'nombre': nombre,
                    'categoria': categoria,
                    'tiempo_preparacion': int(receta.tiempo_preparacion or 0),
                    'porciones': int(receta.porciones or 1),
                    'costo_total': round(costo_total, 2),  # Redondear para evitar errores de visualización
                    'precio_venta': round(precio_venta, 2),  # Redondear para evitar errores de visualización
                    'num_ingredientes': num_ingredientes,
                    'disponible': disponible                }
                
                recetas_data.append(receta_data)
                logger.info(f"Procesada receta {receta_id} con éxito")
            except Exception as e:
                logger.error(f"Error procesando receta {receta_id}: {e}")
                traceback.print_exc()
                # Continuar con la siguiente receta, no detener el proceso
                continue
        
        # Calcular costo promedio, evitando división por cero
        costo_promedio = 0.0
        if total_recetas > 0:
            costo_promedio = costo_total_todas / total_recetas
        
        # Crear el contexto para el template
        context = {
            'total_recetas': total_recetas,
            'costo_promedio': round(costo_promedio, 2),
            'tiempo_promedio': int(tiempo_promedio),
            'recetas': recetas_data
        }
        
        # Importar y agregar contexto del sidebar
        from dashboard.views import get_sidebar_context
        context.update(get_sidebar_context('recetas'))
        
        logger.info(f"Total de recetas encontradas: {total_recetas}")
        
        if is_ajax:
            logger.debug("Respuesta AJAX para lista de recetas")
            return render(request, 'dashboard/recetas.html', context)
        else:
            logger.debug("Respuesta normal para lista de recetas")
            return render(request, 'dashboard/recetas.html', context)
    except Exception as e:
        logger.error(f"Error en recetas_view: {e}")
        traceback.print_exc()
        # Importar y agregar contexto del sidebar para el caso de error también
        from dashboard.views import get_sidebar_context
        error_context = {
            'total_recetas': 0,
            'costo_promedio': 0,
            'tiempo_promedio': 0,
            'recetas': []
        }
        error_context.update(get_sidebar_context('recetas'))
        return render(request, 'dashboard/recetas.html', error_context)

@login_required
def obtener_categorias_recetas(request):
    """API para obtener categorías de recetas"""
    try:
        # Obtener categorías de productos que pueden ser usados como recetas
        categorias = CategoriaProducto.objects.filter(activo=True).order_by('nombre')
        
        categorias_data = []
        for categoria in categorias:
            categorias_data.append({
                'id': categoria.id,
                'codigo': f"CAT{categoria.id:03d}",  # Generar código si no existe
                'nombre': categoria.nombre,
                'descripcion': categoria.descripcion or '',
                'activa': categoria.activo
            })
        
        return JsonResponse({
            'success': True,
            'categorias': categorias_data,
            'message': 'Categorías cargadas correctamente'
        })
    except Exception as e:
        logger.error(f"Error en obtener_categorias_recetas: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al cargar categorías: {str(e)}'
        })

@login_required
@require_POST
def crear_categoria_receta(request):
    """Crear nueva categoría de receta"""
    try:
        data = request.POST
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        
        if not nombre:
            return JsonResponse({
                'success': False,
                'message': 'El nombre de la categoría es obligatorio'
            })
        
        # Verificar si ya existe una categoría con ese nombre
        if CategoriaProducto.objects.filter(nombre=nombre).exists():
            return JsonResponse({
                'success': False,
                'message': f'Ya existe una categoría con el nombre "{nombre}"'
            })
        
        # Crear la nueva categoría
        categoria = CategoriaProducto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            activo=True
        )
        
        return JsonResponse({
            'success': True,
            'categoria': {
                'id': categoria.id,
                'nombre': categoria.nombre,
                'descripcion': categoria.descripcion,
                'codigo': f"CAT{categoria.id:03d}"
            },
            'message': 'Categoría creada correctamente'
        })
    except Exception as e:
        logger.error(f"Error al crear categoría: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al crear categoría: {str(e)}'
        })

@login_required
@require_module_access('recetas')
@require_POST
def crear_receta(request):
    """Crear nueva receta"""
    try:
        data = request.POST
        logger.info(f"Datos recibidos para crear receta: {dict(data)}")
        
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        categoria_id = data.get('categoria_id')
        tiempo_preparacion = data.get('tiempo_preparacion', 0)
        porciones = data.get('porciones', 1)
        instrucciones = data.get('instrucciones', '').strip()
        precio_venta = data.get('precio_venta', 0)
        costo_total = data.get('costo_total', 0)
        
        # Validaciones básicas
        if not nombre:
            return JsonResponse({
                'success': False,
                'message': 'El nombre de la receta es obligatorio'
            })
        
        if not categoria_id:
            return JsonResponse({
                'success': False,
                'message': 'Debe seleccionar una categoría'
            })
        
        # Verificar que la categoría exista
        try:
            categoria = CategoriaProducto.objects.get(id=categoria_id)
        except CategoriaProducto.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'La categoría seleccionada no existe'
            })
        
        # Verificar ingredientes
        insumo_ids = request.POST.getlist('ingrediente_insumo[]')
        cantidades = request.POST.getlist('ingrediente_cantidad[]')
        
        if not insumo_ids or not cantidades or len(insumo_ids) == 0:
            return JsonResponse({
                'success': False,
                'message': 'Debe agregar al menos un ingrediente'
            })
        
        # Procesar los ingredientes y validar que los insumos existan
        ingredientes_validos = []
        for i, insumo_id in enumerate(insumo_ids):
            if insumo_id and i < len(cantidades) and cantidades[i]:
                try:
                    insumo = Insumo.objects.get(id=insumo_id)
                    cantidad = float(cantidades[i])
                    
                    if cantidad <= 0:
                        return JsonResponse({
                            'success': False,
                            'message': f'La cantidad del ingrediente {insumo.nombre} debe ser mayor a cero'
                        })
                    
                    ingredientes_validos.append({
                        'insumo': insumo,
                        'cantidad': cantidad,
                        'index': i
                    })
                except Insumo.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': f'El insumo ID {insumo_id} no existe'
                    })
                except (ValueError, TypeError):
                    return JsonResponse({
                        'success': False,
                        'message': f'La cantidad del ingrediente {i+1} no es válida'
                    })
            
        if len(ingredientes_validos) == 0:
            return JsonResponse({
                'success': False,
                'message': 'No hay ingredientes válidos para crear la receta'
            })
        
        # Usar una transacción para asegurar que todo se guarde correctamente
        from django.db import transaction
        import time
        import random
        
        with transaction.atomic():
            # Crear el producto con código único basado en timestamp y número aleatorio
            timestamp = int(time.time())
            random_suffix = random.randint(100, 999)
            codigo = f"REC{timestamp}{random_suffix}"
            
            # Verificar que el código no exista ya (aunque es muy improbable)
            while ProductoVenta.objects.filter(codigo=codigo).exists():
                random_suffix = random.randint(100, 999)
                codigo = f"REC{timestamp}{random_suffix}"
            
            # logger.info(f"Creando producto con código único: {codigo}")
            # producto = ProductoVenta.objects.create(
            #     codigo=codigo,
            #     nombre=nombre,
            #     descripcion=descripcion,
            #     categoria=categoria,
            #     precio=Decimal(str(precio_venta)),
            #     costo=Decimal(str(costo_total)),
            #     tipo='plato',
            #     disponible=True
            # )
            # logger.info(f"Producto creado: {producto}")
            # except Exception as e:
            #     logger.error(f"Error al crear producto: {e}")
            #     # Dar un mensaje más amigable para el error de código duplicado
            #     if "UNIQUE constraint failed" in str(e) and "codigo" in str(e):
            #         return JsonResponse({
            #             'success': False,
            #             'message': 'Error: Ya existe un producto con el mismo código. Intente nuevamente.'
            #         })
            #     return JsonResponse({
            #         'success': False,
            #         'message': f'Error al crear el producto: {str(e)}'
            #     })
            
            # Crear la receta
            try:
                receta = Receta.objects.create(
                    nombre=nombre,
                    tiempo_preparacion=int(float(tiempo_preparacion)) if tiempo_preparacion else 0,
                    porciones=int(float(porciones)) if porciones else 1,
                    instrucciones=instrucciones,
                    activo=True
                )
                logger.info(f"Receta creada: {receta}")
            except Exception as e:
                logger.error(f"Error al crear receta: {e}")
                return JsonResponse({
                    'success': False,
                    'message': f'Error al crear la receta: {str(e)}'
                })
            
            # Procesar ingredientes
            opcionales = request.POST.getlist('ingrediente_opcional[]')
            notas_list = request.POST.getlist('ingrediente_notas[]')
            
            logger.info(f"Procesando {len(ingredientes_validos)} ingredientes")
            
            for item in ingredientes_validos:
                insumo = item['insumo']
                cantidad = item['cantidad']
                index = item['index']
                
                try:
                    es_opcional = index < len(opcionales) and opcionales[index] == 'on'
                    notas = notas_list[index] if index < len(notas_list) else ''
                    
                    RecetaInsumo.objects.create(
                        receta=receta,
                        insumo=insumo,
                        cantidad=Decimal(str(cantidad)),
                        opcional=es_opcional,
                        notas=notas,
                        orden=index+1
                    )
                    logger.info(f"Ingrediente {index+1} añadido: {insumo.nombre}, cantidad: {cantidad}")
                except Exception as e:
                    logger.error(f"Error al procesar ingrediente {index}: {e}")
                    # La transacción manejará el rollback si falla
                    return JsonResponse({
                        'success': False,
                        'message': f'Error al añadir el ingrediente {insumo.nombre}: {str(e)}'
                    })
            
            # Todo se guardó correctamente
            return JsonResponse({
                'success': True,
                'receta_id': receta.id,
                'receta_nombre': nombre,
                'message': f'Receta "{nombre}" creada correctamente'
            })
    except Exception as e:
        logger.error(f"Error al crear receta: {e}")
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error al crear receta: {str(e)}'
        })

@login_required
@login_required
@require_module_access('recetas')
def detalle_receta(request, receta_id):
    """Obtener detalle de una receta"""
    logger.info(f"Obteniendo detalle de receta {receta_id}")
    
    try:
        # Obtener la receta directamente de la base de datos sin relacionados para evitar errores de conversión
        receta = None
        try:
            receta = Receta.objects.get(id=receta_id)
        except Receta.DoesNotExist:
            logger.error(f"Receta no encontrada: {receta_id}")
            return JsonResponse({
                'success': False,
                'message': 'Receta no encontrada'
            })
        
        # Obtener ingredientes de forma segura
        ingredientes = []
        try:
            ingredientes = RecetaInsumo.objects.filter(receta_id=receta_id).select_related('insumo', 'insumo__unidad_medida')
        except Exception as e:
            logger.error(f"Error al obtener ingredientes: {e}")
            # Continuar sin ingredientes
        
        # Calcular el costo total de la receta
        costo_total = 0.0
        try:
            # Intentar obtener el producto directamente con raw SQL para evitar problemas de conversión
            producto_data = None
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, nombre, descripcion, precio, costo, categoria_id FROM restaurant_productoventa WHERE id = (SELECT producto_id FROM restaurant_receta WHERE id = %s)",
                    [receta_id]
                )
                row = cursor.fetchone()
                if row:
                    producto_data = {
                        'id': row[0],
                        'nombre': row[1],
                        'descripcion': row[2],
                        'precio': float(row[3]) if row[3] is not None else 0.0,
                        'costo': float(row[4]) if row[4] is not None else 0.0,
                        'categoria_id': row[5]
                    }
            
            # Si tenemos datos del producto, usar el costo almacenado
            if producto_data and producto_data['costo'] > 0:
                costo_total = producto_data['costo']
            else:
                # Calcular desde los ingredientes
                for ingrediente in ingredientes:
                    try:
                        precio_unitario = float(ingrediente.insumo.precio_unitario) if ingrediente.insumo.precio_unitario is not None else 0.0
                        cantidad = float(ingrediente.cantidad) if ingrediente.cantidad is not None else 0.0
                        costo_total += precio_unitario * cantidad
                    except Exception as e:
                        logger.error(f"Error calculando costo de ingrediente {ingrediente.id}: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error calculando costo total: {e}")
            # Continuar con costo_total = 0
        
        # Intentar actualizar el costo en el producto si existe
        if producto_data:
            try:
                # Solo actualizar si hay diferencia significativa
                if abs(producto_data['costo'] - costo_total) > 0.01:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "UPDATE restaurant_productoventa SET costo = %s WHERE id = %s",
                            [costo_total, producto_data['id']]
                        )
                    logger.info(f"Costo de producto actualizado a {costo_total}")
            except Exception as e:
                logger.error(f"Error actualizando costo del producto: {e}")
                # Continuar sin actualizar
        
        # Preparar datos para la respuesta
        try:
            # Obtener datos de categoría si existe
            categoria_data = {'id': None, 'nombre': 'Sin categoría'}
            if producto_data and producto_data['categoria_id']:
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "SELECT id, nombre FROM restaurant_categoriaproducto WHERE id = %s",
                            [producto_data['categoria_id']]
                        )
                        cat_row = cursor.fetchone()
                        if cat_row:
                            categoria_data = {
                                'id': cat_row[0],
                                'nombre': cat_row[1]
                            }
                except Exception as e:
                    logger.error(f"Error obteniendo categoría: {e}")
            
            # Preparar datos de la receta
            # Usar el nombre real de la receta si existe, o nombre del producto asociado
            nombre_receta = receta.nombre
            if not nombre_receta or nombre_receta == f"Receta {receta.id}":
                if producto_data:
                    nombre_receta = producto_data['nombre']
                else:
                    nombre_receta = f"Receta {receta.id}"

            if not producto_data:
                receta_data = {
                    'id': receta.id,
                    'nombre': nombre_receta,
                    'descripcion': "Esta receta no tiene un producto asociado. Por favor, edítela para corregir este problema.",
                    'categoria': categoria_data,
                    'tiempo_preparacion': receta.tiempo_preparacion or 0,
                    'porciones': receta.porciones or 1,
                    'costo_total': costo_total,
                    'precio_venta': 0,
                    'instrucciones': receta.instrucciones or ''
                }
            else:
                receta_data = {
                    'id': receta.id,
                    'nombre': nombre_receta,
                    'descripcion': producto_data['descripcion'] or '',
                    'categoria': categoria_data,
                    'tiempo_preparacion': receta.tiempo_preparacion or 0,
                    'porciones': receta.porciones or 1,
                    'costo_total': costo_total,
                    'precio_venta': producto_data['precio'],
                    'instrucciones': receta.instrucciones or ''
                }
                
            logger.info(f"Datos de receta {receta.id} preparados correctamente: {receta_data['nombre']}")
            
        except Exception as e:
            logger.error(f"Error preparando datos de receta {receta.id}: {e}")
            import traceback
            traceback.print_exc()
            receta_data = {
                'id': receta.id,
                'nombre': f"Receta {receta.id}",
                'descripcion': "Error al cargar los datos completos de la receta",
                'categoria': {'id': None, 'nombre': 'Sin categoría'},
                'tiempo_preparacion': receta.tiempo_preparacion or 0,
                'porciones': receta.porciones or 1,
                'costo_total': costo_total,
                'precio_venta': 0,
                'instrucciones': receta.instrucciones or ''
            }
        
        # Preparar datos de ingredientes
        ingredientes_data = []
        for ingrediente in ingredientes:
            try:
                # Verificar si el insumo existe
                if not ingrediente.insumo:
                    logger.warning(f"Ingrediente {ingrediente.id} no tiene insumo asociado")
                    continue
                
                # Obtener datos del insumo de forma segura
                insumo = ingrediente.insumo
                
                # Calcular costo individual del ingrediente de manera segura
                try:
                    precio_unitario = float(insumo.precio_unitario) if insumo.precio_unitario is not None else 0.0
                except (ValueError, TypeError, decimal.InvalidOperation):
                    precio_unitario = 0.0
                
                try:
                    cantidad = float(ingrediente.cantidad) if ingrediente.cantidad is not None else 0.0
                except (ValueError, TypeError, decimal.InvalidOperation):
                    cantidad = 0.0
                
                costo_ingrediente = precio_unitario * cantidad
                
                # Obtener datos de unidad de medida
                unidad_id = None
                unidad_nombre = 'Unidad'
                unidad_abrev = 'Un'
                
                try:
                    if insumo.unidad_medida:
                        unidad_id = insumo.unidad_medida.id
                        unidad_nombre = insumo.unidad_medida.nombre
                        unidad_abrev = insumo.unidad_medida.abreviacion
                except Exception as e:
                    logger.error(f"Error obteniendo unidad de medida: {e}")
                
                # Preparar datos del ingrediente
                ingrediente_data = {
                    'id': ingrediente.id,
                    'insumo': {
                        'id': insumo.id,
                        'nombre': insumo.nombre or 'Insumo sin nombre',
                        'tipo': insumo.tipo or 'basico',
                        'unidad_medida': {
                            'id': unidad_id,
                            'nombre': unidad_nombre,
                        },
                        'unidad_abrev': unidad_abrev,
                        'precio_unitario': precio_unitario
                    },
                    'cantidad': cantidad,
                    'costo_unitario': precio_unitario,
                    'costo_total': costo_ingrediente,
                    'opcional': ingrediente.opcional or False,
                    'notas': ingrediente.notas or ''
                }
                
                ingredientes_data.append(ingrediente_data)
            except Exception as e:
                logger.error(f"Error procesando ingrediente {getattr(ingrediente, 'id', 'desconocido')}: {e}")
                continue
        
        logger.info(f"Total de ingredientes: {len(ingredientes_data)}")
        
        response_data = {
            'success': True,
            'receta': receta_data,
            'ingredientes': ingredientes_data
        }
        
        return JsonResponse(response_data)
    except Exception as e:
        logger.error(f"Error al obtener receta {receta_id}: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener receta: {str(e)}'
        })

@login_required
@login_required
@require_module_access('recetas')
@require_POST
def editar_receta(request, receta_id):
    """Editar receta existente"""
    logger.info(f"Editando receta {receta_id}")
    
    try:
        # Obtener la receta directamente sin relaciones
        try:
            receta = Receta.objects.get(id=receta_id)
        except Receta.DoesNotExist:
            logger.error(f"Receta {receta_id} no encontrada")
            return JsonResponse({
                'success': False,
                'message': 'Receta no encontrada'
            })
        
        # Obtener producto relacionado de forma directa usando SQL
        producto_id = None
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT producto_id FROM restaurant_receta WHERE id = %s",
                [receta_id]
            )
            row = cursor.fetchone()
            if row:
                producto_id = row[0]
        
        # Permitir editar recetas aunque no tengan producto asociado
            
        # Obtener datos del formulario
        data = request.POST
        
        # Validar datos básicos
        nombre = data.get('nombre', '').strip()
        if not nombre:
            return JsonResponse({
                'success': False,
                'message': 'El nombre de la receta es obligatorio'
            })
            
        descripcion = data.get('descripcion', '').strip()
        categoria_id = data.get('categoria_id')
        
        # Conversión segura de valores numéricos
        try:
            tiempo_preparacion = int(data.get('tiempo_preparacion', 0))
        except (ValueError, TypeError):
            tiempo_preparacion = 0
            
        try:
            porciones = int(data.get('porciones', 1))
            if porciones < 1:
                porciones = 1
        except (ValueError, TypeError):
            porciones = 1
            
        instrucciones = data.get('instrucciones', '').strip()
        
        # Conversión segura del precio de venta
        try:
            precio_venta_str = data.get('precio_venta', '0')
            precio_venta = float(precio_venta_str.replace(',', '.'))
        except (ValueError, TypeError):
            logger.warning(f"Precio de venta inválido: {data.get('precio_venta')}, usando 0")
            precio_venta = 0
        
        # Actualizar el producto usando SQL directo para evitar problemas de conversión
        try:
            categoria_sql = "NULL"
            if categoria_id:
                try:
                    # Verificar que la categoría existe
                    categoria_exists = CategoriaProducto.objects.filter(id=categoria_id).exists()
                    if categoria_exists:
                        categoria_sql = categoria_id
                except Exception as e:
                    logger.error(f"Error verificando categoría {categoria_id}: {e}")
            
            with connection.cursor() as cursor:
                if categoria_sql != "NULL":
                    cursor.execute(
                        "UPDATE restaurant_productoventa SET nombre = %s, descripcion = %s, precio = %s, categoria_id = %s, disponible = 1 WHERE id = %s",
                        [nombre, descripcion, precio_venta, categoria_sql, producto_id]
                    )
                else:
                    cursor.execute(
                        "UPDATE restaurant_productoventa SET nombre = %s, descripcion = %s, precio = %s, categoria_id = NULL, disponible = 1 WHERE id = %s",
                        [nombre, descripcion, precio_venta, producto_id]
                    )
            logger.info(f"Producto {producto_id} actualizado correctamente")
        except Exception as e:
            logger.error(f"Error al actualizar producto: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar producto: {str(e)}'
            })
        
        # Actualizar receta
        try:
            receta.tiempo_preparacion = tiempo_preparacion
            receta.porciones = porciones
            receta.instrucciones = instrucciones
            receta.activo = True
            receta.save()
            logger.info(f"Receta {receta.id} actualizada correctamente")
        except Exception as e:
            logger.error(f"Error al actualizar receta: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar receta: {str(e)}'
            })
        
        # Eliminar ingredientes actuales con manejo de errores
        try:
            RecetaInsumo.objects.filter(receta=receta).delete()
            logger.info(f"Ingredientes de receta {receta.id} eliminados correctamente")
        except Exception as e:
            logger.error(f"Error al eliminar ingredientes actuales: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar ingredientes: {str(e)}'
            })
        
        # Procesar nuevos ingredientes
        try:
            insumo_ids = request.POST.getlist('ingrediente_insumo[]') or request.POST.getlist('editar_ingrediente_insumo[]')
            cantidades = request.POST.getlist('ingrediente_cantidad[]') or request.POST.getlist('editar_ingrediente_cantidad[]')
            opcionales = request.POST.getlist('ingrediente_opcional[]') or request.POST.getlist('editar_ingrediente_opcional[]')
            notas_list = request.POST.getlist('ingrediente_notas[]') or request.POST.getlist('editar_ingrediente_notas[]')
            
            costo_total = 0.0
            ingredientes_procesados = 0
            
            for i, insumo_id in enumerate(insumo_ids):
                if not insumo_id or i >= len(cantidades) or not cantidades[i]:
                    continue
                    
                try:
                    insumo = Insumo.objects.get(id=insumo_id)
                    
                    # Conversión segura de cantidad
                    try:
                        cantidad = float(cantidades[i].replace(',', '.'))
                    except (ValueError, TypeError):
                        logger.warning(f"Cantidad inválida para insumo {insumo_id}: {cantidades[i]}, usando 0")
                        cantidad = 0
                        
                    # Verificar si es opcional
                    es_opcional = False
                    if i < len(opcionales) and opcionales[i] == 'on':
                        es_opcional = True
                        
                    # Obtener notas si existen
                    notas = ''
                    if i < len(notas_list):
                        notas = notas_list[i]
                    
                    # Crear el ingrediente
                    RecetaInsumo.objects.create(
                        receta=receta,
                        insumo=insumo,
                        cantidad=cantidad,
                        opcional=es_opcional,
                        notas=notas,
                        orden=i+1
                    )
                    ingredientes_procesados += 1
                    
                    # Calcular costo total con manejo de errores
                    try:
                        precio_unitario = float(insumo.precio_unitario or 0)
                        costo_insumo = precio_unitario * cantidad
                        costo_total += costo_insumo
                    except Exception as e:
                        logger.error(f"Error calculando costo de insumo {insumo.id}: {e}")
                        # Continuar con el siguiente ingrediente
                except Insumo.DoesNotExist:
                    logger.warning(f"Insumo {insumo_id} no encontrado")
                except Exception as e:
                    logger.error(f"Error al procesar ingrediente {i}: {e}")
                    # Continuar con el siguiente ingrediente en lugar de fallar toda la receta
            
            logger.info(f"Se procesaron {ingredientes_procesados} ingredientes para la receta {receta.id}")
            
            # Actualizar costo en el producto con SQL directo
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE restaurant_productoventa SET costo = %s WHERE id = %s",
                        [costo_total, producto_id]
                    )
                logger.info(f"Costo de producto actualizado a {costo_total}")
            except Exception as e:
                logger.error(f"Error al actualizar costo del producto: {e}")
                # No retornamos error, simplemente loggeamos el problema
                
            return JsonResponse({
                'success': True,
                'message': 'Receta actualizada correctamente'
            })
                
        except Exception as e:
            logger.error(f"Error al procesar ingredientes: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar ingredientes: {str(e)}'
            })
            
    except Exception as e:
        logger.error(f"Error al actualizar receta: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error al actualizar receta: {str(e)}'
        })

@login_required
@require_module_access('recetas')
@require_POST
def eliminar_receta(request, receta_id):
    """Eliminar receta"""
    try:
        logger.info(f"Intento de eliminar receta ID: {receta_id}")
        
        try:
            receta = Receta.objects.get(id=receta_id)
        except Receta.DoesNotExist:
            logger.warning(f"Receta no encontrada con ID: {receta_id}")
            return JsonResponse({
                'success': False,
                'message': 'Receta no encontrada'
            }, status=404)
        
        # Guardar el producto asociado para eliminarlo después
        producto = None
        receta_nombre = f"Receta {receta_id}"  # Valor por defecto
        
        try:
            producto = receta.producto
            if producto:
                receta_nombre = producto.nombre or receta_nombre
        except Exception as e:
            logger.warning(f"Error al obtener producto asociado a receta {receta_id}: {e}")
            # Continuamos con la eliminación de la receta aunque no podamos acceder al producto
        
        # Eliminar ingredientes
        try:
            ingredientes_count = RecetaInsumo.objects.filter(receta=receta).count()
            logger.info(f"Eliminando {ingredientes_count} ingredientes de la receta {receta_id}")
            RecetaInsumo.objects.filter(receta=receta).delete()
        except Exception as e:
            logger.error(f"Error al eliminar ingredientes de receta {receta_id}: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar ingredientes: {str(e)}'
            }, status=500)
        
        # Eliminar receta
        try:
            receta.delete()
            logger.info(f"Receta {receta_id} ({receta_nombre}) eliminada correctamente")
        except Exception as e:
            logger.error(f"Error al eliminar receta {receta_id}: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar la receta: {str(e)}'
            }, status=500)
        
        # Eliminar producto asociado si existe
        if producto:
            try:
                producto.delete()
                logger.info(f"Producto asociado a receta {receta_id} eliminado correctamente")
            except Exception as e:
                logger.error(f"Error al eliminar producto asociado a receta {receta_id}: {e}")
                # No devolvemos error aquí ya que la receta ya se eliminó
        
        return JsonResponse({
            'success': True,
            'message': f'Receta "{receta_nombre}" eliminada correctamente'
        })
    except Exception as e:
        logger.error(f"Error inesperado al eliminar receta {receta_id}: {e}")
        logger.error(traceback.format_exc())  # Log the full traceback for debugging
        return JsonResponse({
            'success': False,
            'message': f'Error inesperado al eliminar receta: {str(e)}'
        }, status=500)

@login_required
@require_module_access('recetas')
@require_POST
def duplicar_receta(request, receta_id):
    """Duplicar receta usando Django ORM para evitar problemas de cursor"""
    logger.info(f"Duplicando receta ID: {receta_id}")
    
    from django.db import transaction
    import time
    import random
    
    try:
        # Verificar que la receta original existe
        try:
            receta_original = Receta.objects.get(id=receta_id)
            producto_original = receta_original.producto
        except Receta.DoesNotExist:
            logger.error(f"Receta no encontrada: {receta_id}")
            return JsonResponse({
                'success': False,
                'message': 'Receta no encontrada'
            })
        
        # Crear código único para el nuevo producto
        timestamp = int(time.time())
        random_suffix = random.randint(100, 999)
        codigo_unico = f"REC{timestamp}{random_suffix}"
        
        # Verificar que el código no exista ya (aunque es muy improbable)
        contador_intentos = 0
        while ProductoVenta.objects.filter(codigo=codigo_unico).exists() and contador_intentos < 10:
            random_suffix = random.randint(100, 999)
            codigo_unico = f"REC{timestamp}{random_suffix}"
            contador_intentos += 1
        
        logger.info(f"Duplicando receta con nuevo código único: {codigo_unico}")
        
        # Crear copia del producto
        nombre_nuevo = f"Copia de {producto_original.nombre}"
        
        # Usar transacción para asegurar consistencia
        with transaction.atomic():
            try:
                # Crear nuevo producto usando Django ORM para evitar problemas de cursor
                # Convertir valores decimales a float para evitar problemas
                precio_seguro = float(producto_original.precio) if producto_original.precio else 0.0
                costo_seguro = float(producto_original.costo) if producto_original.costo else 0.0
                margen_seguro = float(producto_original.margen) if producto_original.margen else 0.0
                
                producto_nuevo = ProductoVenta.objects.create(
                    codigo=codigo_unico,
                    nombre=nombre_nuevo,
                    descripcion=producto_original.descripcion or '',
                    precio=Decimal(str(precio_seguro)),
                    costo=Decimal(str(costo_seguro)),
                    margen=Decimal(str(margen_seguro)),
                    tipo=producto_original.tipo or 'plato',
                    disponible=True,
                    es_promocion=producto_original.es_promocion or False,
                    destacado=producto_original.destacado or False,
                    categoria=producto_original.categoria
                )
                
                logger.info(f"Producto duplicado creado: {producto_nuevo.id}")
                
                # Crear nueva receta
                receta_nueva = Receta.objects.create(
                    producto=producto_nuevo,
                    tiempo_preparacion=receta_original.tiempo_preparacion or 0,
                    porciones=receta_original.porciones or 1,
                    instrucciones=receta_original.instrucciones or '',
                    activo=True
                )
                
                logger.info(f"Receta duplicada creada: {receta_nueva.id}")
                
                # Copiar ingredientes
                ingredientes_originales = RecetaInsumo.objects.filter(receta=receta_original)
                for ingrediente in ingredientes_originales:
                    try:
                        # Asegurar que la cantidad se maneja correctamente
                        cantidad = float(ingrediente.cantidad) if ingrediente.cantidad is not None else 0.0
                        
                        RecetaInsumo.objects.create(
                            receta=receta_nueva,
                            insumo=ingrediente.insumo,
                            cantidad=Decimal(str(cantidad)),
                            opcional=ingrediente.opcional or False,
                            notas=ingrediente.notas or '',
                            orden=ingrediente.orden or 0
                        )
                    except Exception as ing_error:
                        logger.error(f"Error copiando ingrediente {ingrediente.id}: {ing_error}")
                        # Continuar con el siguiente ingrediente
                
                logger.info(f"Receta {receta_id} duplicada como {receta_nueva.id} con éxito")
                
                return JsonResponse({
                    'success': True,
                    'receta': {
                        'id': receta_nueva.id,
                        'nombre': nombre_nuevo
                    },
                    'message': 'Receta duplicada correctamente'
                })
                
            except Exception as e:
                logger.error(f"Error en la transacción de duplicación: {e}")
                # Django manejará automáticamente el rollback
                return JsonResponse({
                    'success': False,
                    'message': f'Error al duplicar receta: {str(e)}'
                })
            
    except Exception as e:
        logger.error(f"Error al duplicar receta: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error al duplicar receta: {str(e)}'
        })

@login_required
@require_POST
def editar_categoria_receta(request, categoria_id):
    """Editar categoría de receta"""
    try:
        categoria = get_object_or_404(CategoriaProducto, id=categoria_id)
        data = request.POST
        
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        
        if not nombre:
            return JsonResponse({
                'success': False,
                'message': 'El nombre de la categoría es obligatorio'
            })
        
        # Verificar si ya existe otra categoría con ese nombre
        if CategoriaProducto.objects.filter(nombre=nombre).exclude(id=categoria_id).exists():
            return JsonResponse({
                'success': False,
                'message': f'Ya existe otra categoría con el nombre "{nombre}"'
            })
        
        # Actualizar la categoría
        categoria.nombre = nombre
        categoria.descripcion = descripcion
        categoria.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Categoría actualizada correctamente'
        })
    except CategoriaProducto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Categoría no encontrada'
        })
    except Exception as e:
        logger.error(f"Error al actualizar categoría: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al actualizar categoría: {str(e)}'
        })

@login_required
@require_POST
def eliminar_categoria_receta(request, categoria_id):
    """Eliminar categoría de receta"""
    try:
        categoria = get_object_or_404(CategoriaProducto, id=categoria_id)
        
        # Verificar si hay productos asociados
        productos_asociados = ProductoVenta.objects.filter(categoria=categoria).count()
        if productos_asociados > 0:
            return JsonResponse({
                'success': False,
                'message': f'No se puede eliminar la categoría porque tiene {productos_asociados} productos asociados'
            })
        
        # Eliminar la categoría
        categoria.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Categoría eliminada correctamente'
        })
    except CategoriaProducto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Categoría no encontrada'
        })
    except Exception as e:
        logger.error(f"Error al eliminar categoría: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar categoría: {str(e)}'
        })

@login_required
def obtener_todos_los_insumos(request):
    """API para obtener todos los insumos disponibles para recetas"""
    try:
        # Obtener todos los insumos activos
        insumos = Insumo.objects.filter(activo=True).select_related('categoria', 'unidad_medida')
        
        insumos_data = []
        for insumo in insumos:
            insumos_data.append({
                'id': insumo.id,
                'codigo': insumo.codigo,
                'nombre': insumo.nombre,
                'tipo': insumo.tipo,
                'categoria': insumo.categoria.nombre,
                'unidad_medida': insumo.unidad_medida.abreviacion,
                'unidad_medida_nombre': insumo.unidad_medida.nombre,
                'unidad_abrev': insumo.unidad_medida.abreviacion,
                'precio_unitario': float(insumo.precio_unitario),
                'stock_actual': float(insumo.stock_actual)
            })
        
        return JsonResponse({
            'success': True,
            'insumos': insumos_data,
            'total': len(insumos_data),
            'message': 'Insumos cargados correctamente'
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo todos los insumos: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })
