from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from restaurant.models import Receta, CategoriaProducto, ProductoVenta, RecetaInsumo, Insumo
from django.db.models import Avg, Count, Sum
from decimal import Decimal

@login_required
def recetas_view(request):
    """Vista principal para mostrar las recetas"""
    try:
        # Obtener todas las recetas
        recetas = Receta.objects.filter(activo=True).select_related('producto', 'producto__categoria')
        
        # Calcular estadísticas
        total_recetas = recetas.count()
        costo_promedio = 0
        tiempo_promedio = 0
        
        if total_recetas > 0:
            tiempo_promedio = recetas.aggregate(Avg('tiempo_preparacion'))['tiempo_preparacion__avg'] or 0
            
            # Calcular costo promedio
            costos = []
            for receta in recetas:
                insumos = RecetaInsumo.objects.filter(receta=receta)
                costo_total = sum(insumo.cantidad * insumo.insumo.precio_unitario for insumo in insumos)
                costos.append(costo_total)
            
            if costos:
                costo_promedio = sum(costos) / len(costos)
          # Preparar listado de recetas para el template
        recetas_data = []
        for receta in recetas:
            insumos = RecetaInsumo.objects.filter(receta=receta)
            
            # Calcular costo total de manera segura
            costo_total = Decimal('0.00')
            for insumo in insumos:
                precio_unitario = insumo.insumo.precio_unitario or Decimal('0.00')
                cantidad = insumo.cantidad or Decimal('0.00')
                costo_total += precio_unitario * cantidad
            
            # Convertimos a formato legible
            precio_venta = float(receta.producto.precio) if receta.producto.precio else 0
            
            recetas_data.append({
                'id': receta.id,
                'nombre': receta.producto.nombre,
                'categoria': receta.producto.categoria.nombre if receta.producto.categoria else 'Sin categoría',
                'tiempo_preparacion': receta.tiempo_preparacion,
                'porciones': receta.porciones,
                'costo_total': float(costo_total),
                'precio_venta': precio_venta,
                'ingredientes_count': insumos.count()
            })
        
        context = {
            'total_recetas': total_recetas,
            'costo_promedio': costo_promedio,
            'tiempo_promedio': int(tiempo_promedio),
            'recetas': recetas_data
        }
        return render(request, 'dashboard/recetas.html', context)
    except Exception as e:
        print(f"Error en recetas_view: {e}")
        return render(request, 'dashboard/recetas.html', {
            'total_recetas': 0,
            'costo_promedio': 0,
            'tiempo_promedio': 0,
            'recetas': []
        })

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
        print(f"Error en obtener_categorias_recetas: {e}")
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
        print(f"Error al crear categoría: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al crear categoría: {str(e)}'
        })

@login_required
@require_POST
def crear_receta(request):
    """Crear nueva receta"""
    try:
        data = request.POST
        
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        categoria_id = data.get('categoria_id')
        tiempo_preparacion = data.get('tiempo_preparacion', 0)
        porciones = data.get('porciones', 1)
        instrucciones = data.get('instrucciones', '').strip()
        precio_venta = data.get('precio_venta', 0)
        costo_total = data.get('costo_total', 0)
        
        if not nombre:
            return JsonResponse({
                'success': False,
                'message': 'El nombre de la receta es obligatorio'
            })
        
        if not categoria_id:
            return JsonResponse({
                'success': False,
                'message': 'La categoría es obligatoria'
            })
        
        # Obtener la categoría
        try:
            categoria = CategoriaProducto.objects.get(id=categoria_id)
        except CategoriaProducto.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'La categoría seleccionada no existe'
            })
        
        # Crear producto asociado a la receta
        producto = ProductoVenta.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            codigo=f"REC{ProductoVenta.objects.count() + 1:04d}",
            precio=Decimal(precio_venta),
            costo=Decimal(costo_total),
            tipo='plato',
            disponible=True,
            categoria=categoria
        )
        
        # Crear la receta
        receta = Receta.objects.create(
            producto=producto,
            tiempo_preparacion=int(tiempo_preparacion) if tiempo_preparacion else 0,
            porciones=int(porciones) if porciones else 1,
            instrucciones=instrucciones,
            activo=True
        )
        
        # Procesar ingredientes
        insumo_ids = request.POST.getlist('ingrediente_insumo[]')
        cantidades = request.POST.getlist('ingrediente_cantidad[]')
        opcionales = request.POST.getlist('ingrediente_opcional[]')
        notas_list = request.POST.getlist('ingrediente_notas[]')
        
        for i, insumo_id in enumerate(insumo_ids):
            if insumo_id and cantidades[i]:
                try:
                    insumo = Insumo.objects.get(id=insumo_id)
                    cantidad = Decimal(cantidades[i])
                    es_opcional = i < len(opcionales) and opcionales[i] == 'on'
                    notas = notas_list[i] if i < len(notas_list) else ''
                    
                    RecetaInsumo.objects.create(
                        receta=receta,
                        insumo=insumo,
                        cantidad=cantidad,
                        opcional=es_opcional,
                        notas=notas,
                        orden=i+1
                    )
                except Insumo.DoesNotExist:
                    print(f"Insumo {insumo_id} no encontrado")
                except Exception as e:
                    print(f"Error al procesar ingrediente {i}: {e}")
        
        return JsonResponse({
            'success': True,
            'receta_id': receta.id,
            'message': 'Receta creada correctamente'
        })
    except Exception as e:
        print(f"Error al crear receta: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al crear receta: {str(e)}'
        })

@login_required
def detalle_receta(request, receta_id):
    """Obtener detalle de una receta"""
    try:
        print(f"Obteniendo detalle para receta ID: {receta_id}")
        receta = get_object_or_404(Receta, id=receta_id)
        
        # Obtener ingredientes
        ingredientes = RecetaInsumo.objects.filter(receta=receta).select_related('insumo', 'insumo__unidad_medida')
        
        # Calcular costo total
        costo_total = Decimal('0.00')
        for ingrediente in ingredientes:
            precio_unitario = ingrediente.insumo.precio_unitario or Decimal('0.00')
            cantidad = ingrediente.cantidad or Decimal('0.00')
            costo_ingrediente = precio_unitario * cantidad
            costo_total += costo_ingrediente
        
        print(f"Costo total calculado: {costo_total}")
        
        # Preparar datos para la respuesta
        receta_data = {
            'id': receta.id,
            'nombre': receta.producto.nombre,
            'descripcion': receta.producto.descripcion or '',
            'categoria': {
                'id': receta.producto.categoria.id if receta.producto.categoria else None,
                'nombre': receta.producto.categoria.nombre if receta.producto.categoria else 'Sin categoría'
            },
            'tiempo_preparacion': receta.tiempo_preparacion,
            'porciones': receta.porciones,
            'costo_total': float(costo_total),
            'precio_venta': float(receta.producto.precio),
            'instrucciones': receta.instrucciones or ''
        }
        
        print(f"Datos de receta preparados: {receta_data}")
        
        ingredientes_data = []
        for ingrediente in ingredientes:
            # Calcular costo individual del ingrediente
            precio_unitario = float(ingrediente.insumo.precio_unitario or Decimal('0.00'))
            cantidad = float(ingrediente.cantidad or Decimal('0.00'))
            costo_ingrediente = precio_unitario * cantidad
            
            # Preparar datos del ingrediente
            ingrediente_data = {
                'id': ingrediente.id,
                'insumo': {
                    'id': ingrediente.insumo.id,
                    'nombre': ingrediente.insumo.nombre,
                    'tipo': ingrediente.insumo.tipo,
                    'unidad_medida': {
                        'id': ingrediente.insumo.unidad_medida.id if ingrediente.insumo.unidad_medida else None,
                        'nombre': ingrediente.insumo.unidad_medida.nombre if ingrediente.insumo.unidad_medida else 'Unidad',
                    },
                    'unidad_abrev': ingrediente.insumo.unidad_medida.abreviacion if ingrediente.insumo.unidad_medida else 'Un'
                },
                'cantidad': cantidad,
                'costo_unitario': precio_unitario,
                'costo_total': costo_ingrediente,
                'opcional': ingrediente.opcional,
                'notas': ingrediente.notas or ''
            }
            
            ingredientes_data.append(ingrediente_data)
        
        print(f"Total de ingredientes: {len(ingredientes_data)}")
        
        response_data = {
            'success': True,
            'receta': receta_data,
            'ingredientes': ingredientes_data
        }
        
        return JsonResponse(response_data)
    except Receta.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Receta no encontrada'
        })
    except Exception as e:
        print(f"Error al obtener receta: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener receta: {str(e)}'
        })

@login_required
@require_POST
def editar_receta(request, receta_id):
    """Editar receta existente"""
    try:
        receta = get_object_or_404(Receta, id=receta_id)
        producto = receta.producto
        data = request.POST
        
        # Actualizar datos básicos
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        categoria_id = data.get('categoria_id')
        tiempo_preparacion = data.get('tiempo_preparacion', 0)
        porciones = data.get('porciones', 1)
        instrucciones = data.get('instrucciones', '').strip()
        precio_venta = data.get('precio_venta', 0)
        
        if not nombre:
            return JsonResponse({
                'success': False,
                'message': 'El nombre de la receta es obligatorio'
            })
        
        # Actualizar producto
        producto.nombre = nombre
        producto.descripcion = descripcion
        producto.precio = Decimal(precio_venta)
        
        if categoria_id:
            try:
                categoria = CategoriaProducto.objects.get(id=categoria_id)
                producto.categoria = categoria
            except CategoriaProducto.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'La categoría seleccionada no existe'
                })
        
        producto.save()
        
        # Actualizar receta
        receta.tiempo_preparacion = int(tiempo_preparacion) if tiempo_preparacion else 0
        receta.porciones = int(porciones) if porciones else 1
        receta.instrucciones = instrucciones
        receta.save()
        
        # Eliminar ingredientes actuales
        RecetaInsumo.objects.filter(receta=receta).delete()
        
        # Procesar nuevos ingredientes
        insumo_ids = request.POST.getlist('ingrediente_insumo[]')
        cantidades = request.POST.getlist('ingrediente_cantidad[]')
        opcionales = request.POST.getlist('ingrediente_opcional[]')
        notas_list = request.POST.getlist('ingrediente_notas[]')
        
        costo_total = Decimal('0.00')
        
        for i, insumo_id in enumerate(insumo_ids):
            if insumo_id and cantidades[i]:
                try:
                    insumo = Insumo.objects.get(id=insumo_id)
                    cantidad = Decimal(cantidades[i])
                    es_opcional = i < len(opcionales) and opcionales[i] == 'on'
                    notas = notas_list[i] if i < len(notas_list) else ''
                    
                    RecetaInsumo.objects.create(
                        receta=receta,
                        insumo=insumo,
                        cantidad=cantidad,
                        opcional=es_opcional,
                        notas=notas,
                        orden=i+1
                    )
                    
                    costo_total += cantidad * insumo.precio_unitario
                except Insumo.DoesNotExist:
                    print(f"Insumo {insumo_id} no encontrado")
                except Exception as e:
                    print(f"Error al procesar ingrediente {i}: {e}")
        
        # Actualizar costo en el producto
        producto.costo = costo_total
        producto.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Receta actualizada correctamente'
        })
    except Receta.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Receta no encontrada'
        })
    except Exception as e:
        print(f"Error al actualizar receta: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al actualizar receta: {str(e)}'
        })

@login_required
@require_POST
def eliminar_receta(request, receta_id):
    """Eliminar receta"""
    try:
        receta = get_object_or_404(Receta, id=receta_id)
        
        # Guardar el producto asociado para eliminarlo después
        producto = receta.producto
        
        # Eliminar ingredientes
        RecetaInsumo.objects.filter(receta=receta).delete()
        
        # Eliminar receta
        receta.delete()
        
        # Eliminar producto asociado
        if producto:
            producto.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Receta eliminada correctamente'
        })
    except Receta.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Receta no encontrada'
        })
    except Exception as e:
        print(f"Error al eliminar receta: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar receta: {str(e)}'
        })

@login_required
@require_POST
def duplicar_receta(request, receta_id):
    """Duplicar receta"""
    try:
        receta_original = get_object_or_404(Receta, id=receta_id)
        producto_original = receta_original.producto
        
        # Crear copia del producto
        producto_nuevo = ProductoVenta.objects.create(
            nombre=f"Copia de {producto_original.nombre}",
            descripcion=producto_original.descripcion,
            codigo=f"REC{ProductoVenta.objects.count() + 1:04d}",
            precio=producto_original.precio,
            costo=producto_original.costo,
            tipo=producto_original.tipo,
            disponible=True,
            categoria=producto_original.categoria
        )
        
        # Crear copia de la receta
        receta_nueva = Receta.objects.create(
            producto=producto_nuevo,
            tiempo_preparacion=receta_original.tiempo_preparacion,
            porciones=receta_original.porciones,
            instrucciones=receta_original.instrucciones,
            activo=True
        )
        
        # Copiar ingredientes
        ingredientes_originales = RecetaInsumo.objects.filter(receta=receta_original)
        for ingrediente in ingredientes_originales:
            RecetaInsumo.objects.create(
                receta=receta_nueva,
                insumo=ingrediente.insumo,
                cantidad=ingrediente.cantidad,
                opcional=ingrediente.opcional,
                notas=ingrediente.notas,
                orden=ingrediente.orden
            )
        
        return JsonResponse({
            'success': True,
            'receta_id': receta_nueva.id,
            'message': 'Receta duplicada correctamente'
        })
    except Receta.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Receta no encontrada'
        })
    except Exception as e:
        print(f"Error al duplicar receta: {e}")
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
        print(f"Error al actualizar categoría: {e}")
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
        print(f"Error al eliminar categoría: {e}")
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
        print(f"Error obteniendo todos los insumos: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })
