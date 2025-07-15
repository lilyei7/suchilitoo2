from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Count, F, Q, Avg, Case, When, Value, DecimalField
from django.db.models.functions import ExtractWeekDay, ExtractHour
import json
from decimal import Decimal
import csv
from datetime import datetime, timedelta
import calendar

from restaurant.models import ProductoVenta, Receta, RecetaInsumo
from dashboard.models import Venta, DetalleVenta, Orden, OrdenItem, Mesa, Cliente
from dashboard.models import HistorialPrecios
from accounts.models import Sucursal, Usuario
from dashboard.views.base_views import get_sidebar_context

@login_required
def ventas_view(request):
    """Vista principal del módulo de ventas con reportes completos"""
    
    # Determinar qué sucursales puede ver el usuario
    user = request.user
    
    if user.is_superuser or (user.rol and user.rol.nombre == 'admin'):
        sucursales = Sucursal.objects.filter(activa=True)
        sucursal_filtro = request.GET.get('sucursal', None)
        if sucursal_filtro:
            sucursal_filtro = int(sucursal_filtro)
    elif user.rol and user.rol.nombre == 'gerente' and user.sucursal:
        sucursales = Sucursal.objects.filter(id=user.sucursal.id, activa=True)
        sucursal_filtro = user.sucursal.id
    else:
        if user.sucursal:
            sucursales = Sucursal.objects.filter(id=user.sucursal.id, activa=True)
            sucursal_filtro = user.sucursal.id
        else:
            sucursales = Sucursal.objects.none()
            sucursal_filtro = None
    
    # Configurar filtros de fecha
    hoy = timezone.now().date()
    fecha_inicio_str = request.GET.get('fecha_inicio', (hoy - timedelta(days=30)).strftime('%Y-%m-%d'))
    fecha_fin_str = request.GET.get('fecha_fin', hoy.strftime('%Y-%m-%d'))
    
    try:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
    except ValueError:
        fecha_inicio = hoy - timedelta(days=30)
        fecha_fin = hoy
        fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')
    
    # Filtro por tipo de reporte
    tipo_reporte = request.GET.get('tipo_reporte', 'diario')
    
    # Construir filtros base para las consultas
    filtros_base = Q(fecha_hora__date__gte=fecha_inicio, fecha_hora__date__lte=fecha_fin)
    if sucursal_filtro:
        filtros_base &= Q(sucursal_id=sucursal_filtro)
    
    # Construir consulta de ventas según filtros
    ventas_query = Venta.objects.filter(filtros_base, anulada=False)
    
    # Obtener estadísticas generales
    total_ventas = ventas_query.count()
    total_ingresos = ventas_query.aggregate(total=Sum('total'))['total'] or 0
    ticket_promedio = total_ingresos / total_ventas if total_ventas > 0 else 0
    
    # Convertir total_ingresos a un valor numérico para usarlo en cálculos
    total_ingresos_valor = float(total_ingresos)
    
    # Obtener ventas por cajero si aplica
    ventas_por_cajero = []
    if user.is_superuser or (user.rol and user.rol.nombre in ['admin', 'gerente']):
        ventas_por_cajero = ventas_query.values('cajero__username', 'cajero__first_name', 'cajero__last_name') \
            .annotate(
                total_ventas=Count('id'),
                total_ingresos=Sum('total'),
                ticket_promedio=Avg('total')
            ).order_by('-total_ingresos')
    
    # Obtener detalles de productos vendidos
    productos_vendidos = DetalleVenta.objects.filter(
            venta__in=ventas_query
        ).values(
            'producto__nombre', 
            'producto__id'
        ).annotate(
            cantidad_total=Sum('cantidad'),
            ingreso_total=Sum(F('precio_unitario') * F('cantidad'))
        ).order_by('-ingreso_total')[:20]  # Top 20 productos
    
    # Calcular el porcentaje de ingresos para cada producto después de la consulta
    for producto in productos_vendidos:
        if total_ingresos_valor > 0:
            producto['porcentaje_ingresos'] = (float(producto['ingreso_total']) * 100) / total_ingresos_valor
        else:
            producto['porcentaje_ingresos'] = 0
    
    # Obtener detalles por día/semana/mes según el tipo de reporte
    detalles_temporales = []
    labels_chart = []
    data_chart = []
    
    if tipo_reporte == 'diario':
        # Agrupar por día
        delta = fecha_fin - fecha_inicio
        for i in range(delta.days + 1):
            dia = fecha_inicio + timedelta(days=i)
            ventas_dia = ventas_query.filter(fecha_hora__date=dia)
            total_dia = ventas_dia.aggregate(total=Sum('total'))['total'] or 0
            
            detalles_temporales.append({
                'periodo': dia.strftime('%d/%m/%Y'),
                'ventas': ventas_dia.count(),
                'total': total_dia,
                'ticket_promedio': total_dia / ventas_dia.count() if ventas_dia.count() > 0 else 0
            })
            
            labels_chart.append(dia.strftime('%d/%m'))
            data_chart.append(float(total_dia))
    
    elif tipo_reporte == 'semanal':
        # Agrupar por semana
        start_week = fecha_inicio - timedelta(days=fecha_inicio.weekday())
        end_week = fecha_fin + timedelta(days=6-fecha_fin.weekday())
        current = start_week
        
        while current <= end_week:
            week_end = current + timedelta(days=6)
            week_start_str = current.strftime('%d/%m/%Y')
            week_end_str = week_end.strftime('%d/%m/%Y')
            
            ventas_semana = ventas_query.filter(fecha_hora__date__gte=current, fecha_hora__date__lte=week_end)
            total_semana = ventas_semana.aggregate(total=Sum('total'))['total'] or 0
            
            detalles_temporales.append({
                'periodo': f"{week_start_str} - {week_end_str}",
                'ventas': ventas_semana.count(),
                'total': total_semana,
                'ticket_promedio': total_semana / ventas_semana.count() if ventas_semana.count() > 0 else 0
            })
            
            labels_chart.append(f"Sem {current.strftime('%d/%m')}")
            data_chart.append(float(total_semana))
            
            current += timedelta(days=7)
    
    else:  # mensual
        # Agrupar por mes
        current_date = fecha_inicio.replace(day=1)
        
        while current_date <= fecha_fin:
            last_day = calendar.monthrange(current_date.year, current_date.month)[1]
            month_end = current_date.replace(day=last_day)
            
            ventas_mes = ventas_query.filter(fecha_hora__date__gte=current_date, fecha_hora__date__lte=month_end)
            total_mes = ventas_mes.aggregate(total=Sum('total'))['total'] or 0
            
            detalles_temporales.append({
                'periodo': current_date.strftime('%B %Y'),
                'ventas': ventas_mes.count(),
                'total': total_mes,
                'ticket_promedio': total_mes / ventas_mes.count() if ventas_mes.count() > 0 else 0
            })
            
            labels_chart.append(current_date.strftime('%b/%y'))
            data_chart.append(float(total_mes))
            
            # Avanzar al siguiente mes
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
    
    # Verificar si es una solicitud de exportación
    if 'exportar' in request.GET:
        formato = request.GET.get('formato', 'csv')
        if formato == 'csv':
            return exportar_ventas_csv(request, ventas_query)
    
    # Obtener información adicional: mejores días/horas de venta
    mejores_dias = None
    mejores_horas = None
    
    if total_ventas > 0:
        # Análisis de mejores días de la semana
        mejores_dias = ventas_query.annotate(
            dia_semana=ExtractWeekDay('fecha')
        ).values('dia_semana').annotate(
            total_ventas=Count('id'),
            ingresos=Sum('total')
        ).order_by('-ingresos')[:3]
        
        # Agregar nombres de días
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        for dia in mejores_dias:
            # Ajustar índice ya que ExtractWeekDay devuelve 1-7 (domingo=1)
            idx = dia['dia_semana'] % 7  # Convertir a 0-6 (lunes=0)
            dia['nombre_dia'] = dias_semana[idx]
        
        # Análisis de mejores horas
        mejores_horas = ventas_query.annotate(
            hora=ExtractHour('fecha')
        ).values('hora').annotate(
            total_ventas=Count('id'),
            ingresos=Sum('total')
        ).order_by('-ingresos')[:3]
        
        # Formatear horas
        for hora in mejores_horas:
            hora['franja'] = f"{hora['hora']}:00 - {hora['hora']+1}:00"
    
    # Ordenar para mostrar los más recientes primero
    detalles_temporales.reverse()
    labels_chart.reverse()
    data_chart.reverse()
    
    context = {
        'sucursales': sucursales,
        'sucursal_filtro': sucursal_filtro,
        'fecha_inicio': fecha_inicio_str,
        'fecha_fin': fecha_fin_str,
        'tipo_reporte': tipo_reporte,
        'total_ventas': total_ventas,
        'total_ingresos': total_ingresos,
        'ticket_promedio': ticket_promedio,
        'ventas_por_cajero': ventas_por_cajero,
        'productos_vendidos': productos_vendidos,
        'detalles_temporales': detalles_temporales,
        'labels_chart': json.dumps(labels_chart),
        'data_chart': json.dumps(data_chart),
        'mejores_dias': mejores_dias,
        'mejores_horas': mejores_horas,
        'current_view': 'ventas',
        'sidebar_active': 'ventas',
        **get_sidebar_context('ventas')
    }
    
    return render(request, 'dashboard/ventas.html', context)

@login_required
def venta_producto_api(request):
    """API para obtener las ventas de un producto específico en un período"""
    
    try:
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        producto_id = request.GET.get('producto_id')
        sucursal_id = request.GET.get('sucursal_id')
        
        if not fecha_inicio or not fecha_fin or not producto_id:
            return JsonResponse({
                'success': False,
                'message': 'Se requieren fechas de inicio, fin y ID de producto'
            }, status=400)
        
        # Crear filtros
        filtros_venta = Q(
            venta__fecha_hora__date__gte=datetime.strptime(fecha_inicio, '%Y-%m-%d').date(),
            venta__fecha_hora__date__lte=datetime.strptime(fecha_fin, '%Y-%m-%d').date(),
            producto_id=producto_id
        )
        
        if sucursal_id and sucursal_id != '0':
            filtros_venta &= Q(venta__sucursal_id=sucursal_id)
        
        # Obtener ventas del producto
        detalles = DetalleVenta.objects.filter(filtros_venta)
        
        # Calcular datos
        total_vendido = detalles.aggregate(
            total_cantidad=Sum('cantidad'),
            total_venta=Sum('precio_total'),
            total_costo=Sum('costo_total')
        )
        
        # Obtener información del producto
        try:
            producto = ProductoVenta.objects.get(id=producto_id)
            nombre_producto = producto.nombre
        except ProductoVenta.DoesNotExist:
            nombre_producto = "Producto desconocido"
        
        # Obtener detalles diarios para gráfico
        ventas_diarias = detalles.values('venta__fecha_hora__date').annotate(
            fecha=F('venta__fecha_hora__date'),
            cantidad=Sum('cantidad'),
            total=Sum('precio_total')
        ).order_by('fecha')
        
        # Preparar datos para gráficos
        datos_grafico = [
            {
                'fecha': venta['fecha'].strftime('%Y-%m-%d'),
                'cantidad': float(venta['cantidad']),
                'total': float(venta['total'])
            }
            for venta in ventas_diarias
        ]
        
        return JsonResponse({
            'success': True,
            'producto': {
                'id': producto_id,
                'nombre': nombre_producto
            },
            'resumen': {
                'cantidad_total': float(total_vendido['total_cantidad'] or 0),
                'venta_total': float(total_vendido['total_venta'] or 0),
                'costo_total': float(total_vendido['total_costo'] or 0),
                'margen': float((total_vendido['total_venta'] or 0) - (total_vendido['total_costo'] or 0))
            },
            'ventas_diarias': datos_grafico
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener datos: {str(e)}'
        }, status=500)

@login_required
def exportar_ventas_csv(request, ventas_query):
    """Función para exportar las ventas a un archivo CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Fecha', 'Sucursal', 'Cajero', 'Cliente', 'Total', 'Método Pago', 'Estado'])
    
    for venta in ventas_query:
        writer.writerow([
            venta.id,
            venta.fecha.strftime('%d/%m/%Y %H:%M'),
            venta.sucursal.nombre if venta.sucursal else 'N/A',
            f"{venta.cajero.first_name} {venta.cajero.last_name}" if venta.cajero else 'N/A',
            venta.cliente.nombre if venta.cliente else 'Cliente General',
            float(venta.total),
            venta.metodo_pago,
            'Completada' if venta.completada else 'Pendiente'
        ])
    
    return response
    """API para registrar venta de un producto y descontar inventario"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        producto_id = data.get('producto_id')
        cantidad = Decimal(str(data.get('cantidad', 1)))
        sucursal_id = data.get('sucursal_id')
        metodo_costeo = data.get('metodo_costeo', 'peps')  # 'peps' o 'promedio'
        
        if not producto_id or not sucursal_id or cantidad <= 0:
            return JsonResponse({'success': False, 'message': 'Parámetros inválidos'}, status=400)
        
        # Obtener producto y verificar que tenga receta
        producto = get_object_or_404(ProductoVenta, id=producto_id, disponible=True)
        sucursal = get_object_or_404(Sucursal, id=sucursal_id, activa=True)
        
        try:
            receta = Receta.objects.get(producto=producto)
        except Receta.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': f'El producto {producto.nombre} no tiene una receta asociada para descontar inventario'
            }, status=400)
        
        # Obtener insumos de la receta
        insumos_receta = RecetaInsumo.objects.filter(receta=receta)
        
        if not insumos_receta:
            return JsonResponse({
                'success': False, 
                'message': f'La receta de {producto.nombre} no tiene insumos asociados'
            }, status=400)
        
        # Realizar la operación en una transacción
        with transaction.atomic():
            costo_total = Decimal('0')
            detalles = []
            
            # Procesar cada insumo de la receta
            for item in insumos_receta:
                insumo = item.insumo
                cantidad_insumo = item.cantidad * cantidad  # Cantidad por número de productos
                
                # Descontar stock según el método elegido
                if metodo_costeo == 'peps':
                    # Usar PEPS para descontar stock y calcular costo
                    costo_item, movimiento = HistorialPrecios.descontar_stock_peps(
                        insumo,
                        cantidad_insumo,
                        sucursal,
                        f"Venta de {producto.nombre} - {cantidad} unidad(es)"
                    )
                else:
                    # Implementar método promedio si se requiere
                    # Por ahora usamos PEPS
                    costo_item, movimiento = HistorialPrecios.descontar_stock_peps(
                        insumo,
                        cantidad_insumo,
                        sucursal,
                        f"Venta de {producto.nombre} - {cantidad} unidad(es)"
                    )
                
                costo_total += costo_item
                
                detalles.append({
                    'insumo_id': insumo.id,
                    'insumo_nombre': insumo.nombre,
                    'cantidad_utilizada': float(cantidad_insumo),
                    'costo': float(costo_item),
                    'unidad': insumo.unidad_medida.abreviacion
                })
            
            # Aquí se podría registrar la venta en un modelo de Ventas si existiera
            
            # Calcular margen de ganancia
            precio_venta_total = producto.precio * cantidad
            margen = (precio_venta_total - costo_total) / costo_total * 100 if costo_total > 0 else 0
            
            return JsonResponse({
                'success': True,
                'message': f'Se ha registrado la venta de {cantidad} {producto.nombre} y descontado el inventario',
                'producto': {
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'codigo': producto.codigo
                },
                'cantidad': float(cantidad),
                'precio_unitario': float(producto.precio),
                'precio_total': float(precio_venta_total),
                'costo_total': float(costo_total),
                'margen': float(margen),
                'fecha': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
                'detalles': detalles
            })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def exportar_ventas_csv(ventas_query):
    """
    Exportar consulta de ventas a un archivo CSV
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Fecha', 'Sucursal', 'Cajero', 'Cliente', 
        'Método de Pago', 'Subtotal', 'Impuestos', 'Total',
        'Estado', 'Comentarios'
    ])
    
    for venta in ventas_query:
        writer.writerow([
            venta.id,
            venta.fecha.strftime('%d/%m/%Y %H:%M'),
            venta.sucursal.nombre if venta.sucursal else 'N/A',
            f"{venta.cajero.first_name} {venta.cajero.last_name}" if venta.cajero else 'N/A',
            venta.cliente.nombre if venta.cliente else 'Cliente General',
            venta.metodo_pago,
            venta.subtotal,
            venta.impuestos,
            venta.total,
            'Anulada' if venta.anulada else 'Completada',
            venta.comentarios or ''
        ])
    
    return response

@login_required
def ventas_por_periodo_api(request):
    """API para obtener datos de ventas por periodo (día, semana, mes)"""
    
    # Validar parámetros de consulta
    try:
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        tipo_periodo = request.GET.get('tipo_periodo', 'diario')  # diario, semanal, mensual
        sucursal_id = request.GET.get('sucursal_id')
        
        if not fecha_inicio or not fecha_fin:
            return JsonResponse({
                'success': False,
                'message': 'Se requieren fechas de inicio y fin'
            }, status=400)
        
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        # Construir filtros
        filtros = Q(fecha_hora__date__gte=fecha_inicio, fecha_hora__date__lte=fecha_fin, anulada=False)
        if sucursal_id:
            filtros &= Q(sucursal_id=sucursal_id)
        
        # Consulta base
        ventas = Venta.objects.filter(filtros)
        
        # Resultados según el tipo de periodo
        resultados = []
        labels = []
        valores = []
        
        if tipo_periodo == 'diario':
            # Consulta por día
            delta = fecha_fin - fecha_inicio
            for i in range(delta.days + 1):
                dia = fecha_inicio + timedelta(days=i)
                ventas_dia = ventas.filter(fecha_hora__date=dia)
                total_dia = ventas_dia.aggregate(total=Sum('total'))['total'] or 0
                
                labels.append(dia.strftime('%d/%m/%Y'))
                valores.append(float(total_dia))
                resultados.append({
                    'fecha': dia.strftime('%d/%m/%Y'),
                    'total_ventas': ventas_dia.count(),
                    'total_ingresos': float(total_dia),
                })
        
        elif tipo_periodo == 'semanal':
            # Consulta por semana
            current = fecha_inicio - timedelta(days=fecha_inicio.weekday())
            end_date = fecha_fin + timedelta(days=6-fecha_fin.weekday())
            
            while current <= end_date:
                week_end = current + timedelta(days=6)
                ventas_semana = ventas.filter(fecha_hora__date__gte=current, fecha_hora__date__lte=week_end)
                total_semana = ventas_semana.aggregate(total=Sum('total'))['total'] or 0
                
                week_label = f"{current.strftime('%d/%m/%Y')} - {week_end.strftime('%d/%m/%Y')}"
                labels.append(week_label)
                valores.append(float(total_semana))
                resultados.append({
                    'periodo': week_label,
                    'total_ventas': ventas_semana.count(),
                    'total_ingresos': float(total_semana),
                })
                
                current += timedelta(days=7)
        
        else:  # mensual
            # Consulta por mes
            current_date = fecha_inicio.replace(day=1)
            
            while current_date <= fecha_fin:
                last_day = calendar.monthrange(current_date.year, current_date.month)[1]
                month_end = current_date.replace(day=last_day)
                
                ventas_mes = ventas.filter(fecha_hora__date__gte=current_date, fecha_hora__date__lte=month_end)
                total_mes = ventas_mes.aggregate(total=Sum('total'))['total'] or 0
                
                month_label = current_date.strftime('%B %Y')
                labels.append(month_label)
                valores.append(float(total_mes))
                resultados.append({
                    'periodo': month_label,
                    'total_ventas': ventas_mes.count(),
                    'total_ingresos': float(total_mes),
                })
                
                # Avanzar al siguiente mes
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        return JsonResponse({
            'success': True,
            'labels': labels,
            'valores': valores,
            'resultados': resultados
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al generar reporte: {str(e)}'
        }, status=500)

@login_required
def productos_mas_vendidos_api(request):
    """API para obtener los productos más vendidos en un período"""
    
    try:
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        limite = int(request.GET.get('limite', 10))
        sucursal_id = request.GET.get('sucursal_id')
        
        if not fecha_inicio or not fecha_fin:
            return JsonResponse({
                'success': False,
                'message': 'Se requieren fechas de inicio y fin'
            }, status=400)
        
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        # Construir filtros
        filtros_venta = Q(venta__fecha__gte=fecha_inicio, venta__fecha__lte=fecha_fin, venta__anulada=False)
        if sucursal_id:
            filtros_venta &= Q(venta__sucursal_id=sucursal_id)
        
        # Obtener productos más vendidos
        productos = DetalleVenta.objects.filter(filtros_venta).values(
            'producto__nombre',
            'producto__id'
        ).annotate(
            total_unidades=Sum('cantidad'),
            total_ventas=Sum(F('precio_unitario') * F('cantidad'))
        ).order_by('-total_unidades')[:limite]
        
        # Formatear resultados
        resultados = []
        for p in productos:
            resultados.append({
                'id': p['producto__id'],
                'nombre': p['producto__nombre'],
                'unidades_vendidas': p['total_unidades'],
                'total_ventas': float(p['total_ventas'])
            })
        
        return JsonResponse({
            'success': True,
            'productos': resultados
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener productos más vendidos: {str(e)}'
        }, status=500)

@login_required
def ventas_por_cajero_api(request):
    """API para obtener datos de ventas por cajero"""
    
    try:
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        sucursal_id = request.GET.get('sucursal_id')
        
        if not fecha_inicio or not fecha_fin:
            return JsonResponse({
                'success': False,
                'message': 'Se requieren fechas de inicio y fin'
            }, status=400)
        
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        # Verificar permisos del usuario para ver información de cajeros
        user = request.user
        if not (user.is_superuser or (user.rol and user.rol.nombre in ['admin', 'gerente'])):
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para acceder a esta información'
            }, status=403)
        
        # Construir filtros
        filtros = Q(fecha_hora__date__gte=fecha_inicio, fecha_hora__date__lte=fecha_fin, anulada=False)
        if sucursal_id:
            filtros &= Q(sucursal_id=sucursal_id)
        
        # Obtener ventas por cajero
        ventas_cajeros = Venta.objects.filter(filtros).values(
            'cajero__id',
            'cajero__username',
            'cajero__first_name',
            'cajero__last_name'
        ).annotate(
            total_ventas=Count('id'),
            total_ingresos=Sum('total'),
            ticket_promedio=Avg('total')
        ).order_by('-total_ingresos')
        
        # Formatear resultados
        resultados = []
        for vc in ventas_cajeros:
            if vc['cajero__id']:  # Evitar cajeros nulos
                resultados.append({
                    'id': vc['cajero__id'],
                    'username': vc['cajero__username'],
                    'nombre': f"{vc['cajero__first_name']} {vc['cajero__last_name']}",
                    'total_ventas': vc['total_ventas'],
                    'total_ingresos': float(vc['total_ingresos']),
                    'ticket_promedio': float(vc['ticket_promedio'])
                })
        
        return JsonResponse({
            'success': True,
            'cajeros': resultados
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener ventas por cajero: {str(e)}'
        }, status=500)
