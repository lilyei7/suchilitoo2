from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Avg
from decimal import Decimal

from restaurant.models import (
    Receta, RecetaInsumo, Insumo as RestaurantInsumo,
    CategoriaProducto, ProductoVenta, CategoriaReceta
)
from .base_views import get_sidebar_context, is_admin_or_manager

# Usamos el Insumo de restaurant para tener consistencia
Insumo = RestaurantInsumo

@login_required
def recetas_view(request):
    """Vista principal para gestión de recetas"""
    # Obtener todas las recetas activas con sus productos relacionados
    recetas = Receta.objects.filter(activa=True).order_by('nombre')
    
    # Añadir precio de venta a cada receta
    for receta in recetas:
        try:
            producto = ProductoVenta.objects.get(receta=receta)
            receta.precio_venta = producto.precio
            receta.tiene_producto = True
        except ProductoVenta.DoesNotExist:
            receta.precio_venta = None
            receta.tiene_producto = False
    
    # Estadísticas
    total_recetas = recetas.count()
    costo_promedio = recetas.aggregate(promedio=Avg('costo_total'))['promedio'] or 0
    tiempo_promedio = recetas.aggregate(promedio=Avg('tiempo_preparacion'))['promedio'] or 0
    
    # Obtener categorías de productos para el formulario
    categorias_productos = CategoriaProducto.objects.all().order_by('nombre')
    
    context = {
        'recetas': recetas,
        'total_recetas': total_recetas,
        'costo_promedio': costo_promedio,
        'tiempo_promedio': int(tiempo_promedio),
        'categorias_productos': categorias_productos,
        **get_sidebar_context('recetas')
    }
    
    return render(request, 'dashboard/recetas.html', context)

@login_required
def obtener_insumos_basicos(request):
    """API para obtener insumos básicos disponibles"""
    try:
        insumos = Insumo.objects.filter(
            tipo='basico', 
            activo=True
        ).select_related('categoria', 'unidad_medida').order_by('nombre')
        
        insumos_data = []
        for insumo in insumos:
            insumos_data.append({
                'id': insumo.id,
                'codigo': insumo.codigo,
                'nombre': insumo.nombre,
                'tipo': 'basico',
                'categoria_nombre': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
                'unidad_medida_nombre': str(insumo.unidad_medida) if insumo.unidad_medida else 'Sin unidad',
                'unidad_abrev': insumo.unidad_medida.abreviacion if insumo.unidad_medida else '',
                'precio_unitario': float(insumo.precio_unitario)
            })
        
        return JsonResponse({
            'success': True,
            'insumos': insumos_data,
            'count': len(insumos_data)
        })
    except Exception as e:
        print(f"Error obteniendo insumos básicos: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
def obtener_insumos_compuestos(request):
    """API para obtener insumos compuestos disponibles"""
    try:
        insumos = Insumo.objects.filter(
            tipo='compuesto', 
            activo=True
        ).select_related('categoria', 'unidad_medida').order_by('nombre')
        
        insumos_data = []
        for insumo in insumos:
            insumos_data.append({
                'id': insumo.id,
                'codigo': insumo.codigo,
                'nombre': insumo.nombre,
                'tipo': 'compuesto',
                'categoria_nombre': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
                'unidad_medida_nombre': str(insumo.unidad_medida) if insumo.unidad_medida else 'Sin unidad',
                'unidad_abrev': insumo.unidad_medida.abreviacion if insumo.unidad_medida else '',
                'precio_unitario': float(insumo.precio_unitario)
            })
        
        return JsonResponse({
            'success': True,
            'insumos': insumos_data,
            'count': len(insumos_data)
        })
    except Exception as e:
        print(f"Error obteniendo insumos compuestos: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
def obtener_insumos_elaborados(request):
    """API para obtener insumos elaborados disponibles"""
    try:
        insumos = Insumo.objects.filter(
            tipo='elaborado', 
            activo=True
        ).select_related('categoria', 'unidad_medida').order_by('nombre')
        
        insumos_data = []
        for insumo in insumos:
            insumos_data.append({
                'id': insumo.id,
                'codigo': insumo.codigo,
                'nombre': insumo.nombre,
                'tipo': 'elaborado',
                'categoria_nombre': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
                'unidad_medida_nombre': str(insumo.unidad_medida) if insumo.unidad_medida else 'Sin unidad',
                'unidad_abrev': insumo.unidad_medida.abreviacion if insumo.unidad_medida else '',
                'precio_unitario': float(insumo.precio_unitario)
            })
        
        return JsonResponse({
            'success': True,
            'insumos': insumos_data,
            'count': len(insumos_data)
        })
    except Exception as e:
        print(f"Error obteniendo insumos elaborados: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def crear_receta(request):
    """Vista para crear una nueva receta"""
    if request.method == 'POST':
        try:            # Datos básicos de la receta
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            categoria_codigo = request.POST.get('categoria')  # Código de categoría de receta
            tiempo_preparacion = request.POST.get('tiempo_preparacion')
            porciones = request.POST.get('porciones', 1)
            precio_venta = request.POST.get('precio_venta')
            
            # Validaciones básicas
            if not all([nombre, tiempo_preparacion, porciones]):
                return JsonResponse({
                    'success': False,
                    'message': 'Los campos nombre, tiempo de preparación y porciones son obligatorios'
                })
            
            # Convertir datos a tipos correctos
            tiempo_preparacion = int(tiempo_preparacion)
            porciones = int(porciones)
            precio_venta = Decimal(str(precio_venta)) if precio_venta else None
              # Obtener ingredientes unificados (todos los tipos de insumos)
            ingredientes_data = []
            insumo_ids = request.POST.getlist('ingrediente_insumo[]')
            cantidades = request.POST.getlist('ingrediente_cantidad[]')
            
            if len(insumo_ids) != len(cantidades):
                return JsonResponse({
                    'success': False,
                    'message': 'Error en los datos de ingredientes'
                })
            
            # Procesar todos los ingredientes (básicos, compuestos y elaborados)
            total_costo_ingredientes = Decimal('0')
            for i, (insumo_id, cantidad) in enumerate(zip(insumo_ids, cantidades)):
                if not insumo_id or not cantidad:
                    continue
                
                try:
                    insumo = Insumo.objects.get(id=insumo_id, activo=True)
                    cantidad_decimal = Decimal(str(cantidad))
                    
                    if cantidad_decimal <= 0:
                        return JsonResponse({
                            'success': False,
                            'message': f'La cantidad para {insumo.nombre} debe ser mayor a 0'
                        })
                    
                    costo = cantidad_decimal * insumo.precio_unitario
                    total_costo_ingredientes += costo
                    
                    ingredientes_data.append({
                        'insumo': insumo,
                        'cantidad': cantidad_decimal,
                        'costo': costo
                    })
                except Insumo.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': f'El insumo con ID {insumo_id} no existe o no está activo'
                    })
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'message': f'Cantidad inválida para el ingrediente {i+1}'
                    })
            
            # Verificar que haya al menos un ingrediente
            if not ingredientes_data:
                return JsonResponse({
                    'success': False,
                    'message': 'Debe agregar al menos un ingrediente'
                })
              # Calcular costo total
            costo_total = total_costo_ingredientes
            
            # Obtener categoría de receta si se proporciona
            categoria_receta = None
            if categoria_codigo:
                try:
                    categoria_receta = CategoriaReceta.objects.get(codigo=categoria_codigo)
                except CategoriaReceta.DoesNotExist:
                    # No es un error crítico, la receta puede no tener categoría
                    pass
            
            # Crear la receta en la base de datos
            with transaction.atomic():
                # Crear la receta
                receta = Receta.objects.create(
                    nombre=nombre,
                    categoria=categoria_receta,
                    descripcion=descripcion,
                    instrucciones='',  # Por ahora sin instrucciones detalladas
                    tiempo_preparacion=tiempo_preparacion,
                    porciones=porciones,
                    costo_total=costo_total,
                    activa=True
                )
                  # Agregar ingredientes unificados (todos los tipos)
                for item in ingredientes_data:
                    RecetaInsumo.objects.create(
                        receta=receta,
                        insumo=item['insumo'],
                        cantidad=item['cantidad']
                    )
                
                # Si hay precio de venta, crear un producto asociado
                if precio_venta:
                    try:
                        # Obtener categoría de producto por defecto
                        categoria_producto = CategoriaProducto.objects.get(nombre='Platos del Menú')
                        
                        codigo = f"PROD-{receta.id}"
                        ProductoVenta.objects.create(
                            codigo=codigo,
                            nombre=nombre,
                            descripcion=descripcion,
                            categoria=categoria_producto,
                            precio=precio_venta,
                            costo=costo_total,
                            receta=receta,
                            disponible=True
                        )
                    except CategoriaProducto.DoesNotExist:
                        # Si no existe la categoría por defecto, no crear el producto
                        # Esto no es un error crítico
                        pass
            
            return JsonResponse({
                'success': True,
                'message': f'Receta "{nombre}" creada exitosamente',
                'receta_id': receta.id,
                'costo_total': float(costo_total),
                'ingredientes': len(ingredientes_data)
            })
            
        except Exception as e:
            print(f"Error creando receta: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })

@login_required
def detalle_receta(request, receta_id):
    """Vista para ver detalles de una receta"""
    try:
        receta = get_object_or_404(Receta, id=receta_id, activa=True)
        
        # Obtener ingredientes
        ingredientes = RecetaInsumo.objects.filter(receta=receta).select_related('insumo', 'insumo__unidad_medida')
        
        # Obtener producto asociado si existe
        try:
            producto = ProductoVenta.objects.get(receta=receta)
            precio_venta = float(producto.precio)
        except ProductoVenta.DoesNotExist:
            precio_venta = None
          # Preparar datos de la receta
        receta_data = {
            'id': receta.id,
            'nombre': receta.nombre,
            'descripcion': receta.descripcion,
            'tiempo_preparacion': receta.tiempo_preparacion,
            'porciones': receta.porciones,
            'costo_total': float(receta.costo_total),
            'precio_venta': precio_venta,
            'categoria': receta.categoria.nombre if hasattr(receta, 'categoria') and receta.categoria else None,
            'categoria_codigo': receta.categoria.codigo if hasattr(receta, 'categoria') and receta.categoria else None,
            'fecha_creacion': receta.created_at.strftime('%d/%m/%Y')
        }
        
        # Preparar datos de ingredientes
        ingredientes_data = []
        for ingrediente in ingredientes:
            ingredientes_data.append({
                'id': ingrediente.insumo.id,
                'nombre': ingrediente.insumo.nombre,
                'codigo': ingrediente.insumo.codigo,
                'tipo': ingrediente.insumo.tipo,
                'cantidad': float(ingrediente.cantidad),
                'unidad': ingrediente.insumo.unidad_medida.abreviacion if ingrediente.insumo.unidad_medida else '',
                'precio_unitario': float(ingrediente.insumo.precio_unitario),
                'costo': float(ingrediente.cantidad * ingrediente.insumo.precio_unitario)
            })
        
        return JsonResponse({
            'success': True,
            'receta': receta_data,
            'ingredientes': ingredientes_data
        })
        
    except Exception as e:
        print(f"Error obteniendo detalle de receta: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def eliminar_receta(request, receta_id):
    """Vista para eliminar una receta"""
    if request.method == 'POST':
        try:
            receta = get_object_or_404(Receta, id=receta_id)
            
            # Verificar si hay productos asociados
            productos = ProductoVenta.objects.filter(receta=receta)
            
            with transaction.atomic():
                # Desactivar la receta en lugar de eliminarla
                receta.activa = False
                receta.save()
                
                # Desactivar productos asociados
                for producto in productos:
                    producto.disponible = False
                    producto.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Receta "{receta.nombre}" eliminada exitosamente'
            })
            
        except Exception as e:
            print(f"Error eliminando receta: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })

@login_required
def obtener_todos_los_insumos(request):
    """API unificada para obtener todos los tipos de insumos disponibles"""
    try:
        # Obtener todos los insumos activos
        insumos = Insumo.objects.filter(
            activo=True
        ).select_related('categoria', 'unidad_medida').order_by('tipo', 'nombre')
        
        insumos_data = []
        for insumo in insumos:
            insumos_data.append({
                'id': insumo.id,
                'codigo': insumo.codigo,
                'nombre': insumo.nombre,
                'tipo': insumo.tipo,
                'tipo_display': {
                    'basico': 'Básico',
                    'compuesto': 'Compuesto', 
                    'elaborado': 'Elaborado'
                }.get(insumo.tipo, insumo.tipo),
                'categoria_nombre': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
                'unidad_medida_nombre': str(insumo.unidad_medida) if insumo.unidad_medida else 'Sin unidad',
                'unidad_abrev': insumo.unidad_medida.abreviacion if insumo.unidad_medida else '',
                'precio_unitario': float(insumo.precio_unitario)
            })
        
        return JsonResponse({
            'success': True,
            'insumos': insumos_data,
            'count': len(insumos_data),
            'by_type': {
                'basicos': len([i for i in insumos_data if i['tipo'] == 'basico']),
                'compuestos': len([i for i in insumos_data if i['tipo'] == 'compuesto']),
                'elaborados': len([i for i in insumos_data if i['tipo'] == 'elaborado'])
            }
        })
        
    except Exception as e:
        print(f"Error obteniendo todos los insumos: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })
    
@login_required
@user_passes_test(is_admin_or_manager)
def editar_receta(request, receta_id):
    """Editar una receta existente"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        receta = get_object_or_404(Receta, id=receta_id)
          # Obtener datos del formulario
        nombre = request.POST.get('nombre', '').strip()
        categoria_codigo = request.POST.get('categoria')  # Código de categoría de receta
        descripcion = request.POST.get('descripcion', '').strip()
        tiempo_preparacion = request.POST.get('tiempo_preparacion')
        porciones = request.POST.get('porciones')
        precio_venta = request.POST.get('precio_venta')
        
        # Validaciones básicas
        if not nombre:
            return JsonResponse({'success': False, 'message': 'El nombre es obligatorio'})
        
        if not tiempo_preparacion or int(tiempo_preparacion) <= 0:
            return JsonResponse({'success': False, 'message': 'El tiempo de preparación debe ser mayor a 0'})
        
        if not porciones or int(porciones) <= 0:
            return JsonResponse({'success': False, 'message': 'Las porciones deben ser mayor a 0'})
        
        # Validar ingredientes
        ingredientes_insumos = request.POST.getlist('editar_ingrediente_insumo[]')
        ingredientes_cantidades = request.POST.getlist('editar_ingrediente_cantidad[]')
        
        # Filtrar ingredientes válidos
        ingredientes_validos = []
        for i, insumo_id in enumerate(ingredientes_insumos):
            if insumo_id and i < len(ingredientes_cantidades):
                try:
                    cantidad = float(ingredientes_cantidades[i])
                    if cantidad > 0:
                        ingredientes_validos.append((insumo_id, cantidad))
                except (ValueError, IndexError):
                    continue
        
        if not ingredientes_validos:
            return JsonResponse({'success': False, 'message': 'Debes agregar al menos un ingrediente válido'})
        
        # Verificar que los insumos existan
        insumos_ids = [ing[0] for ing in ingredientes_validos]
        insumos_existentes = Insumo.objects.filter(id__in=insumos_ids, activo=True)
        
        if len(insumos_existentes) != len(insumos_ids):
            return JsonResponse({'success': False, 'message': 'Algunos insumos no son válidos'})
        
        # Verificar que no haya duplicados
        if len(set(insumos_ids)) != len(insumos_ids):
            return JsonResponse({'success': False, 'message': 'No puedes agregar el mismo ingrediente más de una vez'})
        
        with transaction.atomic():
            # Actualizar datos básicos de la receta
            receta.nombre = nombre
            receta.descripcion = descripcion
            receta.tiempo_preparacion = int(tiempo_preparacion)
            receta.porciones = int(porciones)
              # Actualizar categoría si se proporcionó
            if categoria_codigo:
                try:
                    categoria = CategoriaReceta.objects.get(codigo=categoria_codigo)
                    receta.categoria = categoria
                except CategoriaReceta.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Categoría de receta no válida'})
            else:
                receta.categoria = None
            
            # Eliminar todos los ingredientes existentes
            RecetaInsumo.objects.filter(receta=receta).delete()
            
            # Calcular costo total
            costo_total = Decimal('0.00')
            
            # Crear nuevos ingredientes
            for insumo_id, cantidad in ingredientes_validos:
                insumo = insumos_existentes.get(id=insumo_id)
                costo_ingrediente = Decimal(str(cantidad)) * insumo.precio_unitario
                costo_total += costo_ingrediente
                
                RecetaInsumo.objects.create(
                    receta=receta,
                    insumo=insumo,
                    cantidad=Decimal(str(cantidad))
                )
            
            # Actualizar costo total
            receta.costo_total = costo_total
              # Manejar precio de venta y producto asociado
            if precio_venta:
                try:
                    precio_venta_decimal = Decimal(str(precio_venta))
                    
                    # Obtener categoría de producto por defecto
                    try:
                        categoria_producto = CategoriaProducto.objects.get(nombre='Platos del Menú')
                    except CategoriaProducto.DoesNotExist:
                        # Si no existe, crear una categoría por defecto
                        categoria_producto = CategoriaProducto.objects.create(
                            nombre='Platos del Menú',
                            descripcion='Productos del menú principal'
                        )
                    
                    # Crear o actualizar producto de venta
                    producto, created = ProductoVenta.objects.get_or_create(
                        receta=receta,
                        defaults={
                            'codigo': f"PROD-{receta.id}",
                            'nombre': nombre,
                            'descripcion': descripcion,
                            'precio': precio_venta_decimal,
                            'costo': costo_total,
                            'categoria': categoria_producto,
                            'disponible': True
                        }
                    )
                    
                    if not created:
                        # Actualizar producto existente
                        producto.nombre = nombre
                        producto.descripcion = descripcion
                        producto.precio = precio_venta_decimal
                        producto.costo = costo_total
                        producto.save()
                    
                except (ValueError, TypeError):
                    return JsonResponse({'success': False, 'message': 'Precio de venta no válido'})
            
            receta.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Receta "{nombre}" actualizada exitosamente'
        })
        
    except Exception as e:
        print(f"Error editando receta: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def duplicar_receta(request, receta_id):
    """Duplicar una receta existente"""
    try:
        # Obtener la receta original
        receta_original = get_object_or_404(Receta, id=receta_id, activa=True)
          # Obtener los ingredientes
        ingredientes_original = RecetaInsumo.objects.filter(receta=receta_original).select_related('insumo')
        
        # Crear una nueva receta con los datos de la original
        with transaction.atomic():            # Crear la nueva receta
            nueva_receta = Receta.objects.create(
                nombre=f"{receta_original.nombre} (Copia)",
                categoria=receta_original.categoria,  # Copiar categoría de receta también
                descripcion=receta_original.descripcion,
                instrucciones=receta_original.instrucciones,
                tiempo_preparacion=receta_original.tiempo_preparacion,
                porciones=receta_original.porciones,
                costo_total=receta_original.costo_total,
                activa=True
            )
            
            # Copiar los ingredientes
            for ingrediente in ingredientes_original:
                RecetaInsumo.objects.create(
                    receta=nueva_receta,
                    insumo=ingrediente.insumo,
                    cantidad=ingrediente.cantidad
                )
            
            # Verificar si la receta original tiene un producto asociado
            try:
                producto_original = ProductoVenta.objects.get(receta=receta_original)
                
                # Crear un nuevo producto para la nueva receta
                ProductoVenta.objects.create(
                    codigo=f"PROD-{nueva_receta.id}",
                    nombre=f"{producto_original.nombre} (Copia)",
                    descripcion=producto_original.descripcion,
                    categoria=producto_original.categoria,
                    precio=producto_original.precio,
                    costo=producto_original.costo,
                    receta=nueva_receta,
                    disponible=True
                )
            except ProductoVenta.DoesNotExist:
                # No hay producto asociado, no se hace nada
                pass
        
        # Preparar datos para la respuesta
        nueva_receta_data = {
            'id': nueva_receta.id,
            'nombre': nueva_receta.nombre
        }
        
        return JsonResponse({
            'success': True,
            'message': f'Receta "{receta_original.nombre}" duplicada exitosamente',
            'receta': nueva_receta_data
        })
        
    except Exception as e:
        print(f"Error duplicando receta: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })
    
@login_required
@user_passes_test(is_admin_or_manager)
def obtener_categorias_productos(request):
    """API para obtener todas las categorías de productos"""
    categorias = CategoriaProducto.objects.filter(activa=True).order_by('nombre')
    categorias_data = [
        {
            'id': cat.id, 
            'nombre': cat.nombre,
            'descripcion': cat.descripcion
        } 
        for cat in categorias
    ]
    
    return JsonResponse({
        'success': True,
        'categorias': categorias_data
    })

@login_required
@user_passes_test(is_admin_or_manager)
def crear_categoria_producto(request):
    """Vista para crear una nueva categoría de producto"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido'
        })
    
    try:
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        
        if not nombre:
            return JsonResponse({
                'success': False,
                'message': 'El nombre de la categoría es requerido'
            })
        
        # Verificar si ya existe una categoría con ese nombre
        if CategoriaProducto.objects.filter(nombre__iexact=nombre, activa=True).exists():
            return JsonResponse({
                'success': False,
                'message': f'Ya existe una categoría con el nombre "{nombre}"'
            })
        
        # Crear la categoría
        categoria = CategoriaProducto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            activa=True
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Categoría "{nombre}" creada correctamente',
            'categoria': {
                'id': categoria.id,
                'nombre': categoria.nombre,
                'descripcion': categoria.descripcion
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al crear la categoría: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def eliminar_categoria_producto(request, categoria_id):
    """Vista para eliminar una categoría de producto"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido'
        })
    
    try:
        categoria = get_object_or_404(CategoriaProducto, id=categoria_id)
        
        # Verificar si hay productos asociados a esta categoría
        if categoria.productoventa_set.exists():
            return JsonResponse({
                'success': False,
                'message': 'No se puede eliminar la categoría porque tiene productos asociados'
            })
        
        nombre = categoria.nombre
        categoria.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Categoría "{nombre}" eliminada correctamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar la categoría: {str(e)}'
        })

@login_required
def obtener_categorias_recetas(request):
    """API para obtener todas las categorías de recetas"""
    try:
        categorias = CategoriaReceta.objects.all().order_by('nombre')
        categorias_data = []
        
        for categoria in categorias:
            categorias_data.append({
                'id': categoria.id,
                'codigo': categoria.codigo,
                'nombre': categoria.nombre,
                'descripcion': categoria.descripcion,
                'activa': categoria.activa,
                'created_at': categoria.created_at.strftime('%d/%m/%Y')
            })
        
        return JsonResponse({
            'success': True,
            'categorias': categorias_data,
            'count': len(categorias_data)
        })
        
    except Exception as e:
        print(f"Error obteniendo categorías de recetas: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def crear_categoria_receta(request):
    """Vista para crear una nueva categoría de receta"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido'
        })
    
    try:
        codigo = request.POST.get('codigo', '').strip().lower()
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        
        # Validaciones
        if not codigo:
            return JsonResponse({
                'success': False,
                'message': 'El código es obligatorio'
            })
        
        if not nombre:
            return JsonResponse({
                'success': False,
                'message': 'El nombre es obligatorio'
            })
        
        # Verificar que el código no exista
        if CategoriaReceta.objects.filter(codigo=codigo).exists():
            return JsonResponse({
                'success': False,
                'message': f'Ya existe una categoría con el código "{codigo}"'
            })
        
        # Crear la categoría
        categoria = CategoriaReceta.objects.create(
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion,
            activa=True
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Categoría "{nombre}" creada correctamente',
            'categoria': {
                'id': categoria.id,
                'codigo': categoria.codigo,
                'nombre': categoria.nombre,
                'descripcion': categoria.descripcion
            }
        })
        
    except Exception as e:
        print(f"Error creando categoría de receta: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def editar_categoria_receta(request, categoria_id):
    """Vista para editar una categoría de receta"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido'
        })
    
    try:
        categoria = get_object_or_404(CategoriaReceta, id=categoria_id)
        
        codigo = request.POST.get('codigo', '').strip().lower()
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        
        # Validaciones
        if not codigo:
            return JsonResponse({
                'success': False,
                'message': 'El código es obligatorio'
            })
        
        if not nombre:
            return JsonResponse({
                'success': False,
                'message': 'El nombre es obligatorio'
            })
        
        # Verificar que el código no exista (excepto en esta categoría)
        if CategoriaReceta.objects.filter(codigo=codigo).exclude(id=categoria_id).exists():
            return JsonResponse({
                'success': False,
                'message': f'Ya existe otra categoría con el código "{codigo}"'
            })
        
        # Actualizar la categoría
        categoria.codigo = codigo
        categoria.nombre = nombre
        categoria.descripcion = descripcion
        categoria.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Categoría "{nombre}" actualizada correctamente'
        })
        
    except Exception as e:
        print(f"Error editando categoría de receta: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def eliminar_categoria_receta(request, categoria_id):
    """Vista para eliminar una categoría de receta"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido'
        })
    
    try:
        categoria = get_object_or_404(CategoriaReceta, id=categoria_id)
        
        # Verificar si hay recetas usando esta categoría
        recetas_usando = Receta.objects.filter(categoria=categoria, activa=True).count()
        
        if recetas_usando > 0:
            return JsonResponse({
                'success': False,
                'message': f'No se puede eliminar la categoría "{categoria.nombre}" porque tiene {recetas_usando} receta(s) asociada(s)'
            })
        
        nombre_categoria = categoria.nombre
        categoria.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Categoría "{nombre_categoria}" eliminada correctamente'
        })
        
    except Exception as e:
        print(f"Error eliminando categoría de receta: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })
