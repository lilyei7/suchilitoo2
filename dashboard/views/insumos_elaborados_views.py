from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal
import traceback
import traceback

from restaurant.models import (
    Insumo, CategoriaInsumo, UnidadMedida, InsumoCompuesto
)
from dashboard.views import get_sidebar_context, is_admin_or_manager
from dashboard.utils.permissions import require_submodule_access

@login_required
@require_submodule_access('inventario', 'elaborados')
def insumos_elaborados_view(request):
    """Vista principal de insumos elaborados con funcionalidad completa"""    # Filtrar insumos elaborados con sus componentes
    insumos_elaborados = Insumo.objects.filter(
        tipo='elaborado'
    ).select_related(
        'categoria', 'unidad_medida'
    ).prefetch_related(
        'componentes__insumo_componente__categoria',
        'componentes__insumo_componente__unidad_medida'
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
@login_required
@require_submodule_access('inventario', 'elaborados')
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
                        tipo__in=['basico', 'compuesto', 'elaborado'],
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
                InsumoCompuesto.objects.create(
                    insumo_compuesto=insumo_elaborado,
                    insumo_componente=componente_data['insumo'],
                    cantidad=componente_data['cantidad'],
                    notas=''
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
@login_required
@require_submodule_access('inventario', 'elaborados')
def obtener_insumos_para_elaborados(request):
    """Vista para obtener insumos disponibles para elaborados"""
    try:
        # Obtener insumos básicos, compuestos y elaborados activos
        insumos = Insumo.objects.filter(
            tipo__in=['basico', 'compuesto', 'elaborado'],
            activo=True
        ).select_related('categoria', 'unidad_medida').order_by('tipo', 'nombre')

        insumos_data = []
        total_basicos = 0
        total_compuestos = 0
        total_elaborados = 0

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
            elif insumo.tipo == 'elaborado':
                total_elaborados += 1

        print(f"📊 Insumos cargados: {total_basicos} básicos, {total_compuestos} compuestos, {total_elaborados} elaborados")

        return JsonResponse({
            'success': True,
            'insumos': insumos_data,
            'total_basicos': total_basicos,
            'total_compuestos': total_compuestos,
            'total_elaborados': total_elaborados,
            'total': len(insumos_data)
        })

    except Exception as e:
        print(f"Error obteniendo insumos para elaborados: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@require_submodule_access('inventario', 'elaborados')
def detalle_insumo_elaborado(request, insumo_id):
    """Vista para ver detalles de un insumo elaborado"""
    try:
        # Obtener insumo elaborado según modelo Insumo
        insumo = get_object_or_404(Insumo, id=insumo_id, tipo='elaborado')
        
        # Obtener componentes según modelo InsumoCompuesto
        componentes = InsumoCompuesto.objects.filter(
            insumo_compuesto=insumo
        ).select_related(
            'insumo_componente',
            'insumo_componente__categoria',
            'insumo_componente__unidad_medida'
        )
        
        # Calcular costo total usando los campos del modelo
        costo_total = Decimal('0.00')
        componentes_data = []
        
        for componente in componentes:
            # Usar los campos del modelo para los cálculos
            cantidad = componente.cantidad or Decimal('0')
            precio_unitario = componente.insumo_componente.precio_unitario or Decimal('0')
            costo_componente = cantidad * precio_unitario
            costo_total += costo_componente
            
            componentes_data.append({
                'id': componente.id,
                'insumo_id': componente.insumo_componente.id,
                'insumo_nombre': componente.insumo_componente.nombre,
                'codigo': componente.insumo_componente.codigo,
                'tipo': componente.insumo_componente.tipo,
                'categoria': componente.insumo_componente.categoria.nombre if componente.insumo_componente.categoria else 'Sin categoría',
                'unidad_medida': str(componente.insumo_componente.unidad_medida) if componente.insumo_componente.unidad_medida else '',
                'unidad_abrev': componente.insumo_componente.unidad_medida.abreviacion if componente.insumo_componente.unidad_medida else '',
                'cantidad': float(cantidad),
                'precio_unitario': float(precio_unitario),
                'costo_total': float(costo_componente),
                'notas': componente.notas or ''
            })
        
        # Actualizar el costo de producción en la base de datos
        if costo_total > 0:
            insumo.costo_produccion = costo_total
            insumo.save(update_fields=['costo_produccion', 'fecha_actualizacion'])
        
        # Retornar los datos basados directamente en los campos del modelo
        return JsonResponse({
            'success': True,
            'insumo': {
                'id': insumo.id,
                'codigo': insumo.codigo,
                'nombre': insumo.nombre,
                'descripcion': insumo.descripcion or '',
                'categoria': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
                'categoria_id': insumo.categoria.id if insumo.categoria else None,
                'unidad_medida': str(insumo.unidad_medida) if insumo.unidad_medida else 'Sin unidad',
                'unidad_medida_id': insumo.unidad_medida.id if insumo.unidad_medida else None,                'precio_unitario': float(insumo.precio_unitario) if insumo.precio_unitario is not None else 0.0,
                'stock_minimo': float(insumo.stock_minimo) if insumo.stock_minimo is not None else 0.0,
                'stock_actual': float(insumo.stock_actual) if insumo.stock_actual is not None else 0.0,
                'activo': insumo.activo,
                'perecedero': insumo.perecedero,
                'dias_vencimiento': insumo.dias_vencimiento,
                'cantidad_producida': float(insumo.cantidad_producida) if insumo.cantidad_producida is not None else 1.0,
                'tiempo_preparacion': insumo.tiempo_preparacion or 0,
                'costo_produccion': float(insumo.costo_produccion) if insumo.costo_produccion is not None else 0.0,
                'fecha_creacion': insumo.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
                'fecha_actualizacion': insumo.fecha_actualizacion.strftime('%Y-%m-%d %H:%M:%S'),
                'total_costo': float(costo_total),
                'cantidad_componentes': len(componentes_data)
            },
            'componentes': componentes_data
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@require_submodule_access('inventario', 'elaborados')
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
            
            # Actualizar campos específicos para insumos elaborados
            try:
                cantidad_producida = Decimal(str(request.POST.get('cantidad_producida', '1')))
                if cantidad_producida <= 0:
                    cantidad_producida = Decimal('1')
            except:
                cantidad_producida = Decimal('1')
                
            try:
                tiempo_preparacion = int(request.POST.get('tiempo_preparacion', '0'))
                if tiempo_preparacion < 0:
                    tiempo_preparacion = 0
            except:
                tiempo_preparacion = 0
                
            insumo.cantidad_producida = cantidad_producida
            insumo.tiempo_preparacion = tiempo_preparacion
            
            # Eliminar componentes existentes
            InsumoCompuesto.objects.filter(insumo_compuesto=insumo).delete()
            
            # Crear nuevos componentes
            total_costo = Decimal('0')
            
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
                InsumoCompuesto.objects.create(
                    insumo_compuesto=insumo,
                    insumo_componente=insumo_componente,
                    cantidad=cantidad_decimal,
                    notas=instrucciones
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
@require_submodule_access('inventario', 'elaborados')
def eliminar_insumo_elaborado(request, insumo_id):
    """Vista para eliminar un insumo elaborado"""
    if request.method == 'POST':
        try:
            insumo = get_object_or_404(Insumo, id=insumo_id, tipo='elaborado')
            nombre = insumo.nombre
            
            # Verificar si este insumo es usado como componente en otros insumos
            usado_en_compuestos = False
            try:
                usado_en_compuestos = insumo.usado_en.exists()
            except:
                pass
                
            # Verificar si este insumo es usado en recetas
            usado_en_recetas = False
            try:
                from restaurant.models import RecetaInsumo
                usado_en_recetas = RecetaInsumo.objects.filter(insumo=insumo).exists()
            except ImportError:
                # Si no podemos importar RecetaInsumo, asumimos que no se usa
                pass
                
            if usado_en_compuestos or usado_en_recetas:
                return JsonResponse({
                    'success': False,
                    'message': f'No se puede eliminar el insumo "{nombre}" porque está siendo utilizado en '
                              + ('insumos compuestos y ' if usado_en_compuestos else '')
                              + ('recetas' if usado_en_recetas else ''),
                    'tipo_error': 'dependencia'
                })
            
            # Si llegamos aquí, podemos proceder con la eliminación
            # Primero eliminar componentes (relaciones)
            InsumoCompuesto.objects.filter(insumo_compuesto=insumo).delete()
            
            # Luego eliminar el insumo
            try:
                insumo.delete()
                return JsonResponse({
                    'success': True,
                    'message': f'Insumo elaborado "{nombre}" eliminado exitosamente'
                })
            except Exception as delete_error:
                # Si falla la eliminación por alguna restricción de base de datos no detectada antes
                print(f"Error al eliminar insumo elaborado: {delete_error}. Marcando como inactivo.")
                insumo.activo = False
                insumo.save()
                return JsonResponse({
                    'success': True,
                    'message': f'No se pudo eliminar completamente el insumo "{nombre}" debido a dependencias. Ha sido marcado como inactivo.',
                    'was_deactivated': True
                })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error eliminando insumo elaborado: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}',
                'tipo_error': 'sistema'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })
