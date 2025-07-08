from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from mesero.models import Orden, OrdenItem
from .models import OrdenCocina, ItemCocina, TiempoPreparacion, LogCocina
import json
from datetime import datetime, timedelta

def es_personal_cocina(user):
    """Verifica si el usuario es personal de cocina"""
    return user.groups.filter(name__in=['Cocina', 'Cocinero', 'Chef']).exists() or user.is_superuser

def login_view(request):
    """Vista de login específica para cocina"""
    if request.user.is_authenticated:
        if es_personal_cocina(request.user):
            return redirect('cocina:dashboard')
        else:
            messages.error(request, 'No tienes permisos para acceder al sistema de cocina.')
            return redirect('accounts:login')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if es_personal_cocina(user):
                login(request, user)
                messages.success(request, f'¡Bienvenido a Cocina, {user.first_name or user.username}!')
                return redirect('cocina:dashboard')
            else:
                messages.error(request, 'No tienes permisos para acceder al sistema de cocina.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    context = {
        'title': 'Acceso a Cocina',
    }
    return render(request, 'cocina/login.html', context)

@login_required
def logout_view(request):
    """Vista de logout para cocina"""
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('cocina:login')

@login_required
@user_passes_test(es_personal_cocina)
def dashboard(request):
    """Dashboard principal de cocina - Vista de comandas optimizada"""
    # Obtener la sucursal del usuario
    sucursal_usuario = request.user.sucursal
    
    # Fecha y hora actual
    ahora = timezone.now()
    
    # Query base filtrado por sucursal
    if sucursal_usuario:
        ordenes_base = Orden.objects.filter(mesa__sucursal=sucursal_usuario)
    else:
        # Si el usuario no tiene sucursal asignada, mostrar todas (para superusuarios)
        ordenes_base = Orden.objects.all()
    
    # Obtener todas las órdenes activas (pendientes, confirmadas, en preparación)
    ordenes_activas = ordenes_base.filter(
        estado__in=['pendiente', 'confirmada', 'en_preparacion']
    ).select_related('mesa', 'mesero').prefetch_related('items__producto').order_by('fecha_creacion')
    
    # Obtener órdenes completadas del día actual para el tab "Completados"
    ordenes_completadas = ordenes_base.filter(
        estado__in=['lista', 'entregada', 'completada'],
        fecha_creacion__date=ahora.date()  # Solo del día actual
    ).select_related('mesa', 'mesero').prefetch_related('items__producto').order_by('-fecha_creacion')
    
    # Procesar cada orden para agregar metadatos de tiempo y prioridad
    ordenes_procesadas = []
    ordenes_completadas_procesadas = []
    
    # Procesar órdenes activas
    for orden in ordenes_activas:
        # Calcular tiempo transcurrido desde la creación
        tiempo_transcurrido = int((ahora - orden.fecha_creacion).total_seconds() / 60)
        
        # Tiempo estimado de preparación (15 min estándar + 1.5 min tolerancia)
        tiempo_estimado_base = 15
        tiempo_tolerancia = 1.5
        tiempo_limite_total = tiempo_estimado_base + tiempo_tolerancia
        
        # Determinar estado de prioridad
        if tiempo_transcurrido > tiempo_limite_total:
            prioridad = 'retrasada'
            minutos_retraso = tiempo_transcurrido - tiempo_limite_total
            minutos_tolerancia = -1
        elif tiempo_transcurrido > tiempo_estimado_base:
            prioridad = 'tolerancia'
            minutos_retraso = 0
            minutos_tolerancia = max(0, tiempo_limite_total - tiempo_transcurrido)
        else:
            prioridad = 'normal'
            minutos_retraso = 0
            minutos_tolerancia = tiempo_limite_total - tiempo_transcurrido
        
        # Formatear tiempos para mostrar en template
        def format_time(minutes):
            if minutes >= 60:
                hours = minutes // 60
                mins = minutes % 60
                return f"{hours}h {mins}m"
            else:
                return f"{minutes}m"
        
        # Agregar metadatos a la orden
        orden.tiempo_transcurrido = tiempo_transcurrido
        orden.tiempo_estimado = tiempo_estimado_base
        orden.tiempo_tolerancia = tiempo_tolerancia
        orden.tiempo_limite_total = tiempo_limite_total
        orden.minutos_retraso = minutos_retraso
        orden.minutos_tolerancia = minutos_tolerancia
        orden.prioridad = prioridad
        
        # Strings formateados para el template
        orden.tiempo_transcurrido_str = format_time(tiempo_transcurrido)
        orden.tiempo_estimado_str = format_time(tiempo_estimado_base)
        
        # Calcular tiempo restante
        if tiempo_transcurrido < tiempo_limite_total:
            orden.tiempo_restante = max(0, tiempo_limite_total - tiempo_transcurrido)
        else:
            orden.tiempo_restante = 0
        
        # Expandir ítems para visualización individual
        orden.items_expandidos = expandir_items_orden(orden)
        
        ordenes_procesadas.append(orden)
    
    # Procesar órdenes completadas
    for orden in ordenes_completadas:
        # Para órdenes completadas, calculamos el tiempo total que tomó
        fecha_final = orden.fecha_lista or orden.fecha_entrega or orden.fecha_cierre
        if fecha_final:
            tiempo_total = int((fecha_final - orden.fecha_creacion).total_seconds() / 60)
        else:
            tiempo_total = int((ahora - orden.fecha_creacion).total_seconds() / 60)
        
        def format_time(minutes):
            if minutes >= 60:
                hours = minutes // 60
                mins = minutes % 60
                return f"{hours}h {mins}m"
            else:
                return f"{minutes}m"
        
        # Agregar metadatos a la orden completada
        orden.tiempo_total = tiempo_total
        orden.tiempo_total_str = format_time(tiempo_total)
        orden.prioridad = 'completada'
        orden.estado_display = 'Completada'
        orden.fecha_final = fecha_final or ahora
        
        # Expandir ítems para visualización individual
        orden.items_expandidos = expandir_items_orden(orden)
        
        ordenes_completadas_procesadas.append(orden)
    
    # Ordenar por prioridad: retrasados primero, luego por tiempo de creación
    ordenes_procesadas.sort(key=lambda x: (
        0 if x.prioridad == 'retrasada' else 1 if x.prioridad == 'tolerancia' else 2,
        x.fecha_creacion
    ))
    
    # Estadísticas rápidas
    total_ordenes = len(ordenes_procesadas)
    ordenes_retrasadas = len([o for o in ordenes_procesadas if o.prioridad == 'retrasada'])
    ordenes_en_tolerancia = len([o for o in ordenes_procesadas if o.prioridad == 'tolerancia'])
    ordenes_normales = len([o for o in ordenes_procesadas if o.prioridad == 'normal'])
    total_completadas = len(ordenes_completadas_procesadas)
    
    context = {
        'total_ordenes': total_ordenes,
        'total_retrasadas': ordenes_retrasadas,
        'total_tolerancia': ordenes_en_tolerancia,
        'total_normales': ordenes_normales,
        'total_completadas': total_completadas,
        
        # Información de sucursal
        'sucursal_actual': sucursal_usuario,
        'usuario_actual': request.user,
        
        # Lista de órdenes procesadas con prioridad
        'ordenes_activas': ordenes_procesadas,
        'ordenes_completadas': ordenes_completadas_procesadas,
        
        # Fecha actual
        'fecha_actual': ahora.date(),
        'hora_actual': ahora.time(),
    }
    
    return render(request, 'cocina/dashboard_comandas.html', context)

@login_required
@user_passes_test(es_personal_cocina)
def ordenes_pendientes(request):
    """Vista de órdenes pendientes y en preparación"""
    # Obtener la sucursal del usuario
    sucursal_usuario = request.user.sucursal
    
    # Filtros
    estado_filter = request.GET.get('estado', 'activas')
    mesa_filter = request.GET.get('mesa', '')
    
    # Query base filtrado por sucursal
    if sucursal_usuario:
        ordenes = Orden.objects.filter(mesa__sucursal=sucursal_usuario)
    else:
        ordenes = Orden.objects.all()
    
    ordenes = ordenes.select_related('mesa', 'mesero').prefetch_related('items__producto')
    
    if estado_filter == 'activas':
        ordenes = ordenes.filter(estado__in=['confirmada', 'en_preparacion'])
    elif estado_filter == 'pendientes':
        ordenes = ordenes.filter(estado='confirmada')
    elif estado_filter == 'preparacion':
        ordenes = ordenes.filter(estado='en_preparacion')
    elif estado_filter == 'listas':
        ordenes = ordenes.filter(estado='lista')
    elif estado_filter == 'todas':
        ordenes = ordenes.filter(estado__in=['confirmada', 'en_preparacion', 'lista'])
    
    if mesa_filter:
        ordenes = ordenes.filter(mesa__numero__icontains=mesa_filter)
    
    # Ordenamiento
    ordenes = ordenes.order_by('fecha_creacion')
    
    # Paginación
    paginator = Paginator(ordenes, 20)
    page = request.GET.get('page')
    ordenes_paginadas = paginator.get_page(page)
    
    # Agregar información de cocina a cada orden
    for orden in ordenes_paginadas:
        try:
            orden.cocina_info = orden.cocina_info
        except OrdenCocina.DoesNotExist:
            # Crear info de cocina si no existe
            OrdenCocina.objects.create(orden=orden)
            orden.refresh_from_db()
    
    context = {
        'ordenes': ordenes_paginadas,
        'estado_filter': estado_filter,
        'mesa_filter': mesa_filter,
        'total_ordenes': ordenes.count() if hasattr(ordenes, 'count') else len(ordenes),
        'sucursal_actual': sucursal_usuario,
    }
    
    return render(request, 'cocina/ordenes_pendientes.html', context)

@login_required
@user_passes_test(es_personal_cocina)
def ordenes_ajax(request):
    """Vista AJAX para actualizar órdenes en tiempo real"""
    estado_filter = request.GET.get('estado', 'activas')
    
    ordenes = Orden.objects.select_related('mesa', 'mesero').prefetch_related('items__producto')
    
    if estado_filter == 'activas':
        ordenes = ordenes.filter(estado__in=['confirmada', 'en_preparacion'])
    elif estado_filter == 'pendientes':
        ordenes = ordenes.filter(estado='confirmada')
    elif estado_filter == 'preparacion':
        ordenes = ordenes.filter(estado='en_preparacion')
    elif estado_filter == 'listas':
        ordenes = ordenes.filter(estado='lista')
    
    ordenes = ordenes.order_by('fecha_creacion')[:20]
    
    data = []
    for orden in ordenes:
        try:
            cocina_info = orden.cocina_info
        except OrdenCocina.DoesNotExist:
            cocina_info = OrdenCocina.objects.create(orden=orden)
        
        items_data = []
        for item in orden.items.all():
            items_data.append({
                'id': item.id,
                'producto': item.producto.nombre,
                'cantidad': item.cantidad,
                'estado': item.estado,
                'observaciones': item.observaciones or '',
            })
        
        data.append({
            'id': orden.id,
            'numero_orden': orden.numero_orden,
            'mesa': orden.mesa.numero if orden.mesa else 'Sin mesa',
            'estado': orden.estado,
            'estado_display': orden.get_estado_display(),
            'tiempo_creacion': orden.fecha_creacion.strftime('%H:%M'),
            'tiempo_estimado': cocina_info.tiempo_estimado_total,
            'tiempo_transcurrido': cocina_info.tiempo_transcurrido() or 0,
            'prioridad': cocina_info.prioridad,
            'cocinero': cocina_info.cocinero_asignado.first_name if cocina_info.cocinero_asignado else None,
            'items': items_data,
            'observaciones': orden.observaciones or '',
        })
    
    return JsonResponse({'ordenes': data})

@login_required
@user_passes_test(es_personal_cocina)
def detalle_orden(request, orden_id):
    """Vista detallada de una orden específica"""
    orden = get_object_or_404(Orden, id=orden_id)
    
    # Obtener o crear info de cocina
    cocina_info, created = OrdenCocina.objects.get_or_create(orden=orden)
    if created:
        cocina_info.calcular_tiempo_estimado()
    
    # Obtener items con su info de cocina
    items = []
    for item in orden.items.all():
        item_cocina, _ = ItemCocina.objects.get_or_create(orden_item=item)
        items.append({
            'item': item,
            'cocina_info': item_cocina,
        })
    
    # Logs de la orden
    logs = LogCocina.objects.filter(orden=orden).order_by('-timestamp')[:10]
    
    context = {
        'orden': orden,
        'cocina_info': cocina_info,
        'items': items,
        'logs': logs,
    }
    
    return render(request, 'cocina/detalle_orden.html', context)

@login_required
@user_passes_test(es_personal_cocina)
@require_POST
def cambiar_estado_item(request, orden_id, item_id):
    """Cambia el estado de un item específico"""
    try:
        orden = get_object_or_404(Orden, id=orden_id)
        item = get_object_or_404(OrdenItem, id=item_id, orden=orden)
        
        nuevo_estado = request.POST.get('estado')
        estados_validos = ['pendiente', 'en_preparacion', 'listo', 'entregado', 'cancelado']
        
        if nuevo_estado not in estados_validos:
            return JsonResponse({'success': False, 'message': 'Estado no válido'})
        
        # Actualizar estado del item
        estado_anterior = item.estado
        item.estado = nuevo_estado
        item.save()
        
        # Obtener o crear info de cocina del item
        item_cocina, _ = ItemCocina.objects.get_or_create(orden_item=item)
        
        # Manejar transiciones de estado
        if nuevo_estado == 'en_preparacion' and estado_anterior != 'en_preparacion':
            item_cocina.iniciar_preparacion(request.user)
        elif nuevo_estado == 'listo' and estado_anterior != 'listo':
            item_cocina.finalizar_preparacion()
        
        # Actualizar estado de cocina del item
        item_cocina.estado_cocina = nuevo_estado
        item_cocina.save()
        
        # Log de la acción
        LogCocina.objects.create(
            orden=orden,
            item=item,
            accion='cambio_estado',
            usuario=request.user,
            descripcion=f'Estado cambiado de {estado_anterior} a {nuevo_estado}'
        )
        
        # Verificar si todos los items están listos para cambiar estado de orden
        items_pendientes = orden.items.exclude(estado__in=['listo', 'entregado', 'cancelado']).count()
        if items_pendientes == 0 and orden.estado == 'en_preparacion':
            orden.estado = 'lista'
            orden.fecha_lista = timezone.now()
            orden.save()
            
            # Log de orden lista
            LogCocina.objects.create(
                orden=orden,
                accion='orden_completada',
                usuario=request.user,
                descripcion='Todos los items completados - orden lista'
            )
        
        return JsonResponse({
            'success': True,
            'message': f'Estado del item actualizado a {nuevo_estado}',
            'nuevo_estado': nuevo_estado,
            'orden_estado': orden.estado
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@user_passes_test(es_personal_cocina)
@require_POST
def cambiar_estado_orden(request, orden_id):
    """Cambia el estado de una orden completa"""
    try:
        orden = get_object_or_404(Orden, id=orden_id)
        nuevo_estado = request.POST.get('estado')
        
        estados_validos = ['confirmada', 'en_preparacion', 'lista', 'entregada', 'cancelada']
        if nuevo_estado not in estados_validos:
            return JsonResponse({'success': False, 'message': 'Estado no válido'})
        
        estado_anterior = orden.estado
        orden.estado = nuevo_estado
        
        # Actualizar fechas según el estado
        now = timezone.now()
        if nuevo_estado == 'en_preparacion':
            orden.fecha_preparacion = now
            # Obtener o crear info de cocina
            cocina_info, _ = OrdenCocina.objects.get_or_create(orden=orden)
            cocina_info.iniciar_preparacion(request.user)
        elif nuevo_estado == 'lista':
            orden.fecha_lista = now
        elif nuevo_estado == 'entregada':
            orden.fecha_entrega = now
        
        orden.save()
        
        # Si se inicia preparación, cambiar estado de todos los items a en_preparacion
        if nuevo_estado == 'en_preparacion':
            orden.items.filter(estado='pendiente').update(estado='en_preparacion')
        
        # Log de la acción
        LogCocina.objects.create(
            orden=orden,
            accion='cambio_estado',
            usuario=request.user,
            descripcion=f'Estado de orden cambiado de {estado_anterior} a {nuevo_estado}'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Orden actualizada a {nuevo_estado}',
            'nuevo_estado': nuevo_estado
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@user_passes_test(es_personal_cocina)
def reportes(request):
    """Reportes y estadísticas de cocina"""
    # Filtros de fecha
    fecha_desde = request.GET.get('desde', (timezone.now() - timedelta(days=7)).date())
    fecha_hasta = request.GET.get('hasta', timezone.now().date())
    
    if isinstance(fecha_desde, str):
        fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
    if isinstance(fecha_hasta, str):
        fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    
    # Estadísticas de órdenes
    ordenes_periodo = Orden.objects.filter(
        fecha_creacion__date__range=[fecha_desde, fecha_hasta]
    )
    
    total_ordenes = ordenes_periodo.count()
    ordenes_completadas = ordenes_periodo.filter(estado='entregada').count()
    ordenes_canceladas = ordenes_periodo.filter(estado='cancelada').count()
    
    # Tiempos promedio
    tiempos = TiempoPreparacion.objects.aggregate(
        tiempo_promedio=Avg('tiempo_promedio'),
        tiempo_estimado_promedio=Avg('tiempo_estimado')
    )
    
    # Productos más preparados
    productos_populares = OrdenItem.objects.filter(
        orden__fecha_creacion__date__range=[fecha_desde, fecha_hasta]
    ).values('producto__nombre').annotate(
        total=Count('id'),
        cantidad_total=Count('cantidad')
    ).order_by('-total')[:10]
    
    context = {
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'total_ordenes': total_ordenes,
        'ordenes_completadas': ordenes_completadas,
        'ordenes_canceladas': ordenes_canceladas,
        'tasa_completacion': round((ordenes_completadas / total_ordenes * 100) if total_ordenes > 0 else 0, 1),
        'tiempo_promedio': round(tiempos['tiempo_promedio'] or 0, 1),
        'tiempo_estimado_promedio': round(tiempos['tiempo_estimado_promedio'] or 0, 1),
        'productos_populares': productos_populares,
    }
    
    return render(request, 'cocina/reportes.html', context)

@login_required
@user_passes_test(es_personal_cocina)
def estadisticas(request):
    """Estadísticas avanzadas y gráficos"""
    return render(request, 'cocina/estadisticas.html')

@login_required
@user_passes_test(es_personal_cocina)
def api_ordenes(request):
    """API para obtener órdenes en formato JSON"""
    estado = request.GET.get('estado', 'activas')
    limit = int(request.GET.get('limit', 50))
    
    ordenes = Orden.objects.select_related('mesa', 'mesero')
    
    if estado == 'activas':
        ordenes = ordenes.filter(estado__in=['confirmada', 'en_preparacion'])
    elif estado != 'todas':
        ordenes = ordenes.filter(estado=estado)
    
    ordenes = ordenes.order_by('-fecha_creacion')[:limit]
    
    data = []
    for orden in ordenes:
        data.append({
            'id': orden.id,
            'numero_orden': orden.numero_orden,
            'mesa': orden.mesa.numero if orden.mesa else None,
            'estado': orden.estado,
            'fecha_creacion': orden.fecha_creacion.isoformat(),
            'total': float(orden.total),
            'items_count': orden.items.count(),
        })
    
    return JsonResponse({'ordenes': data})

@login_required
@user_passes_test(es_personal_cocina)
def api_tiempos_preparacion(request):
    """API para obtener tiempos de preparación"""
    tiempos = TiempoPreparacion.objects.select_related('producto').all()
    
    data = []
    for tiempo in tiempos:
        data.append({
            'producto_id': tiempo.producto.id,
            'producto_nombre': tiempo.producto.nombre,
            'tiempo_estimado': tiempo.tiempo_estimado,
            'tiempo_promedio': round(tiempo.tiempo_promedio, 1),
            'cantidad_preparaciones': tiempo.cantidad_preparaciones,
        })
    
    return JsonResponse({'tiempos': data})

@login_required
@user_passes_test(es_personal_cocina)
def orden_detalles_ajax(request, orden_id):
    """Vista AJAX para obtener detalles de una orden"""
    try:
        orden = get_object_or_404(
            Orden.objects.select_related('mesa', 'mesero').prefetch_related('items__producto'),
            id=orden_id
        )
        
        # Calcular tiempo transcurrido
        ahora = timezone.now()
        tiempo_transcurrido = int((ahora - orden.fecha_creacion).total_seconds() / 60)
        
        # Generar HTML para el modal
        html = f"""
        <div class="order-details-modal">
            <div class="row">
                <div class="col-md-8">
                    <h6>Orden #{orden.numero_orden}</h6>
                    <p><strong>Mesa:</strong> {orden.mesa.numero}</p>
                    <p><strong>Mesero:</strong> {orden.mesero.get_full_name() if orden.mesero else 'N/A'}</p>
                    <p><strong>Estado:</strong> 
                        <span class="badge bg-{'warning' if orden.estado == 'confirmada' else 'info' if orden.estado == 'en_preparacion' else 'success' if orden.estado == 'lista' else 'secondary'}">
                            {orden.get_estado_display()}
                        </span>
                    </p>
                    <p><strong>Tiempo transcurrido:</strong> {tiempo_transcurrido} minutos</p>
                    
                    <h6 class="mt-4">Items del pedido:</h6>
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Producto</th>
                                    <th>Cantidad</th>
                                    <th>Notas</th>
                                    <th>Estado</th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for item in orden.items.all():
            html += f"""
                                <tr>
                                    <td>{item.producto.nombre}</td>
                                    <td>{item.cantidad}</td>
                                    <td>{item.notas or '-'}</td>
                                    <td>
                                        <span class="badge bg-{'warning' if item.estado == 'pendiente' else 'info' if item.estado == 'en_preparacion' else 'success'}">
                                            {item.get_estado_display()}
                                        </span>
                                    </td>
                                </tr>
            """
        
        html += """
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body">
                            <h6>Acciones</h6>
                            <div class="d-grid gap-2">
        """
        
        if orden.estado == 'confirmada':
            html += f"""
                                <button class="btn btn-info btn-sm" onclick="cambiarEstadoOrden({orden.id}, 'en_preparacion')">
                                    <i class="bi bi-play-circle"></i> Iniciar Preparación
                                </button>
            """
        elif orden.estado == 'en_preparacion':
            html += f"""
                                <button class="btn btn-success btn-sm" onclick="cambiarEstadoOrden({orden.id}, 'lista')">
                                    <i class="bi bi-check-circle"></i> Marcar como Lista
                                </button>
            """
        elif orden.estado == 'lista':
            html += f"""
                                <button class="btn btn-primary btn-sm" onclick="cambiarEstadoOrden({orden.id}, 'entregada')">
                                    <i class="bi bi-check-all"></i> Marcar como Entregada
                                </button>
            """
        
        html += """
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        
        return JsonResponse({
            'success': True,
            'html': html
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@user_passes_test(es_personal_cocina)
@require_POST
def cambiar_estado_orden_ajax(request, orden_id):
    """Vista AJAX para cambiar el estado de una orden"""
    try:
        orden = get_object_or_404(Orden, id=orden_id)
        nuevo_estado = request.POST.get('estado')
        
        if nuevo_estado not in ['en_preparacion', 'lista', 'entregada']:
            return JsonResponse({
                'success': False,
                'error': 'Estado no válido'
            })
        
        # Cambiar estado
        orden.estado = nuevo_estado
        orden.save()
        
        # Crear log
        LogCocina.objects.create(
            orden=orden,
            accion=f'cambio_estado_{nuevo_estado}',
            usuario=request.user,
            detalles=f'Estado cambiado a {nuevo_estado}'
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Estado cambiado a {orden.get_estado_display()}'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@user_passes_test(es_personal_cocina)
@require_POST
def finalizar_orden(request, orden_id):
    """Finalizar una orden desde el dashboard de comandas"""
    try:
        # Obtener la orden
        orden = get_object_or_404(Orden, id=orden_id)
        
        # Verificar que la orden esté en un estado que permita finalización
        if orden.estado not in ['pendiente', 'confirmada', 'en_preparacion']:
            return JsonResponse({
                'success': False,
                'error': f'La orden ya está {orden.estado} y no puede ser finalizada.'
            })
        
        # Verificar permisos de sucursal
        if request.user.sucursal and orden.mesa.sucursal != request.user.sucursal:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para modificar esta orden.'
            })
        
        # Cambiar estado a lista para entrega
        orden.estado = 'lista'
        orden.fecha_lista = timezone.now()
        orden.save()
        
        # Registrar en log de cocina si existe el modelo
        try:
            LogCocina.objects.create(
                orden=orden,
                accion='finalizada',
                usuario=request.user,
                descripcion=f'Orden #{orden.numero_orden} marcada como lista desde dashboard de comandas'
            )
        except:
            # Si no existe el modelo LogCocina, continuar sin registrar
            pass
        
        return JsonResponse({
            'success': True,
            'message': f'Orden #{orden.numero_orden} finalizada correctamente',
            'nuevo_estado': orden.estado
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al finalizar la orden: {str(e)}'
        })

@login_required
@user_passes_test(es_personal_cocina)
@require_POST
def finalizar_servicio(request, orden_id):
    """Finalizar servicio completo: marcar orden como entregada y liberar mesa"""
    try:
        # Obtener la orden
        orden = get_object_or_404(Orden, id=orden_id)
        
        # Verificar que la orden esté en un estado que permita finalización
        if orden.estado in ['entregada', 'cancelada', 'cerrada']:
            return JsonResponse({
                'success': False,
                'message': f'La orden ya está {orden.estado} y no puede ser finalizada.'
            })
        
        # Verificar permisos de sucursal
        if request.user.sucursal and orden.mesa and orden.mesa.sucursal != request.user.sucursal:
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para modificar esta orden.'
            })
        
        # Guardar información de la mesa para la respuesta
        mesa_numero = orden.mesa.numero if orden.mesa else 'Sin mesa'
        
        # Cambiar estado de la orden a entregada
        estado_anterior = orden.estado
        orden.cambiar_estado('entregada', request.user, 'Servicio finalizado desde cocina')
        
        # La lógica de liberación de mesa ya está en el método save() del modelo Orden
        # Se ejecutará automáticamente al cambiar el estado
        
        # Registrar en log de cocina si existe el modelo
        try:
            LogCocina.objects.create(
                orden=orden,
                accion='servicio_finalizado',
                usuario=request.user,
                descripcion=f'Servicio completo finalizado para orden #{orden.numero_orden}, mesa {mesa_numero} liberada'
            )
        except:
            # Si no existe el modelo LogCocina, continuar sin registrar
            pass
        
        return JsonResponse({
            'success': True,
            'message': f'Servicio finalizado exitosamente. Mesa {mesa_numero} liberada.',
            'mesa_numero': mesa_numero,
            'estado_anterior': estado_anterior,
            'nuevo_estado': orden.estado
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al finalizar servicio: {str(e)}'
        })

def expandir_items_orden(orden):
    """
    Expande los ítems de una orden para mostrar cada unidad por separado.
    Útil para cocina cuando cada unidad puede tener características específicas.
    """
    items_expandidos = []
    
    for item in orden.items.all():
        if item.cantidad > 1 and item.observaciones:
            # Si hay cantidad > 1 y notas, crear entradas separadas
            for i in range(item.cantidad):
                item_copia = type('obj', (object,), {
                    'id': f"{item.id}_{i+1}",
                    'producto': item.producto,
                    'cantidad': 1,
                    'precio_unitario': item.precio_unitario,
                    'observaciones': item.observaciones,
                    'estado': item.estado,
                    'orden': item.orden,
                    'subtotal': item.precio_unitario,
                    'numero_unidad': i + 1,
                    'total_unidades': item.cantidad,
                    'es_expandido': True
                })()
                items_expandidos.append(item_copia)
        else:
            # Si cantidad = 1 o no hay notas, mantener como está
            item.es_expandido = False
            items_expandidos.append(item)
    
    return items_expandidos
