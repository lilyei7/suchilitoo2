from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from decimal import Decimal

from restaurant.models import Insumo, CategoriaInsumo, UnidadMedida, Inventario
from dashboard.views.base_views import is_admin_or_manager
from dashboard.utils.permissions import require_submodule_access

@login_required
@require_submodule_access('inventario', 'insumos')
def crear_insumo(request):
    """Vista para crear un nuevo insumo básico"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            codigo = request.POST.get('codigo', '').strip()
            nombre = request.POST.get('nombre', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            categoria_id = request.POST.get('categoria')
            unidad_medida_id = request.POST.get('unidad_medida')
            stock_minimo = request.POST.get('stock_minimo', '0')
            precio_unitario = request.POST.get('precio_unitario', '0')
            tipo = request.POST.get('tipo', 'basico')
            perecedero = request.POST.get('perecedero') == 'on'
            dias_vencimiento = request.POST.get('dias_vencimiento', '')
            
            # Validaciones básicas
            if not nombre:
                return JsonResponse({
                    'success': False,
                    'error': 'El nombre del insumo es obligatorio'
                })
            
            if not categoria_id:
                return JsonResponse({
                    'success': False,
                    'error': 'La categoría es obligatoria'
                })
            
            if not unidad_medida_id:
                return JsonResponse({
                    'success': False,
                    'error': 'La unidad de medida es obligatoria'
                })
            
            # Generar código si no se proporciona
            if not codigo:
                import time
                codigo = f"{nombre[:3].upper()}-{int(time.time())}"
            
            # Verificar que el código no exista
            if Insumo.objects.filter(codigo=codigo).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'El código "{codigo}" ya existe'
                })
            
            # Obtener objetos relacionados
            categoria = get_object_or_404(CategoriaInsumo, id=categoria_id)
            unidad_medida = get_object_or_404(UnidadMedida, id=unidad_medida_id)
              # Crear el insumo
            insumo = Insumo.objects.create(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                categoria=categoria,
                unidad_medida=unidad_medida,
                stock_minimo=Decimal(stock_minimo) if stock_minimo else Decimal('0'),
                precio_unitario=Decimal(precio_unitario) if precio_unitario else Decimal('0'),
                tipo=tipo,
                perecedero=perecedero,
                dias_vencimiento=int(dias_vencimiento) if dias_vencimiento and perecedero else None,
                activo=True
            )
              # Crear registros de inventario en todas las sucursales activas
            from accounts.models import Sucursal
            sucursales_activas = Sucursal.objects.filter(activa=True)
            inventarios_creados = 0
            
            for sucursal in sucursales_activas:
                try:
                    Inventario.objects.create(
                        insumo=insumo,
                        sucursal=sucursal,
                        cantidad_actual=Decimal('0.00'),
                        cantidad_reservada=Decimal('0.00'),
                        costo_unitario=insumo.precio_unitario
                    )
                    inventarios_creados += 1
                except Exception as e:
                    print(f"Error creando inventario para {sucursal.nombre}: {e}")
            
            print(f"✅ Insumo '{insumo.nombre}' creado con {inventarios_creados} registros de inventario")
            
            return JsonResponse({
                'success': True,
                'message': f'Insumo "{insumo.nombre}" creado exitosamente con inventario en {inventarios_creados} sucursal(es)',
                'insumo': {
                    'id': insumo.id,
                    'codigo': insumo.codigo,
                    'nombre': insumo.nombre
                }
            })
            
        except Exception as e:
            print(f"Error creando insumo: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })

@login_required
@require_submodule_access('inventario', 'insumos')
def detalle_insumo(request, insumo_id):
    """Vista para obtener detalles de un insumo"""
    try:
        insumo = get_object_or_404(Insumo, id=insumo_id)
        
        return JsonResponse({
            'success': True,
            'id': insumo.id,
            'codigo': insumo.codigo,
            'nombre': insumo.nombre,
            'descripcion': insumo.descripcion or '',
            'categoria': insumo.categoria.id if insumo.categoria else None,
            'categoria_nombre': insumo.categoria.nombre if insumo.categoria else '',
            'unidad_medida': insumo.unidad_medida.id if insumo.unidad_medida else None,
            'unidad_medida_nombre': str(insumo.unidad_medida) if insumo.unidad_medida else '',
            'stock_minimo': float(insumo.stock_minimo),
            'precio_unitario': float(insumo.precio_unitario),
            'tipo': insumo.tipo,
            'perecedero': insumo.perecedero,
            'dias_vencimiento': insumo.dias_vencimiento,
            'activo': insumo.activo
        })
        
    except Exception as e:
        print(f"Error obteniendo detalle de insumo: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
@login_required
@require_submodule_access('inventario', 'insumos')
def editar_insumo(request, insumo_id):
    """Vista para editar un insumo"""
    if request.method == 'POST':
        try:
            insumo = get_object_or_404(Insumo, id=insumo_id)
            
            # Actualizar campos
            nombre = request.POST.get('nombre', '').strip()
            if nombre:
                insumo.nombre = nombre
            
            descripcion = request.POST.get('descripcion', '').strip()
            insumo.descripcion = descripcion
            
            categoria_id = request.POST.get('categoria')
            if categoria_id:
                insumo.categoria = get_object_or_404(CategoriaInsumo, id=categoria_id)
            
            unidad_medida_id = request.POST.get('unidad_medida')
            if unidad_medida_id:
                insumo.unidad_medida = get_object_or_404(UnidadMedida, id=unidad_medida_id)
            
            stock_minimo = request.POST.get('stock_minimo')
            if stock_minimo:
                insumo.stock_minimo = Decimal(stock_minimo)
            
            precio_unitario = request.POST.get('precio_unitario')
            if precio_unitario:
                insumo.precio_unitario = Decimal(precio_unitario)
            
            perecedero = request.POST.get('perecedero') == 'on'
            insumo.perecedero = perecedero
            
            dias_vencimiento = request.POST.get('dias_vencimiento', '')
            if perecedero and dias_vencimiento:
                insumo.dias_vencimiento = int(dias_vencimiento)
            else:
                insumo.dias_vencimiento = None
            
            insumo.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Insumo "{insumo.nombre}" actualizado exitosamente'
            })
            
        except Exception as e:
            print(f"Error editando insumo: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            })
    
    # Si es GET, devolver los datos del insumo para edición
    return detalle_insumo(request, insumo_id)

@login_required
@require_submodule_access('inventario', 'insumos')
def eliminar_insumo(request, insumo_id):
    """Vista para eliminar un insumo"""
    if request.method == 'POST':
        try:
            insumo = get_object_or_404(Insumo, id=insumo_id)
            nombre = insumo.nombre
            
            # Verificar si este insumo es usado como componente en insumos compuestos
            usado_en_compuestos = False
            try:
                usado_en_compuestos = insumo.usado_en.exists()
            except:
                pass
                
            # Verificar si este insumo es usado en recetas
            usado_en_recetas = False
            try:
                usado_en_recetas = insumo.usado_en_recetas.exists()
            except:
                pass
                
            if usado_en_compuestos or usado_en_recetas:
                # En lugar de intentar eliminarlo, lo marcamos como inactivo
                insumo.activo = False
                insumo.save()
                
                mensaje = f'El insumo "{nombre}" no puede ser eliminado completamente porque está siendo utilizado en '
                if usado_en_compuestos and usado_en_recetas:
                    mensaje += 'insumos compuestos y recetas.'
                elif usado_en_compuestos:
                    mensaje += 'insumos compuestos.'
                else:
                    mensaje += 'recetas.'
                    
                mensaje += ' Ha sido marcado como inactivo en su lugar.'
                
                return JsonResponse({
                    'success': True,
                    'message': mensaje,
                    'was_deactivated': True
                })
            
            # Si no tiene dependencias, intentamos eliminarlo completamente
            try:
                insumo.delete()
                return JsonResponse({
                    'success': True,
                    'message': f'Insumo "{nombre}" eliminado exitosamente'
                })
            except Exception as delete_error:
                # Si falla la eliminación por alguna restricción de base de datos no detectada antes
                print(f"Error al eliminar insumo: {delete_error}. Marcando como inactivo.")
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
            print(f"Error eliminando insumo: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })

@login_required
@require_submodule_access('inventario', 'insumos')
def obtener_insumos_basicos(request):
    """API para obtener insumos básicos disponibles para insumos compuestos"""
    try:
        # Obtener insumos básicos activos
        insumos_basicos = Insumo.objects.filter(
            tipo='basico', 
            activo=True
        ).select_related('categoria', 'unidad_medida').order_by('nombre')
        
        insumos_data = []
        for insumo in insumos_basicos:
            insumos_data.append({
                'id': insumo.id,
                'codigo': insumo.codigo,
                'nombre': insumo.nombre,
                'categoria': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
                'unidad_medida': str(insumo.unidad_medida) if insumo.unidad_medida else 'Sin unidad',
                'precio_unitario': float(insumo.precio_unitario),
                'stock_actual': float(insumo.stock_actual) if hasattr(insumo, 'stock_actual') else 0,
                'activo': insumo.activo
            })
        
        return JsonResponse({
            'success': True,
            'insumos': insumos_data,
            'total': len(insumos_data)
        })
        
    except Exception as e:
        print(f"Error obteniendo insumos básicos: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })
