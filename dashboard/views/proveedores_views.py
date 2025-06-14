from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Avg

from dashboard.models import Proveedor, ProveedorInsumo
from restaurant.models import Insumo as RestaurantInsumo
from .base_views import get_sidebar_context

# Usamos el Insumo de restaurant para tener consistencia
Insumo = RestaurantInsumo

@login_required
def proveedores_view(request):
    """Vista principal para gestión de proveedores"""
    # Obtener todos los proveedores
    proveedores = Proveedor.objects.all().order_by('nombre_comercial')
    
    # Estadísticas
    total_proveedores = proveedores.count()
    proveedores_activos = proveedores.filter(estado='activo').count()
    
    context = {
        'proveedores': proveedores,
        'total_proveedores': total_proveedores,
        'proveedores_activos': proveedores_activos,
        **get_sidebar_context('proveedores')
    }
    
    return render(request, 'dashboard/proveedores.html', context)

@login_required
def crear_proveedor(request):
    """Vista para crear un nuevo proveedor"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre_comercial = request.POST.get('nombre_comercial', '').strip()
            razon_social = request.POST.get('razon_social', '').strip()
            rfc = request.POST.get('rfc', '').strip()
            persona_contacto = request.POST.get('persona_contacto', '').strip()
            telefono = request.POST.get('telefono', '').strip()
            email = request.POST.get('email', '').strip()
            forma_pago_preferida = request.POST.get('forma_pago_preferida', 'transferencia')
            dias_credito = int(request.POST.get('dias_credito', '0'))
            direccion = request.POST.get('direccion', '').strip()
            ciudad_estado = request.POST.get('ciudad_estado', '').strip()
            categoria_productos = request.POST.get('categoria_productos', 'ingredientes')
            notas_adicionales = request.POST.get('notas_adicionales', '').strip()
            
            # Validaciones básicas
            if not all([nombre_comercial, telefono]):
                return JsonResponse({
                    'success': False,
                    'message': 'El nombre comercial y teléfono son obligatorios'
                })
            
            # Crear el proveedor
            proveedor = Proveedor.objects.create(
                nombre_comercial=nombre_comercial,
                razon_social=razon_social,
                rfc=rfc,
                persona_contacto=persona_contacto,
                telefono=telefono,
                email=email,
                forma_pago_preferida=forma_pago_preferida,
                dias_credito=dias_credito,
                direccion=direccion,
                ciudad_estado=ciudad_estado,
                categoria_productos=categoria_productos,
                notas_adicionales=notas_adicionales,
                estado='activo'
            )
            
            # Devolver respuesta según el tipo de solicitud
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Proveedor "{nombre_comercial}" creado exitosamente',
                    'proveedor_id': proveedor.id
                })
            else:
                messages.success(request, f'Proveedor "{nombre_comercial}" creado exitosamente')
                return redirect('dashboard:proveedores')
                
        except Exception as e:
            print(f"Error creando proveedor: {e}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error: {str(e)}'
                })
            else:
                messages.error(request, f'Error: {str(e)}')
                return redirect('dashboard:proveedores')
    
    # Si es GET, mostrar formulario
    context = {
        'titulo': 'Crear Proveedor',
        **get_sidebar_context('proveedores')
    }
    
    return render(request, 'dashboard/crear_proveedor.html', context)

@login_required
def detalle_proveedor(request, proveedor_id):
    """Vista para ver detalles completos de un proveedor"""
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    
    # Obtener insumos del proveedor
    insumos_proveedor = ProveedorInsumo.objects.filter(
        proveedor=proveedor, 
        activo=True
    ).select_related('insumo', 'insumo__categoria', 'insumo__unidad_medida')
    
    # Estadísticas del proveedor
    total_insumos = insumos_proveedor.count()
    precio_promedio = insumos_proveedor.aggregate(
        promedio=Avg('precio_unitario')
    )['promedio'] or 0
    
    # Preparar datos de insumos con serialización segura
    insumos_data = []
    for pi in insumos_proveedor:
        # Usar valores escalares en vez de objetos para evitar errores de serialización
        insumo_data = {
            'id': pi.id,
            'insumo_id': pi.insumo.id,
            'nombre': pi.insumo.nombre,
            'categoria_nombre': pi.insumo.categoria.nombre if pi.insumo.categoria else None,
            'categoria_id': pi.insumo.categoria_id,
            'unidad_medida_nombre': str(pi.insumo.unidad_medida) if pi.insumo.unidad_medida else None,
            'unidad_medida_id': pi.insumo.unidad_medida_id,
            'precio_unitario': float(pi.precio_unitario),
            'precio_descuento': float(pi.precio_descuento) if pi.precio_descuento else None,
            'precio_final': float(pi.precio_final()),
            'descuento_porcentaje': pi.descuento_porcentaje(),
            'cantidad_minima': float(pi.cantidad_minima),
            'tiempo_entrega_dias': pi.tiempo_entrega_dias,
            'notas': pi.notas,
        }
        insumos_data.append(insumo_data)
    
    # Datos del proveedor para AJAX
    proveedor_ajax = {
        'id': proveedor.id,
        'nombre_comercial': proveedor.nombre_comercial,
        'razon_social': proveedor.razon_social,
        'rfc': proveedor.rfc,
        'persona_contacto': proveedor.persona_contacto,
        'telefono': proveedor.telefono,
        'email': proveedor.email,
        'direccion': proveedor.direccion,
        'ciudad_estado': proveedor.ciudad_estado,
        'categoria_productos': proveedor.categoria_productos,
        'forma_pago_preferida': proveedor.forma_pago_preferida,
        'dias_credito': proveedor.dias_credito,
        'estado': proveedor.estado,
        'fecha_registro': proveedor.fecha_registro.strftime('%d/%m/%Y'),
        'notas_adicionales': proveedor.notas_adicionales,
        'total_insumos': total_insumos,
        'precio_promedio': float(precio_promedio),
    }
    
    # Datos del proveedor para non-AJAX (versión simplificada)
    proveedor_simple = {
        'id': proveedor.id,
        'nombre_comercial': proveedor.nombre_comercial,
        'razon_social': proveedor.razon_social,
        'rfc': proveedor.rfc,
        'telefono': proveedor.telefono,
        'email': proveedor.email,
        'direccion': proveedor.direccion,
        'contacto_principal': proveedor.persona_contacto,
        'estado': proveedor.estado,
        'fecha_registro': proveedor.fecha_registro.strftime('%d/%m/%Y'),
        'precio_promedio': float(precio_promedio),
    }
      # Responder según el tipo de solicitud
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Renderizar el HTML del modal para AJAX
        from django.template.loader import render_to_string
        
        modal_html = render_to_string('dashboard/proveedor_detalle_modal.html', {
            'proveedor': proveedor,
            'insumos_proveedor': insumos_proveedor,
            'total_insumos': total_insumos,
            'precio_promedio': precio_promedio,
        })
        
        return JsonResponse({
            'success': True,
            'proveedor': proveedor_ajax,
            'insumos': insumos_data,
            'html': modal_html
        })
    else:
        # Para solicitudes no-AJAX
        return JsonResponse({
            'success': True,
            'proveedor': proveedor_simple,
            'insumos': insumos_data
        })

@login_required
def editar_proveedor(request, proveedor_id):
    """Vista para editar un proveedor existente"""
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            proveedor.nombre_comercial = request.POST.get('nombre_comercial', '').strip()
            proveedor.razon_social = request.POST.get('razon_social', '').strip()
            proveedor.rfc = request.POST.get('rfc', '').strip()
            proveedor.persona_contacto = request.POST.get('persona_contacto', '').strip()
            proveedor.telefono = request.POST.get('telefono', '').strip()
            proveedor.email = request.POST.get('email', '').strip()
            proveedor.forma_pago_preferida = request.POST.get('forma_pago_preferida', 'transferencia')
            proveedor.dias_credito = int(request.POST.get('dias_credito', '0'))
            proveedor.direccion = request.POST.get('direccion', '').strip()
            proveedor.ciudad_estado = request.POST.get('ciudad_estado', '').strip()
            proveedor.categoria_productos = request.POST.get('categoria_productos', 'ingredientes')
            proveedor.notas_adicionales = request.POST.get('notas_adicionales', '').strip()
            proveedor.estado = request.POST.get('estado', 'activo')
            
            proveedor.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Proveedor "{proveedor.nombre_comercial}" actualizado exitosamente'
                })
            else:
                messages.success(request, f'Proveedor "{proveedor.nombre_comercial}" actualizado exitosamente')
                return redirect('dashboard:proveedores')
                
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error al actualizar el proveedor: {str(e)}'
                })
            else:
                messages.error(request, f'Error al actualizar el proveedor: {str(e)}')
      # Para GET requests o si hay error en POST
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Renderizar el HTML del formulario de edición para AJAX
        from django.template.loader import render_to_string
        
        modal_html = render_to_string('dashboard/proveedor_editar_modal.html', {
            'proveedor': proveedor,
        })
        
        return JsonResponse({
            'success': True,
            'proveedor': {
                'id': proveedor.id,
                'nombre_comercial': proveedor.nombre_comercial,
                'razon_social': proveedor.razon_social,
                'rfc': proveedor.rfc,
                'persona_contacto': proveedor.persona_contacto,
                'telefono': proveedor.telefono,
                'email': proveedor.email,
                'direccion': proveedor.direccion,
                'ciudad_estado': proveedor.ciudad_estado,
                'categoria_productos': proveedor.categoria_productos,
                'forma_pago_preferida': proveedor.forma_pago_preferida,
                'dias_credito': proveedor.dias_credito,
                'estado': proveedor.estado,
                'notas_adicionales': proveedor.notas_adicionales,
            },
            'html': modal_html
        })

@login_required  
def eliminar_proveedor(request, proveedor_id):
    """Vista para eliminar un proveedor"""
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    
    if request.method == 'POST':
        try:
            nombre = proveedor.nombre_comercial
            proveedor.delete()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Proveedor "{nombre}" eliminado exitosamente'
                })
            else:
                messages.success(request, f'Proveedor "{nombre}" eliminado exitosamente')
                return redirect('dashboard:proveedores')
                
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error al eliminar el proveedor: {str(e)}'
                })
            else:
                messages.error(request, f'Error al eliminar el proveedor: {str(e)}')
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })

@login_required
def asignar_insumo_proveedor(request, proveedor_id):
    """Vista para asignar un insumo a un proveedor con precio"""
    if request.method == 'POST':
        try:
            # Log de datos recibidos para debug
            print(f"🔍 DEBUG - Datos recibidos:")
            print(f"   proveedor_id: {proveedor_id} (tipo: {type(proveedor_id)})")
            print(f"   POST data: {dict(request.POST)}")
            
            # El proveedor_id viene del URL, no del POST
            insumo_id = request.POST.get('insumo_id')
            precio_unitario = request.POST.get('precio_unitario')
            precio_descuento = request.POST.get('precio_descuento') or None
            cantidad_minima = request.POST.get('cantidad_minima', 1)
            tiempo_entrega_dias = request.POST.get('tiempo_entrega_dias', 1)
            notas = request.POST.get('observaciones', '')
            
            print(f"   insumo_id: {insumo_id} (tipo: {type(insumo_id)})")
            print(f"   precio_unitario: {precio_unitario}")
            
            # Validaciones
            if not insumo_id or not precio_unitario:
                return JsonResponse({
                    'success': False,
                    'message': 'Faltan campos requeridos: insumo_id y precio_unitario son obligatorios'
                })
            
            # Validar que insumo_id sea un número válido
            try:
                insumo_id = int(insumo_id)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'message': f'ID de insumo inválido: {insumo_id}'
                })
            
            # Validar que proveedor_id sea un número válido
            try:
                proveedor_id = int(proveedor_id)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'message': f'ID de proveedor inválido: {proveedor_id}'
                })
            
            # Validar precio
            try:
                precio_unitario = float(precio_unitario)
                if precio_unitario <= 0:
                    raise ValueError("Precio debe ser mayor a cero")
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'message': f'Precio unitario inválido: {precio_unitario}'
                })
            
            # Buscar proveedor
            try:
                proveedor = Proveedor.objects.get(id=proveedor_id)
                print(f"   ✅ Proveedor encontrado: {proveedor.id} - {proveedor.nombre_comercial}")
            except Proveedor.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': f'No se encontró el proveedor con ID {proveedor_id}'
                })
            
            # Buscar insumo
            try:
                insumo = Insumo.objects.get(id=insumo_id)
                print(f"   ✅ Insumo encontrado: {insumo.id} - {insumo.nombre}")
            except Insumo.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': f'No se encontró el insumo con ID {insumo_id}'
                })
                
            # Verificar si ya existe la relación
            existing = ProveedorInsumo.objects.filter(proveedor=proveedor, insumo=insumo).first()
            if existing:
                print(f"   ⚠️ Relación ya existe, actualizando: {existing.id}")
                # Actualizar la relación existente
                existing.precio_unitario = precio_unitario
                if precio_descuento:
                    try:
                        existing.precio_descuento = float(precio_descuento)
                    except (ValueError, TypeError):
                        existing.precio_descuento = None
                else:
                    existing.precio_descuento = None
                    
                existing.cantidad_minima = float(cantidad_minima) if cantidad_minima else 1
                existing.tiempo_entrega_dias = int(tiempo_entrega_dias) if tiempo_entrega_dias else 1
                existing.notas = notas
                existing.activo = True
                existing.save()
                proveedor_insumo = existing
                mensaje = f'Precio de "{insumo.nombre}" actualizado para el proveedor "{proveedor.nombre_comercial}"'
            else:
                print(f"   ✅ Creando nueva relación...")
                # Crear una nueva relación
                proveedor_insumo = ProveedorInsumo.objects.create(
                    proveedor=proveedor,
                    insumo=insumo,
                    precio_unitario=precio_unitario,
                    precio_descuento=float(precio_descuento) if precio_descuento else None,
                    cantidad_minima=float(cantidad_minima) if cantidad_minima else 1,
                    tiempo_entrega_dias=int(tiempo_entrega_dias) if tiempo_entrega_dias else 1,
                    notas=notas,
                    activo=True
                )
                print(f"   ✅ Relación creada exitosamente: {proveedor_insumo.id}")
                mensaje = f'Insumo "{insumo.nombre}" asignado al proveedor "{proveedor.nombre_comercial}" exitosamente'
            
            return JsonResponse({
                'success': True,
                'message': mensaje,
                'proveedor_insumo': {
                    'id': proveedor_insumo.id,
                    'insumo_nombre': insumo.nombre,
                    'precio_unitario': float(proveedor_insumo.precio_unitario),
                    'precio_final': float(proveedor_insumo.precio_final()),
                }
            })
            
        except Exception as e:
            print(f"❌ Error en asignar_insumo_proveedor: {e}")
            print(f"   Tipo de error: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Error al asignar el insumo: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })

@login_required
def remover_insumo_proveedor(request, proveedor_insumo_id):
    """Vista para remover un insumo de un proveedor"""
    if request.method == 'POST':
        try:
            proveedor_insumo = get_object_or_404(ProveedorInsumo, id=proveedor_insumo_id)
            insumo_nombre = proveedor_insumo.insumo.nombre
            proveedor_nombre = proveedor_insumo.proveedor.nombre_comercial
            
            proveedor_insumo.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Insumo "{insumo_nombre}" removido del proveedor "{proveedor_nombre}"'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al remover el insumo: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })

@login_required
def obtener_insumos_disponibles(request):
    """Vista para obtener insumos disponibles para asignar a proveedores"""
    proveedor_id = request.GET.get('proveedor_id')
    
    if not proveedor_id:
        return JsonResponse({
            'success': False,
            'message': 'ID de proveedor requerido'
        })
    
    try:
        proveedor = get_object_or_404(Proveedor, id=proveedor_id)
        
        # Obtener insumos que no están asignados a este proveedor
        insumos_asignados = ProveedorInsumo.objects.filter(
            proveedor=proveedor,
            activo=True
        ).values_list('insumo_id', flat=True)
        
        insumos_disponibles = Insumo.objects.filter(
            activo=True
        ).exclude(
            id__in=insumos_asignados
        ).select_related('categoria', 'unidad_medida').order_by('categoria__nombre', 'nombre')
        
        insumos_data = [{
            'id': insumo.id,
            'nombre': insumo.nombre,
            'categoria': insumo.categoria.nombre if insumo.categoria else 'Sin categoría',
            'unidad_medida': f"{insumo.unidad_medida.nombre} ({insumo.unidad_medida.abreviacion})" if insumo.unidad_medida else 'Sin unidad',
            'descripcion': '',  # El modelo de Restaurant.Insumo no tiene descripcion
        } for insumo in insumos_disponibles]
        
        return JsonResponse({
            'success': True,
            'insumos': insumos_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener insumos: {str(e)}'
        })
