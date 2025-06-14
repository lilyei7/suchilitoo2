from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal

from restaurant.models import (
    Insumo as RestaurantInsumo, CategoriaInsumo, UnidadMedida, 
    InsumoElaborado
)
from .base_views import get_sidebar_context, is_admin_or_manager

# Usamos el Insumo de restaurant para tener consistencia
Insumo = RestaurantInsumo

@login_required
def insumos_elaborados_view(request):
    """Vista principal de insumos elaborados con funcionalidad completa"""
    # Filtrar insumos elaborados con sus componentes
    insumos_elaborados = Insumo.objects.filter(
        tipo='elaborado'
    ).select_related(
        'categoria', 'unidad_medida'
    ).prefetch_related(
        'componentes_elaborados__insumo_componente__categoria',
        'componentes_elaborados__insumo_componente__unidad_medida'
    ).order_by('nombre')
    
    # Estadísticas
    total_elaborados = insumos_elaborados.count()
    elaborados_activos = insumos_elaborados.filter(activo=True).count()
    
    context = {
        'insumos_elaborados': insumos_elaborados,
        'total_elaborados': total_elaborados,
        'elaborados_activos': elaborados_activos,
        **get_sidebar_context('insumos_elaborados')
    }
    
    return render(request, 'dashboard/insumos_elaborados.html', context)

@login_required
@user_passes_test(is_admin_or_manager)
def crear_insumo_elaborado(request):
    """Vista para crear un nuevo insumo elaborado"""
    if request.method == 'POST':
        try:
            # Datos básicos del insumo elaborado
            codigo = request.POST.get('codigo')
            nombre = request.POST.get('nombre')
            categoria_id = request.POST.get('categoria_id')
            unidad_medida_id = request.POST.get('unidad_medida_id')
            cantidad_producida = request.POST.get('cantidad_producida')
            descripcion = request.POST.get('descripcion', '')
            tiempo_total_preparacion = request.POST.get('tiempo_total_preparacion', 0)
            
            # Validaciones
            if not all([nombre, categoria_id, unidad_medida_id, cantidad_producida]):
                return JsonResponse({
                    'success': False,
                    'message': 'Todos los campos obligatorios deben ser completados'
                })
            
            # Generar código automáticamente si no se proporciona
            if not codigo:
                numero = 1
                while True:
                    codigo = f'ELAB-{numero:03d}'
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
            
            # Obtener componentes del POST
            componentes_data = []
            insumo_ids = request.POST.getlist('componente_insumo[]')
            cantidades = request.POST.getlist('componente_cantidad[]')
            tiempos = request.POST.getlist('componente_tiempo[]')
            instrucciones_list = request.POST.getlist('componente_instrucciones[]')
            
            if len(insumo_ids) != len(cantidades):
                return JsonResponse({
                    'success': False,
                    'message': 'Error en los datos de componentes'
                })
              # Validar componentes
            total_costo = Decimal('0')
            for i, (insumo_id, cantidad) in enumerate(zip(insumo_ids, cantidades)):
                if not insumo_id or not cantidad:
                    continue
                
                try:
                    # Permitir tanto insumos básicos como compuestos para elaborados
                    insumo_componente = Insumo.objects.get(
                        id=insumo_id, 
                        tipo__in=['basico', 'compuesto'],
                        activo=True
                    )
                    cantidad_decimal = Decimal(str(cantidad))
                    tiempo_prep = int(tiempos[i]) if i < len(tiempos) and tiempos[i] else 0
                    instrucciones = instrucciones_list[i] if i < len(instrucciones_list) else ''
                    
                    if cantidad_decimal <= 0:
                        return JsonResponse({
                            'success': False,
                            'message': f'La cantidad para {insumo_componente.nombre} debe ser mayor a 0'
                        })
                    
                    # Calcular costo usando Decimal para evitar errores de tipo
                    costo_componente = cantidad_decimal * insumo_componente.precio_unitario
                    
                    componentes_data.append({
                        'insumo': insumo_componente,
                        'cantidad': cantidad_decimal,
                        'tiempo_preparacion': tiempo_prep,
                        'instrucciones': instrucciones,
                        'costo': costo_componente
                    })
                    
                    total_costo += costo_componente
                
                except Insumo.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': f'El insumo con ID {insumo_id} no existe o no está activo'
                    })
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'message': f'Cantidad inválida para el componente {i+1}'
                    })
            
            if not componentes_data:
                return JsonResponse({
                    'success': False,
                    'message': 'Debe agregar al menos un componente'
                })
            
            # Crear el insumo elaborado
            categoria = CategoriaInsumo.objects.get(id=categoria_id)
            unidad_medida = UnidadMedida.objects.get(id=unidad_medida_id)
            
            # Calcular precio unitario por unidad producida usando Decimal
            cantidad_producida_decimal = Decimal(str(cantidad_producida))
            precio_unitario = total_costo / cantidad_producida_decimal
            
            insumo_elaborado = Insumo.objects.create(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                categoria=categoria,
                unidad_medida=unidad_medida,
                tipo='elaborado',
                precio_unitario=precio_unitario,
                stock_minimo=Decimal('0'),  # Se iniciará en 0
                activo=True
            )
            
            # Crear los componentes
            for i, componente_data in enumerate(componentes_data):
                InsumoElaborado.objects.create(
                    insumo_elaborado=insumo_elaborado,
                    insumo_componente=componente_data['insumo'],
                    cantidad=componente_data['cantidad'],
                    orden=i + 1,
                    tiempo_preparacion_minutos=componente_data['tiempo_preparacion'],
                    instrucciones=componente_data['instrucciones']
                )
            
            return JsonResponse({
                'success': True,
                'message': f'Insumo elaborado "{nombre}" creado exitosamente',
                'insumo_id': insumo_elaborado.id,
                'codigo': codigo,
                'costo_total': float(total_costo),
                'precio_unitario': float(precio_unitario),
                'cantidad_producida': float(cantidad_producida)
            })
            
        except Exception as e:
            print(f"Error creando insumo elaborado: {e}")
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
def obtener_insumos_para_elaborados(request):
    """Vista para obtener insumos disponibles para elaborados"""
    try:
        # Obtener insumos básicos y compuestos activos
        insumos = Insumo.objects.filter(
            tipo__in=['basico', 'compuesto'], 
            activo=True
        ).select_related('categoria', 'unidad_medida').order_by('tipo', 'nombre')
        
        insumos_data = []
        total_basicos = 0
        total_compuestos = 0
        
        for insumo in insumos:
            insumos_data.append({
                'id': insumo.id,
                'codigo': insumo.codigo,
                'nombre': insumo.nombre,
                'tipo': insumo.tipo,
                'categoria_nombre': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
                'unidad_medida_nombre': str(insumo.unidad_medida) if insumo.unidad_medida else 'Sin unidad',
                'precio_unitario': float(insumo.precio_unitario)
            })
            
            if insumo.tipo == 'basico':
                total_basicos += 1
            elif insumo.tipo == 'compuesto':
                total_compuestos += 1
        
        print(f"📊 Insumos cargados: {total_basicos} básicos, {total_compuestos} compuestos")
        
        return JsonResponse({
            'success': True,
            'insumos': insumos_data,
            'total_basicos': total_basicos,
            'total_compuestos': total_compuestos,
            'total': len(insumos_data)
        })
        
    except Exception as e:
        print(f"Error obteniendo insumos para elaborados: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
def detalle_insumo_elaborado(request, insumo_id):
    """Vista para ver detalles de un insumo elaborado"""
    try:
        insumo = get_object_or_404(Insumo, id=insumo_id, tipo='elaborado')
        componentes = InsumoElaborado.objects.filter(
            insumo_elaborado=insumo
        ).select_related(
            'insumo_componente__categoria', 
            'insumo_componente__unidad_medida'
        ).order_by('orden')
        
        # Calcular estadísticas
        total_costo = sum(c.costo_total() for c in componentes)
        tiempo_total = sum(c.tiempo_preparacion_minutos for c in componentes)
        
        componentes_data = []
        for componente in componentes:
            componentes_data.append({
                'id': componente.id,
                'insumo_nombre': componente.insumo_componente.nombre,
                'insumo_codigo': componente.insumo_componente.codigo,
                'categoria': componente.insumo_componente.categoria.nombre if componente.insumo_componente.categoria else 'Sin categoría',
                'cantidad': float(componente.cantidad),
                'unidad_medida': str(componente.insumo_componente.unidad_medida),                'precio_unitario': float(componente.insumo_componente.precio_unitario),
                'costo_total': float(componente.costo_total()),
                'tiempo_preparacion': componente.tiempo_preparacion_minutos,
                'instrucciones': componente.instrucciones,
                'orden': componente.orden
            })
        
        insumo_data = {
            'id': insumo.id,
            'codigo': insumo.codigo,
            'nombre': insumo.nombre,
            'descripcion': insumo.descripcion,
            'categoria': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
            'unidad_medida': str(insumo.unidad_medida),
            'precio_unitario': float(insumo.precio_unitario),
            'stock_minimo': float(insumo.stock_minimo),  # Cambiado de cantidad_stock
            'activo': insumo.activo,
            'total_costo': float(total_costo),
            'tiempo_total_preparacion': tiempo_total,
            'cantidad_componentes': len(componentes_data)
        }
        
        return JsonResponse({
            'success': True,
            'insumo': insumo_data,
            'componentes': componentes_data
        })
        
    except Exception as e:
        print(f"Error obteniendo detalle de insumo elaborado: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def editar_insumo_elaborado(request, insumo_id):
    """Vista para editar un insumo elaborado"""
    if request.method == 'POST':
        try:
            insumo = get_object_or_404(Insumo, id=insumo_id, tipo='elaborado')
            
            # Actualizar datos básicos
            insumo.nombre = request.POST.get('nombre', insumo.nombre)
            insumo.descripcion = request.POST.get('descripcion', insumo.descripcion)
            
            categoria_id = request.POST.get('categoria_id')
            if categoria_id:
                insumo.categoria = CategoriaInsumo.objects.get(id=categoria_id)
            
            unidad_medida_id = request.POST.get('unidad_medida_id')
            if unidad_medida_id:
                insumo.unidad_medida = UnidadMedida.objects.get(id=unidad_medida_id)
            
            # Obtener nuevos componentes
            insumo_ids = request.POST.getlist('componente_insumo[]')
            cantidades = request.POST.getlist('componente_cantidad[]')
            tiempos = request.POST.getlist('componente_tiempo[]')
            instrucciones_list = request.POST.getlist('componente_instrucciones[]')
            
            # Eliminar componentes existentes
            InsumoElaborado.objects.filter(insumo_elaborado=insumo).delete()
              # Crear nuevos componentes
            total_costo = Decimal('0')
            cantidad_producida = Decimal(str(request.POST.get('cantidad_producida', 1)))
            
            for i, (insumo_id_comp, cantidad) in enumerate(zip(insumo_ids, cantidades)):
                if not insumo_id_comp or not cantidad:
                    continue
                
                insumo_componente = Insumo.objects.get(
                    id=insumo_id_comp, 
                    tipo__in=['basico', 'compuesto']
                )
                cantidad_decimal = Decimal(str(cantidad))
                tiempo_prep = int(tiempos[i]) if i < len(tiempos) and tiempos[i] else 0
                instrucciones = instrucciones_list[i] if i < len(instrucciones_list) else ''
                
                InsumoElaborado.objects.create(
                    insumo_elaborado=insumo,
                    insumo_componente=insumo_componente,
                    cantidad=cantidad_decimal,
                    orden=i + 1,
                    tiempo_preparacion_minutos=tiempo_prep,
                    instrucciones=instrucciones
                )
                
                total_costo += cantidad_decimal * insumo_componente.precio_unitario
            
            # Actualizar precio unitario
            insumo.precio_unitario = total_costo / cantidad_producida
            insumo.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Insumo elaborado "{insumo.nombre}" actualizado exitosamente'
            })
            
        except Exception as e:
            print(f"Error editando insumo elaborado: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            })
    
    # Si es GET, devolver datos para edición
    try:
        return detalle_insumo_elaborado(request, insumo_id)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error cargando datos: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def eliminar_insumo_elaborado(request, insumo_id):
    """Vista para eliminar un insumo elaborado"""
    if request.method == 'POST':
        try:
            insumo = get_object_or_404(Insumo, id=insumo_id, tipo='elaborado')
            nombre = insumo.nombre
            
            # Eliminar componentes primero
            InsumoElaborado.objects.filter(insumo_elaborado=insumo).delete()
            
            # Eliminar el insumo
            insumo.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Insumo elaborado "{nombre}" eliminado exitosamente'
            })
            
        except Exception as e:
            print(f"Error eliminando insumo elaborado: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })
