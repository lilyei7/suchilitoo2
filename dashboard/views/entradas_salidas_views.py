from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db import transaction, models
from django.db.models import Q, F
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
import json

from restaurant.models import (
    Inventario, MovimientoInventario, Insumo, CategoriaInsumo, UnidadMedida
)
from dashboard.models import Proveedor, ProveedorInsumo, HistorialPrecios
from accounts.models import Usuario, Sucursal

def is_admin_or_manager(user):
    """Verifica si el usuario es admin o gerente"""
    return user.is_superuser or (user.rol and user.rol.nombre in ['admin', 'gerente'])

@login_required
def entradas_salidas_view(request):
    """Vista principal para la gestión de entradas y salidas de inventario"""
    
    # Filtrar datos según el tipo de usuario
    user = request.user
    
    # Determinar qué sucursales puede ver el usuario
    if user.is_superuser or (user.rol and user.rol.nombre == 'admin'):
        # Admin puede ver todas las sucursales
        sucursales = Sucursal.objects.filter(activa=True)
        sucursal_filtro = None
    elif user.rol and user.rol.nombre == 'gerente' and user.sucursal:
        # Gerente solo ve su sucursal asignada
        sucursales = Sucursal.objects.filter(id=user.sucursal.id, activa=True)
        sucursal_filtro = user.sucursal
    else:
        # Otros usuarios: pueden ver su sucursal si la tienen asignada
        if user.sucursal:
            sucursales = Sucursal.objects.filter(id=user.sucursal.id, activa=True)
            sucursal_filtro = user.sucursal
        else:
            sucursales = Sucursal.objects.none()
            sucursal_filtro = None
    
    # Filtrar proveedores según las sucursales que puede ver el usuario
    if sucursal_filtro:
        # Si el usuario tiene una sucursal específica, mostrar solo proveedores de esa sucursal
        proveedores = Proveedor.objects.filter(
            estado='activo',
            sucursal=sucursal_filtro
        )
    else:
        # Admin puede ver todos los proveedores activos
        proveedores = Proveedor.objects.filter(estado='activo')
    
    # Filtrar movimientos según las sucursales que puede ver
    if sucursal_filtro:
        movimientos = MovimientoInventario.objects.filter(
            sucursal=sucursal_filtro
        ).order_by('-created_at')[:50]
        
        # Estadísticas filtradas por sucursal
        total_movimientos = MovimientoInventario.objects.filter(sucursal=sucursal_filtro).count()
        movimientos_hoy = MovimientoInventario.objects.filter(
            sucursal=sucursal_filtro,
            created_at__date=datetime.now().date()
        ).count()
        
        # Entradas y salidas en los últimos 30 días (filtradas)
        fecha_limite = datetime.now() - timedelta(days=30)
        entradas_recientes = MovimientoInventario.objects.filter(
            sucursal=sucursal_filtro,
            tipo_movimiento='entrada',
            created_at__gte=fecha_limite
        ).count()
        
        salidas_recientes = MovimientoInventario.objects.filter(
            sucursal=sucursal_filtro,
            tipo_movimiento='salida',
            created_at__gte=fecha_limite
        ).count()
    else:
        # Admin: estadísticas globales
        movimientos = MovimientoInventario.objects.all().order_by('-created_at')[:50]
        
        total_movimientos = MovimientoInventario.objects.count()
        movimientos_hoy = MovimientoInventario.objects.filter(
            created_at__date=datetime.now().date()
        ).count()
        
        # Entradas y salidas en los últimos 30 días
        fecha_limite = datetime.now() - timedelta(days=30)
        entradas_recientes = MovimientoInventario.objects.filter(
            tipo_movimiento='entrada',
            created_at__gte=fecha_limite
        ).count()
        
        salidas_recientes = MovimientoInventario.objects.filter(
            tipo_movimiento='salida',
            created_at__gte=fecha_limite
        ).count()
    
    # Contexto para la plantilla
    context = {
        'movimientos': movimientos,
        'sucursales': sucursales,
        'proveedores': proveedores,
        'total_movimientos': total_movimientos,
        'movimientos_hoy': movimientos_hoy,
        'entradas_recientes': entradas_recientes,
        'salidas_recientes': salidas_recientes,
        'current_view': 'entradas_salidas',
        'sidebar_active': 'entradas_salidas',
        'inventario_section_active': True,
        'user_sucursal': sucursal_filtro,  # Para uso en el frontend
        'is_admin': user.is_superuser or (user.rol and user.rol.nombre == 'admin')
    }
    
    return render(request, 'dashboard/entradas_salidas.html', context)

@login_required
@user_passes_test(is_admin_or_manager)
def crear_movimiento(request):
    """API para crear un nuevo movimiento de inventario"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        data = request.POST
        
        # Validamos los campos obligatorios
        required_fields = ['tipoMovimiento', 'sucursalMovimiento', 'motivoMovimiento', 'insumoMovimiento', 'cantidadMovimiento']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'success': False, 'message': f'El campo {field} es obligatorio'}, status=400)
        
        # Obtenemos los valores del formulario
        tipo_movimiento = data.get('tipoMovimiento')
        sucursal_id = data.get('sucursalMovimiento')
        motivo = data.get('motivoMovimiento')
        insumo_id = data.get('insumoMovimiento')
        cantidad = Decimal(data.get('cantidadMovimiento'))
        
        # Validamos que la cantidad sea mayor que cero
        if cantidad <= 0:
            return JsonResponse({'success': False, 'message': 'La cantidad debe ser mayor que cero'}, status=400)
        
        # Obtenemos los objetos relacionados
        sucursal = Sucursal.objects.get(id=sucursal_id)
        insumo = Insumo.objects.get(id=insumo_id)
        
        # Campos opcionales
        observaciones = data.get('observacionesMovimiento', '')
        proveedor_id = data.get('proveedorMovimiento')
        proveedor = None
        if proveedor_id:
            proveedor = Proveedor.objects.get(id=proveedor_id)
        
        # Procesamiento específico según el tipo de movimiento
        with transaction.atomic():
            # Obtener o crear el registro de inventario
            inventario, created = Inventario.objects.get_or_create(
                sucursal=sucursal,
                insumo=insumo,
                defaults={
                    'cantidad_actual': Decimal('0'),
                    'cantidad_reservada': Decimal('0'),
                    'cantidad_disponible': Decimal('0'),
                    'costo_unitario': Decimal('0')
                }
            )
            
            # Guardar cantidad anterior
            cantidad_anterior = inventario.cantidad_actual
            
            if tipo_movimiento == 'entrada':
                # Para entradas, aumentamos el stock
                inventario.cantidad_actual += cantidad
                
                # Si hay proveedor y tiene precio asignado, actualizamos el costo
                if proveedor:
                    try:
                        proveedor_insumo = ProveedorInsumo.objects.get(
                            proveedor=proveedor,
                            insumo=insumo,
                            activo=True
                        )
                        # Actualizar costo unitario del inventario
                        inventario.costo_unitario = proveedor_insumo.precio_final()
                    except ProveedorInsumo.DoesNotExist:
                        # Si no hay relación proveedor-insumo, usar costo del POST si existe
                        costo_unitario = data.get('costoUnitario')
                        if costo_unitario:
                            inventario.costo_unitario = Decimal(costo_unitario)
                
            elif tipo_movimiento == 'salida':
                # Para salidas, verificamos que hay suficiente stock
                if inventario.cantidad_actual < cantidad:
                    return JsonResponse({
                        'success': False, 
                        'message': f'Stock insuficiente. Disponible: {inventario.cantidad_actual} {insumo.unidad_medida.abreviacion}'
                    }, status=400)
                
                # Reducimos el stock
                inventario.cantidad_actual -= cantidad
            
            # Actualizamos cantidad disponible
            inventario.cantidad_disponible = inventario.cantidad_actual - inventario.cantidad_reservada
            inventario.save()
              # Crear el movimiento
            movimiento = MovimientoInventario.objects.create(
                sucursal=sucursal,
                insumo=insumo,
                tipo_movimiento=tipo_movimiento,
                cantidad=cantidad,
                cantidad_anterior=cantidad_anterior,
                cantidad_nueva=inventario.cantidad_actual,
                motivo=f"{motivo}: {observaciones}" if observaciones else motivo,
                documento_referencia=f"MOV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                usuario=request.user
            )
            
            # Si es entrada, registrar en historial de precios
            if tipo_movimiento == 'entrada':
                # Determinar el costo unitario para este movimiento
                costo_unitario = None
                
                # Opción 1: Costo directo ingresado en el formulario
                if data.get('costoUnitario'):
                    costo_unitario = Decimal(data.get('costoUnitario'))
                # Opción 2: Costo del proveedor asignado
                elif proveedor:
                    try:
                        proveedor_insumo = ProveedorInsumo.objects.get(
                            proveedor=proveedor,
                            insumo=insumo,
                            activo=True
                        )
                        costo_unitario = proveedor_insumo.precio_final()
                    except ProveedorInsumo.DoesNotExist:
                        pass
                # Opción 3: Usar el precio actual del insumo
                if costo_unitario is None:
                    costo_unitario = insumo.precio_unitario
                
                # Actualizar también el precio unitario del movimiento
                movimiento.costo_unitario = costo_unitario
                movimiento.save()
                
                # Registrar en historial de precios
                HistorialPrecios.objects.create(
                    insumo=insumo,
                    sucursal=sucursal,
                    fecha_compra=timezone.now(),
                    precio_unitario=costo_unitario,
                    cantidad_comprada=cantidad,
                    cantidad_restante=cantidad,
                    movimiento=movimiento,
                    creado_por=request.user
                )
            
            # También actualizamos el stock_actual del insumo para compatibilidad
            insumo.stock_actual = inventario.cantidad_actual
            insumo.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Movimiento de {tipo_movimiento} registrado exitosamente',
                'movimiento_id': movimiento.id,
                'nueva_cantidad': float(inventario.cantidad_actual)
            })
    
    except Sucursal.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'La sucursal seleccionada no existe'}, status=400)
    except Insumo.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'El insumo seleccionado no existe'}, status=400)
    except Proveedor.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'El proveedor seleccionado no existe'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al procesar el movimiento: {str(e)}'}, status=500)

@login_required
def obtener_insumos(request):
    """API para obtener la lista de insumos disponibles"""
    try:
        sucursal_id = request.GET.get('sucursal_id')
        proveedor_id = request.GET.get('proveedor_id')
        
        # Filtrar insumos activos
        insumos = Insumo.objects.filter(activo=True)
        
        # Si hay proveedor seleccionado, filtrar por insumos del proveedor
        if proveedor_id and proveedor_id != '':
            try:
                proveedor = Proveedor.objects.get(id=proveedor_id)
                insumos_proveedor = ProveedorInsumo.objects.filter(
                    proveedor=proveedor,
                    activo=True
                ).values_list('insumo_id', flat=True)
                insumos = insumos.filter(id__in=insumos_proveedor)
            except Proveedor.DoesNotExist:
                pass
        
        # Obtener información de inventario si hay sucursal
        if sucursal_id and sucursal_id != '':
            try:
                sucursal = Sucursal.objects.get(id=sucursal_id)
                inventarios = Inventario.objects.filter(sucursal=sucursal)
                inventarios_dict = {inv.insumo_id: inv for inv in inventarios}
            except Sucursal.DoesNotExist:
                inventarios_dict = {}
        else:
            inventarios_dict = {}
        
        insumos_data = []
        for insumo in insumos:
            inventario = inventarios_dict.get(insumo.id)
            stock_actual = inventario.cantidad_actual if inventario else 0
            costo_unitario = inventario.costo_unitario if inventario else insumo.precio_unitario
            
            insumos_data.append({
                'id': insumo.id,
                'nombre': insumo.nombre,
                'codigo': insumo.codigo,
                'categoria': insumo.categoria.nombre if insumo.categoria else '',
                'unidad_medida': insumo.unidad_medida.abreviacion,
                'stock_actual': float(stock_actual),
                'stock_minimo': float(insumo.stock_minimo),
                'costo_unitario': float(costo_unitario)
            })
        
        return JsonResponse({'success': True, 'insumos': insumos_data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al obtener insumos: {str(e)}'}, status=500)

@login_required
def obtener_detalle_movimiento(request, movimiento_id):
    """API para obtener los detalles de un movimiento específico"""
    try:
        try:
            movimiento = MovimientoInventario.objects.get(id=movimiento_id)
        except MovimientoInventario.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Movimiento no encontrado'}, status=404)
        
        # Verificar permisos: el usuario debe poder ver esta sucursal
        user = request.user
        if not (user.is_superuser or 
                (user.rol and user.rol.nombre == 'admin') or 
                (user.sucursal and user.sucursal == movimiento.sucursal)):
            return JsonResponse({'success': False, 'message': 'No tienes permisos para ver este movimiento'}, status=403)
        
        detalle = {
            'id': movimiento.id,
            'tipo_movimiento': movimiento.tipo_movimiento,
            'sucursal': movimiento.sucursal.nombre,
            'insumo': {
                'nombre': movimiento.insumo.nombre,
                'codigo': movimiento.insumo.codigo,
                'unidad_medida': movimiento.insumo.unidad_medida.abreviacion
            },
            'cantidad': float(movimiento.cantidad),
            'cantidad_anterior': float(movimiento.cantidad_anterior),
            'cantidad_nueva': float(movimiento.cantidad_nueva),
            'motivo': movimiento.motivo,
            'documento_referencia': movimiento.documento_referencia,
            'usuario': movimiento.usuario.get_full_name() if movimiento.usuario and movimiento.usuario.get_full_name().strip() else (movimiento.usuario.username if movimiento.usuario else 'Sistema'),
            'fecha_creacion': movimiento.created_at.strftime('%d/%m/%Y %H:%M:%S') if movimiento.created_at else '',
        }
        
        return JsonResponse({'success': True, 'movimiento': detalle})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al obtener detalle: {str(e)}'}, status=500)

@login_required
def filtrar_movimientos(request):
    """API para filtrar movimientos según criterios específicos"""
    try:
        user = request.user
        
        # Parámetros de filtro
        sucursal_id = request.GET.get('sucursal')
        tipo_movimiento = request.GET.get('tipo_movimiento') or request.GET.get('tipo')  # Acepta ambos nombres
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        insumo_id = request.GET.get('insumo')
        
        # Determinar qué movimientos puede ver el usuario
        if user.is_superuser or (user.rol and user.rol.nombre == 'admin'):
            # Admin puede ver todos los movimientos
            movimientos = MovimientoInventario.objects.all()
        elif user.rol and user.rol.nombre == 'gerente' and user.sucursal:
            # Gerente solo ve movimientos de su sucursal
            movimientos = MovimientoInventario.objects.filter(sucursal=user.sucursal)
        else:
            # Otros usuarios: solo movimientos de su sucursal
            if user.sucursal:
                movimientos = MovimientoInventario.objects.filter(sucursal=user.sucursal)
            else:
                movimientos = MovimientoInventario.objects.none()
        
        # Aplicar filtros adicionales
        # Filtro por sucursal (solo para admin, otros usuarios ya están filtrados)
        if sucursal_id and sucursal_id not in ['', 'todos', 'todas']:
            try:
                movimientos = movimientos.filter(sucursal_id=int(sucursal_id))
            except (ValueError, TypeError):                # Si no es un ID válido, ignorar el filtro
                pass
        
        # Filtro por tipo de movimiento
        if tipo_movimiento and tipo_movimiento not in ['', 'todos', 'todas']:
            movimientos = movimientos.filter(tipo_movimiento=tipo_movimiento)
        
        # Filtro por fecha inicio
        if fecha_inicio:
            movimientos = movimientos.filter(created_at__date__gte=fecha_inicio)
        
        # Filtro por fecha fin
        if fecha_fin:
            movimientos = movimientos.filter(created_at__date__lte=fecha_fin)
        
        # Filtro por insumo
        if insumo_id and insumo_id not in ['', 'todos', 'todas']:
            try:
                movimientos = movimientos.filter(insumo_id=int(insumo_id))
            except (ValueError, TypeError):                # Si no es un ID válido, ignorar el filtro
                pass
        
        # Ordenar por fecha más reciente
        movimientos = movimientos.order_by('-created_at')[:100]  # Limitar a 100 resultados
        
        # Preparar datos para respuesta
        movimientos_data = []
        for mov in movimientos:
            # Calcular costo total si es posible
            try:
                inventario = Inventario.objects.filter(
                    sucursal=mov.sucursal,
                    insumo=mov.insumo
                ).first()
                costo_unitario = float(inventario.costo_unitario) if inventario and inventario.costo_unitario else 0
                costo_total = float(mov.cantidad) * costo_unitario
            except:
                costo_total = 0
            
            movimientos_data.append({
                'id': mov.id,
                'tipo': mov.tipo_movimiento,  # Para compatibilidad con el frontend
                'tipo_movimiento': mov.tipo_movimiento,
                'sucursal': mov.sucursal.nombre if mov.sucursal else 'N/A',
                'insumo': mov.insumo.nombre if mov.insumo else 'N/A',
                'insumo_codigo': mov.insumo.codigo if mov.insumo else 'N/A',
                'cantidad': float(mov.cantidad),
                'cantidad_anterior': float(mov.cantidad_anterior),
                'cantidad_nueva': float(mov.cantidad_nueva),
                'motivo': mov.motivo or 'Sin motivo',
                'usuario': mov.usuario.get_full_name() if mov.usuario and mov.usuario.get_full_name().strip() else (mov.usuario.username if mov.usuario else 'Sistema'),
                'fecha': mov.created_at.strftime('%d/%m/%Y %H:%M') if mov.created_at else 'N/A',
                'fecha_creacion': mov.created_at.strftime('%d/%m/%Y %H:%M:%S') if mov.created_at else 'N/A',
                'unidad_medida': mov.insumo.unidad_medida.abreviacion if mov.insumo and mov.insumo.unidad_medida else '',
                'costo_total': f'${costo_total:.2f}' if costo_total > 0 else 'N/A',
                'documento_referencia': mov.documento_referencia or 'N/A'
            })
        
        return JsonResponse({'success': True, 'movimientos': movimientos_data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error al filtrar movimientos: {str(e)}'}, status=500)
