from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
import json

from restaurant.models import Insumo, MovimientoInventario
from dashboard.models import HistorialPrecios
from dashboard.views.base_views import get_sidebar_context
from dashboard.utils.permissions import require_module_access, require_feature
from accounts.models import Sucursal

@login_required
@require_module_access('inventario')
@require_feature('ver_costos')
def historial_precios_view(request):
    """Vista para consultar el historial de precios de insumos"""
    
    user = request.user
    
    # Determinar qué sucursales puede ver el usuario
    if user.is_superuser or (user.rol and user.rol.nombre == 'admin'):
        es_admin = True
        sucursales_disponibles = Sucursal.objects.filter(activa=True)
        sucursal_filtro = None
    elif user.rol and user.rol.nombre == 'gerente' and user.sucursal:
        es_admin = False
        sucursales_disponibles = Sucursal.objects.filter(id=user.sucursal.id, activa=True)
        sucursal_filtro = user.sucursal
    else:
        es_admin = False
        sucursales_disponibles = Sucursal.objects.none()
        sucursal_filtro = user.sucursal if user.sucursal else None
    
    # Filtro por sucursal desde la URL (solo para admin)
    sucursal_seleccionada_id = request.GET.get('sucursal')
    if es_admin and sucursal_seleccionada_id and sucursal_seleccionada_id != 'todas':
        try:
            sucursal_filtro = sucursales_disponibles.get(id=sucursal_seleccionada_id)
        except:
            pass
    
    # Filtrar historial
    historial_query = HistorialPrecios.objects.all()
    
    # Filtro por sucursal
    if sucursal_filtro:
        historial_query = historial_query.filter(sucursal=sucursal_filtro)
    
    # Filtro por insumo
    insumo_id = request.GET.get('insumo')
    if insumo_id:
        historial_query = historial_query.filter(insumo_id=insumo_id)
    
    # Filtro por fecha (últimos 90 días por defecto)
    dias = request.GET.get('dias', 90)
    try:
        dias = int(dias)
    except:
        dias = 90
    
    fecha_desde = timezone.now() - timezone.timedelta(days=dias)
    historial_query = historial_query.filter(fecha_compra__gte=fecha_desde)
    
    # Ordenar por fecha
    historial = historial_query.order_by('-fecha_compra')[:200]  # Limitar a 200 registros
    
    # Obtener lista de insumos para el filtro
    if sucursal_filtro:
        insumos = Insumo.objects.filter(
            historial_precios__sucursal=sucursal_filtro
        ).distinct().order_by('nombre')
    else:
        insumos = Insumo.objects.filter(
            historial_precios__isnull=False
        ).distinct().order_by('nombre')
    
    # Estadísticas de precios
    estadisticas = []
    
    if insumo_id:
        # Si hay un insumo seleccionado, mostrar estadísticas detalladas
        insumo = get_object_or_404(Insumo, id=insumo_id)
        
        # 1. Obtener precio más reciente
        ultimo_precio = historial.filter(insumo=insumo).first()
        
        # 2. Calcular precio promedio ponderado actual
        lotes_activos = HistorialPrecios.objects.filter(
            insumo=insumo,
            cantidad_restante__gt=0
        )
        
        if sucursal_filtro:
            lotes_activos = lotes_activos.filter(sucursal=sucursal_filtro)
        
        total_unidades = lotes_activos.aggregate(
            total=Sum('cantidad_restante')
        )['total'] or Decimal('0')
        
        total_valor = lotes_activos.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('cantidad_restante') * F('precio_unitario'), 
                    output_field=DecimalField()
                )
            )
        )['total'] or Decimal('0')
        
        precio_promedio = Decimal('0')
        if total_unidades > 0:
            precio_promedio = total_valor / total_unidades
        
        # 3. Diferencia con precio anterior (90 días)
        precio_anterior = historial.filter(
            insumo=insumo,
            fecha_compra__lte=timezone.now() - timezone.timedelta(days=90)
        ).first()
        
        variacion = None
        if ultimo_precio and precio_anterior:
            variacion = {
                'precio_anterior': precio_anterior.precio_unitario,
                'precio_actual': ultimo_precio.precio_unitario,
                'diferencia': ultimo_precio.precio_unitario - precio_anterior.precio_unitario,
                'porcentaje': (ultimo_precio.precio_unitario / precio_anterior.precio_unitario - 1) * 100 if precio_anterior.precio_unitario else None
            }
        
        # 4. Cantidad en stock y valor
        stock_actual = insumo.stock_actual
        valor_stock = stock_actual * precio_promedio
        
        # 5. Precios históricos para gráfica (últimos 12 meses)
        precios_historicos = HistorialPrecios.objects.filter(
            insumo=insumo,
            fecha_compra__gte=timezone.now() - timezone.timedelta(days=365)
        )
        
        if sucursal_filtro:
            precios_historicos = precios_historicos.filter(sucursal=sucursal_filtro)
        
        # Agrupar por mes para la gráfica
        precios_historicos = precios_historicos.values('fecha_compra__month', 'fecha_compra__year').annotate(
            precio_promedio=Sum(
                ExpressionWrapper(
                    F('cantidad_comprada') * F('precio_unitario'), 
                    output_field=DecimalField()
                )
            ) / Sum('cantidad_comprada')
        ).order_by('fecha_compra__year', 'fecha_compra__month')
        
        estadisticas = {
            'insumo': insumo,
            'ultimo_precio': ultimo_precio,
            'precio_promedio': precio_promedio,
            'variacion': variacion,
            'stock_actual': stock_actual,
            'valor_stock': valor_stock,
            'precios_historicos': list(precios_historicos),
            'total_unidades': total_unidades,
            'unidad': insumo.unidad_medida.abreviacion
        }
    
    context = {
        'historial': historial,
        'insumos': insumos,
        'insumo_seleccionado_id': insumo_id,
        'sucursales_disponibles': sucursales_disponibles,
        'sucursal_seleccionada': sucursal_filtro,
        'es_admin': es_admin,
        'dias': dias,
        'estadisticas': estadisticas,
        'current_view': 'historial_precios',
        'sidebar_active': 'historial_precios',
        'inventario_section_active': True,
        **get_sidebar_context('inventario')
    }
    
    return render(request, 'dashboard/historial_precios.html', context)

@login_required
@require_module_access('inventario')
@require_feature('ver_costos')
def historial_precios_api(request, insumo_id):
    """API para obtener el historial de precios de un insumo específico"""
    insumo = get_object_or_404(Insumo, id=insumo_id)
    
    try:
        # Filtrar por sucursal si se especifica
        sucursal_id = request.GET.get('sucursal')
        
        # Query base
        query = HistorialPrecios.objects.filter(insumo=insumo)
        
        if sucursal_id:
            query = query.filter(sucursal_id=sucursal_id)
        
        # Obtener todos los lotes con stock disponible
        lotes_disponibles = query.filter(cantidad_restante__gt=0).order_by('fecha_compra')
        
        # Calcular precio promedio ponderado
        total_unidades = lotes_disponibles.aggregate(total=Sum('cantidad_restante'))['total'] or 0
        if total_unidades > 0:
            total_valor = sum(lote.cantidad_restante * lote.precio_unitario for lote in lotes_disponibles)
            precio_promedio = total_valor / total_unidades
        else:
            precio_promedio = insumo.precio_unitario
        
        # Datos históricos (últimos 10 lotes)
        ultimos_lotes = query.order_by('-fecha_compra')[:10]
        
        # Convertir a formato para API
        lotes_data = []
        for lote in lotes_disponibles:
            lotes_data.append({
                'id': lote.id,
                'fecha_compra': lote.fecha_compra.strftime('%d/%m/%Y'),
                'precio_unitario': float(lote.precio_unitario),
                'cantidad_comprada': float(lote.cantidad_comprada),
                'cantidad_restante': float(lote.cantidad_restante),
                'valor_restante': float(lote.cantidad_restante * lote.precio_unitario),
                'sucursal': lote.sucursal.nombre if lote.sucursal else 'N/A',
                'creado_por': str(lote.creado_por) if lote.creado_por else 'Sistema'
            })
        
        historico_data = []
        for lote in ultimos_lotes:
            historico_data.append({
                'id': lote.id,
                'fecha_compra': lote.fecha_compra.strftime('%d/%m/%Y'),
                'precio_unitario': float(lote.precio_unitario),
                'cantidad_comprada': float(lote.cantidad_comprada),
                'cantidad_restante': float(lote.cantidad_restante),
                'sucursal': lote.sucursal.nombre if lote.sucursal else 'N/A'
            })
        
        return JsonResponse({
            'success': True,
            'insumo': {
                'id': insumo.id,
                'nombre': insumo.nombre,
                'codigo': insumo.codigo,
                'unidad': insumo.unidad_medida.abreviacion,
                'stock_actual': float(insumo.stock_actual)
            },
            'lotes_disponibles': lotes_data,
            'historico': historico_data,
            'precio_promedio': float(precio_promedio),
            'valor_total': float(precio_promedio * insumo.stock_actual)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_module_access('inventario')
@require_feature('ver_costos')
def simulacion_costos_view(request):
    """Vista para simular costos de producción usando historial de precios"""
    user = request.user
    
    # Determinar qué sucursales puede ver el usuario
    if user.is_superuser or (user.rol and user.rol.nombre == 'admin'):
        es_admin = True
        sucursales_disponibles = Sucursal.objects.filter(activa=True)
        sucursal_filtro = None
    else:
        es_admin = False
        sucursal_filtro = user.sucursal
        sucursales_disponibles = Sucursal.objects.filter(id=sucursal_filtro.id) if sucursal_filtro else Sucursal.objects.none()
    
    context = {
        'sucursales_disponibles': sucursales_disponibles,
        'sucursal_seleccionada': sucursal_filtro,
        'es_admin': es_admin,
        'current_view': 'simulacion_costos',
        'sidebar_active': 'simulacion_costos',
        'inventario_section_active': True,
        **get_sidebar_context('inventario')
    }
    
    return render(request, 'dashboard/simulacion_costos.html', context)

@login_required
@require_module_access('inventario')
@require_feature('ver_costos')
def calcular_costo_api(request):
    """API para calcular costo de un insumo según método PEPS o promedio"""
    try:
        insumo_id = request.GET.get('insumo')
        if not insumo_id:
            return JsonResponse({'success': False, 'message': 'Debe especificar un insumo'}, status=400)
            
        insumo = get_object_or_404(Insumo, id=insumo_id)
        
        # Parámetros opcionales
        cantidad = Decimal(request.GET.get('cantidad', '1'))
        sucursal_id = request.GET.get('sucursal')
        metodo = request.GET.get('metodo', 'peps')  # 'peps' o 'promedio'
        
        sucursal = None
        if sucursal_id:
            sucursal = get_object_or_404(Sucursal, id=sucursal_id)
        
        # Calcular costo según método elegido
        if metodo == 'peps':
            costo_total, detalles = HistorialPrecios.calcular_costo_peps(insumo, cantidad, sucursal)
            
            # Convertir detalles a formato para API
            detalles_data = []
            for detalle in detalles:
                detalles_data.append({
                    'lote_id': detalle.get('lote_id'),
                    'fecha_compra': detalle.get('fecha_compra').strftime('%d/%m/%Y') if detalle.get('fecha_compra') else None,
                    'precio_unitario': float(detalle.get('precio_unitario')),
                    'cantidad_tomada': float(detalle.get('cantidad_tomada')),
                    'costo_lote': float(detalle.get('costo_lote')),
                    'stock_insuficiente': detalle.get('stock_insuficiente', False)
                })
            
            return JsonResponse({
                'success': True,
                'insumo': {
                    'id': insumo.id,
                    'nombre': insumo.nombre,
                    'codigo': insumo.codigo,
                    'unidad': insumo.unidad_medida.abreviacion
                },
                'cantidad': float(cantidad),
                'costo_total': float(costo_total),
                'costo_unitario': float(costo_total / cantidad) if cantidad else 0,
                'metodo': 'PEPS',
                'detalles': detalles_data
            })
        else:
            # Método de costo promedio
            costo_total, precio_promedio = HistorialPrecios.calcular_costo_promedio(insumo, cantidad, sucursal)
            
            return JsonResponse({
                'success': True,
                'insumo': {
                    'id': insumo.id,
                    'nombre': insumo.nombre,
                    'codigo': insumo.codigo,
                    'unidad': insumo.unidad_medida.abreviacion
                },
                'cantidad': float(cantidad),
                'costo_total': float(costo_total),
                'costo_unitario': float(precio_promedio),
                'metodo': 'Promedio Ponderado'
            })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
@require_module_access('inventario')
@require_feature('ver_costos')
def descontar_stock_peps_api(request):
    """API para descontar stock utilizando método PEPS"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        insumo_id = data.get('insumo')
        cantidad = Decimal(str(data.get('cantidad', 0)))
        sucursal_id = data.get('sucursal')
        descripcion = data.get('descripcion', 'Venta de producto')
        
        if not insumo_id or cantidad <= 0:
            return JsonResponse({'success': False, 'message': 'Parámetros inválidos'}, status=400)
        
        insumo = get_object_or_404(Insumo, id=insumo_id)
        sucursal = get_object_or_404(Sucursal, id=sucursal_id) if sucursal_id else None
        
        # Realizar la operación en una transacción
        with transaction.atomic():
            costo_total, movimiento = HistorialPrecios.descontar_stock_peps(
                insumo, cantidad, sucursal, descripcion
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Stock descontado correctamente',
                'costo_total': float(costo_total),
                'costo_unitario': float(costo_total / cantidad) if cantidad else 0,
                'stock_actual': float(insumo.stock_actual),
                'movimiento_id': movimiento.id
            })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
