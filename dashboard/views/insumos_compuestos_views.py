from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse

from restaurant.models import (
    Insumo as RestaurantInsumo, CategoriaInsumo, UnidadMedida, 
    InsumoCompuesto
)
from .base_views import get_sidebar_context, is_admin_or_manager

# Usamos el Insumo de restaurant para tener consistencia
Insumo = RestaurantInsumo

@login_required
def insumos_compuestos_view(request):
    """Vista principal para insumos compuestos"""
    # Obtener insumos compuestos
    insumos_compuestos = Insumo.objects.filter(
        tipo='compuesto'
    ).select_related(
        'categoria', 'unidad_medida'
    ).prefetch_related(
        'componentes__insumo_componente'
    ).order_by('nombre')
    
    # Estadísticas
    total_compuestos = insumos_compuestos.count()
    compuestos_activos = insumos_compuestos.filter(activo=True).count()
    
    context = {
        'insumos_compuestos': insumos_compuestos,
        'total_compuestos': total_compuestos,
        'compuestos_activos': compuestos_activos,
        **get_sidebar_context('insumos_compuestos')
    }
    
    return render(request, 'dashboard/insumos_compuestos.html', context)

@login_required
@user_passes_test(is_admin_or_manager)
def crear_insumo_compuesto(request):
    """Vista para crear un insumo compuesto"""
    if request.method == 'POST':
        try:
            # Datos básicos
            codigo = request.POST.get('codigo')
            nombre = request.POST.get('nombre')
            categoria_id = request.POST.get('categoria_id')
            unidad_medida_id = request.POST.get('unidad_medida_id')
            descripcion = request.POST.get('descripcion', '')
            
            # Validaciones básicas
            if not all([nombre, categoria_id, unidad_medida_id]):
                return JsonResponse({
                    'success': False,
                    'message': 'Faltan campos obligatorios'
                })
            
            # Generar código automáticamente si no se proporciona
            if not codigo:
                numero = 1
                while True:
                    codigo = f'COMP-{numero:03d}'
                    if not Insumo.objects.filter(codigo=codigo).exists():
                        break
                    numero += 1
                    if numero > 9999:
                        return JsonResponse({
                            'success': False,
                            'message': 'No se pudo generar un código único'
                        })
            else:
                # Verificar que el código proporcionado no exista
                if Insumo.objects.filter(codigo=codigo).exists():
                    return JsonResponse({
                        'success': False,
                        'message': f'Ya existe un insumo con el código "{codigo}"'
                    })
            
            # Obtener componentes
            insumo_ids = request.POST.getlist('componente_insumo[]')
            cantidades = request.POST.getlist('componente_cantidad[]')
            
            if len(insumo_ids) != len(cantidades):
                return JsonResponse({
                    'success': False,
                    'message': 'Error en los datos de componentes'
                })
            
            # Validar componentes y calcular costo total
            componentes_data = []
            costo_total = 0
            
            for i, (insumo_id, cantidad) in enumerate(zip(insumo_ids, cantidades)):
                if not insumo_id or not cantidad:
                    continue
                
                try:
                    # Solo se permiten insumos básicos en compuestos
                    insumo_componente = Insumo.objects.get(
                        id=insumo_id, 
                        tipo='basico',
                        activo=True
                    )
                    
                    try:
                        cantidad_float = float(cantidad)
                    except ValueError:
                        return JsonResponse({
                            'success': False,
                            'message': f'Cantidad inválida para el componente {i+1}'
                        })
                    
                    if cantidad_float <= 0:
                        return JsonResponse({
                            'success': False,
                            'message': f'La cantidad para {insumo_componente.nombre} debe ser mayor a 0'
                        })
                    
                    # Calcular costo
                    costo_componente = cantidad_float * float(insumo_componente.precio_unitario)
                    costo_total += costo_componente
                    
                    componentes_data.append({
                        'insumo': insumo_componente,
                        'cantidad': cantidad_float
                    })
                    
                except Insumo.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': f'El insumo básico con ID {insumo_id} no existe o no está activo'
                    })
            
            if not componentes_data:
                return JsonResponse({
                    'success': False,
                    'message': 'Debe agregar al menos un componente'
                })
            
            # Crear el insumo compuesto
            categoria = CategoriaInsumo.objects.get(id=categoria_id)
            unidad_medida = UnidadMedida.objects.get(id=unidad_medida_id)
            
            # Obtener rendimiento/cantidad producida
            cantidad_producida = float(request.POST.get('cantidad_producida', 1))
            
            # Calcular precio unitario
            precio_unitario = costo_total / cantidad_producida if cantidad_producida > 0 else costo_total
            
            # Crear el insumo compuesto
            insumo_compuesto = Insumo.objects.create(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                categoria=categoria,
                unidad_medida=unidad_medida,
                tipo='compuesto',
                precio_unitario=precio_unitario,
                stock_minimo=0,
                activo=True
            )
            
            # Crear componentes
            for i, componente in enumerate(componentes_data):
                InsumoCompuesto.objects.create(
                    insumo_compuesto=insumo_compuesto,
                    insumo_componente=componente['insumo'],
                    cantidad=componente['cantidad'],
                    orden=i+1
                )
            
            return JsonResponse({
                'success': True,
                'message': f'Insumo compuesto "{nombre}" creado exitosamente',
                'insumo_id': insumo_compuesto.id
            })
            
        except Exception as e:
            print(f"Error creando insumo compuesto: {e}")
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
def detalle_insumo_compuesto(request, insumo_id):
    """Vista para ver detalles de un insumo compuesto"""
    try:
        insumo = get_object_or_404(Insumo, id=insumo_id, tipo='compuesto')
        
        # Obtener componentes
        componentes = InsumoCompuesto.objects.filter(
            insumo_compuesto=insumo
        ).select_related(
            'insumo_componente__categoria', 
            'insumo_componente__unidad_medida'
        ).order_by('orden')
        
        # Calcular costo total
        costo_total = 0
        componentes_data = []
        
        for componente in componentes:
            costo_componente = float(componente.cantidad) * float(componente.insumo_componente.precio_unitario)
            costo_total += costo_componente
            
            componentes_data.append({
                'id': componente.id,
                'insumo_id': componente.insumo_componente.id,
                'insumo_nombre': componente.insumo_componente.nombre,
                'insumo_codigo': componente.insumo_componente.codigo,
                'categoria': componente.insumo_componente.categoria.nombre if componente.insumo_componente.categoria else 'Sin categoría',
                'cantidad': float(componente.cantidad),
                'unidad_medida': str(componente.insumo_componente.unidad_medida) if componente.insumo_componente.unidad_medida else '',
                'unidad_abrev': componente.insumo_componente.unidad_medida.abreviacion if componente.insumo_componente.unidad_medida else '',
                'precio_unitario': float(componente.insumo_componente.precio_unitario),
                'costo': costo_componente
            })
        
        # Datos del insumo
        insumo_data = {
            'id': insumo.id,
            'codigo': insumo.codigo,
            'nombre': insumo.nombre,
            'descripcion': insumo.descripcion,
            'categoria_id': insumo.categoria.id if insumo.categoria else None,
            'categoria_nombre': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
            'unidad_medida_id': insumo.unidad_medida.id if insumo.unidad_medida else None,
            'unidad_medida_nombre': str(insumo.unidad_medida) if insumo.unidad_medida else 'Sin unidad',
            'precio_unitario': float(insumo.precio_unitario),
            'activo': insumo.activo,
            'costo_total': costo_total,
            'cantidad_componentes': len(componentes_data)
        }
        
        return JsonResponse({
            'success': True,
            'insumo': insumo_data,
            'componentes': componentes_data
        })
        
    except Exception as e:
        print(f"Error obteniendo detalle de insumo compuesto: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def editar_insumo_compuesto(request, insumo_id):
    """Vista para editar un insumo compuesto"""
    if request.method == 'POST':
        try:
            insumo = get_object_or_404(Insumo, id=insumo_id, tipo='compuesto')
            
            # Actualizar datos básicos
            insumo.nombre = request.POST.get('nombre', insumo.nombre)
            insumo.descripcion = request.POST.get('descripcion', insumo.descripcion)
            
            categoria_id = request.POST.get('categoria_id')
            if categoria_id:
                insumo.categoria = CategoriaInsumo.objects.get(id=categoria_id)
            
            unidad_medida_id = request.POST.get('unidad_medida_id')
            if unidad_medida_id:
                insumo.unidad_medida = UnidadMedida.objects.get(id=unidad_medida_id)
            
            # Obtener componentes actualizados
            insumo_ids = request.POST.getlist('componente_insumo[]')
            cantidades = request.POST.getlist('componente_cantidad[]')
            
            # Eliminar componentes actuales
            InsumoCompuesto.objects.filter(insumo_compuesto=insumo).delete()
            
            # Validar y crear nuevos componentes
            costo_total = 0
            cantidad_producida = float(request.POST.get('cantidad_producida', 1))
            
            for i, (insumo_id_comp, cantidad) in enumerate(zip(insumo_ids, cantidades)):
                if not insumo_id_comp or not cantidad:
                    continue
                
                insumo_componente = Insumo.objects.get(id=insumo_id_comp, tipo='basico')
                cantidad_float = float(cantidad)
                costo_componente = cantidad_float * float(insumo_componente.precio_unitario)
                costo_total += costo_componente
                
                InsumoCompuesto.objects.create(
                    insumo_compuesto=insumo,
                    insumo_componente=insumo_componente,
                    cantidad=cantidad_float,
                    orden=i+1
                )
            
            # Actualizar precio unitario
            insumo.precio_unitario = costo_total / cantidad_producida if cantidad_producida > 0 else costo_total
            insumo.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Insumo compuesto "{insumo.nombre}" actualizado exitosamente'
            })
            
        except Exception as e:
            print(f"Error editando insumo compuesto: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            })
    
    # Si es GET, devolver datos para edición
    try:
        return detalle_insumo_compuesto(request, insumo_id)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error cargando datos: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def eliminar_insumo_compuesto(request, insumo_id):
    """Vista para eliminar un insumo compuesto"""
    if request.method == 'POST':
        try:
            insumo = get_object_or_404(Insumo, id=insumo_id, tipo='compuesto')
            nombre = insumo.nombre
            
            # Eliminar componentes
            InsumoCompuesto.objects.filter(insumo_compuesto=insumo).delete()
            
            # Eliminar insumo
            insumo.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Insumo compuesto "{nombre}" eliminado exitosamente'
            })
            
        except Exception as e:
            print(f"Error eliminando insumo compuesto: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })
