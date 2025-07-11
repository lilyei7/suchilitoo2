from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
import json
from decimal import Decimal

from restaurant.models import ProductoVenta, Receta, RecetaInsumo, CategoriaProducto
from dashboard.models import HistorialPrecios
from accounts.models import Usuario, Sucursal
from dashboard.views.base_views import get_sidebar_context
from dashboard.models import (
    Mesa, Cliente, Orden, OrdenItem, Venta, DetalleVenta,
    CajaApertura, CajaCierre
)

@login_required
def cajero_dashboard(request):
    """Vista principal del dashboard de cajero"""
    
    # Determinar la sucursal del cajero
    user = request.user
    if not user.sucursal:
        return redirect('dashboard:principal')
    
    sucursal = user.sucursal
    
    # Obtener categorías de productos para el menú
    categorias = CategoriaProducto.objects.filter(activo=True).order_by('orden')
    
    # Obtener productos populares (los 8 más vendidos)
    productos_populares = ProductoVenta.objects.filter(
        disponible=True,
        destacado=True
    )[:8]
    
    # Estadísticas del día para el cajero
    hoy = timezone.now().date()
    
    # Estadísticas de ventas del día
    ventas_hoy = Venta.objects.filter(
        sucursal=sucursal,
        fecha_hora__date=hoy,
        anulada=False
    )
    
    total_ventas = sum(venta.total for venta in ventas_hoy)
    cantidad_tickets = ventas_hoy.count()
    promedio_venta = total_ventas / cantidad_tickets if cantidad_tickets > 0 else 0
    
    # Obtener ordenes activas
    ordenes_activas = Orden.objects.filter(
        sucursal=sucursal,
        estado__in=['abierta', 'en_proceso', 'lista'],
        pagada=False
    ).count()
    
    # Verificar si hay caja abierta para este cajero
    caja_abierta = CajaApertura.objects.filter(
        cajero=user,
        sucursal=sucursal,
        cerrada=False
    ).exists()
    
    context = {
        'sucursal': sucursal,
        'categorias': categorias,
        'productos_populares': productos_populares,
        'ventas_hoy': total_ventas,
        'tickets_hoy': cantidad_tickets,
        'promedio_venta': promedio_venta,
        'ordenes_activas': ordenes_activas,
        'caja_abierta': caja_abierta,
        'cajero_section_active': True,
        'sidebar_active': 'cajero_dashboard',
        **get_sidebar_context('cajero')
    }
    
    return render(request, 'dashboard/cajero/dashboard.html', context)

@login_required
def punto_venta(request):
    """Vista del punto de venta (POS) para cajeros"""
    
    # Verificar que el usuario sea cajero y tenga sucursal asignada
    user = request.user
    if not user.sucursal or (user.rol and user.rol.nombre not in ['cajero', 'admin', 'gerente']):
        return redirect('dashboard:principal')
    
    sucursal = user.sucursal
    
    # Obtener categorías de productos para el menú lateral
    categorias = CategoriaProducto.objects.filter(activo=True).order_by('orden')
    
    # Obtener todos los productos disponibles
    productos = ProductoVenta.objects.filter(
        disponible=True
    ).order_by('categoria__nombre', 'nombre')
    
    # Productos con receta (para calcular costos)
    productos_con_receta = ProductoVenta.objects.filter(
        disponible=True, 
        receta__isnull=False
    ).select_related('receta')
    
    context = {
        'sucursal': sucursal,
        'categorias': categorias,
        'productos': productos,
        'productos_con_receta': productos_con_receta,
        'cajero': user,
        'cajero_section_active': True,
        'sidebar_active': 'punto_venta',
        **get_sidebar_context('cajero')
    }
    
    return render(request, 'dashboard/cajero/punto_venta.html', context)

@login_required
def ordenes_activas(request):
    """Vista para gestionar órdenes activas"""
    
    # Verificar que el usuario sea cajero y tenga sucursal asignada
    user = request.user
    if not user.sucursal or (user.rol and user.rol.nombre not in ['cajero', 'admin', 'gerente']):
        return redirect('dashboard:principal')
    
    sucursal = user.sucursal
    
    # Obtener órdenes activas de la sucursal
    ordenes = Orden.objects.filter(
        sucursal=sucursal,
        estado__in=['abierta', 'en_proceso', 'lista'],
        pagada=False
    ).order_by('-fecha_hora')
    
    # Obtener mesas disponibles para cambio rápido
    mesas = Mesa.objects.filter(
        sucursal=sucursal,
        activo=True
    ).order_by('numero')
    
    context = {
        'sucursal': sucursal,
        'cajero': user,
        'ordenes_activas': ordenes,
        'mesas': mesas,
        'cajero_section_active': True,
        'sidebar_active': 'ordenes_activas',
        **get_sidebar_context('cajero')
    }
    
    return render(request, 'dashboard/cajero/ordenes_activas.html', context)

@login_required
def historial_ventas(request):
    """Vista para ver historial de ventas del cajero"""
    
    # Verificar que el usuario sea cajero y tenga sucursal asignada
    user = request.user
    if not user.sucursal or (user.rol and user.rol.nombre not in ['cajero', 'admin', 'gerente']):
        return redirect('dashboard:principal')
    
    sucursal = user.sucursal
    
    # Parámetros de filtrado
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    cajero_id = request.GET.get('cajero_id')
    metodo_pago = request.GET.get('metodo_pago')
    
    # Base query
    ventas = Venta.objects.filter(sucursal=sucursal).order_by('-fecha_hora')
    
    # Aplicar filtros
    if fecha_desde:
        ventas = ventas.filter(fecha_hora__date__gte=fecha_desde)
    
    if fecha_hasta:
        ventas = ventas.filter(fecha_hora__date__lte=fecha_hasta)
    
    if cajero_id and cajero_id.isdigit():
        ventas = ventas.filter(cajero_id=cajero_id)
    
    if metodo_pago:
        ventas = ventas.filter(metodo_pago=metodo_pago)
    
    # Si no hay filtros, mostrar ventas del día actual
    if not any([fecha_desde, fecha_hasta, cajero_id, metodo_pago]):
        ventas = ventas.filter(fecha_hora__date=timezone.now().date())
    
    # Obtener todos los cajeros para el filtro
    cajeros = Usuario.objects.filter(
        sucursal=sucursal,
        rol__nombre__in=['cajero', 'admin', 'gerente']
    )
    
    context = {
        'sucursal': sucursal,
        'cajero': user,
        'historial_ventas': ventas,
        'cajeros': cajeros,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'cajero_id': cajero_id,
        'metodo_pago': metodo_pago,
        'cajero_section_active': True,
        'sidebar_active': 'historial_ventas',
        **get_sidebar_context('cajero')
    }
    
    return render(request, 'dashboard/cajero/historial_ventas.html', context)

@login_required
def api_agregar_producto(request):
    """API para agregar un producto a una orden"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        producto_id = data.get('producto_id')
        cantidad = Decimal(str(data.get('cantidad', 1)))
        orden_id = data.get('orden_id')  # Opcional, si ya existe una orden
        
        if not producto_id or cantidad <= 0:
            return JsonResponse({'success': False, 'message': 'Datos inválidos'}, status=400)
        
        # Obtener producto
        producto = get_object_or_404(ProductoVenta, id=producto_id, disponible=True)
        
        # Calcular precio total
        precio_total = producto.precio * cantidad
        
        # Calcular costo (si tiene receta)
        costo_total = Decimal('0')
        detalles_insumos = []
        
        try:
            # Intentar obtener la receta para calcular costos
            receta = Receta.objects.get(producto=producto)
            insumos_receta = RecetaInsumo.objects.filter(receta=receta)
            
            # Calcular costo real usando PEPS
            for item in insumos_receta:
                insumo = item.insumo
                cantidad_insumo = item.cantidad * cantidad
                
                # Calcular costo usando PEPS
                costo_item, detalles = HistorialPrecios.calcular_costo_peps(
                    insumo, 
                    cantidad_insumo,
                    request.user.sucursal
                )
                
                costo_total += costo_item
                
                detalles_insumos.append({
                    'insumo_id': insumo.id,
                    'insumo_nombre': insumo.nombre,
                    'cantidad': float(cantidad_insumo),
                    'costo': float(costo_item),
                    'unidad': insumo.unidad_medida.abreviacion
                })
        except Receta.DoesNotExist:
            # Si no tiene receta, usar el costo registrado en el producto
            costo_total = producto.costo * cantidad
        
        # Calcular margen
        margen = (precio_total - costo_total) / precio_total * 100 if precio_total > 0 else 0
        
        # Si se proporciona un ID de orden, agregar el producto a esa orden
        if orden_id:
            try:
                with transaction.atomic():
                    orden = get_object_or_404(Orden, id=orden_id, pagada=False)
                    
                    # Verificar si el producto ya existe en la orden
                    item_existente = OrdenItem.objects.filter(
                        orden=orden,
                        producto=producto
                    ).first()
                    
                    if item_existente:
                        # Actualizar cantidad del item existente
                        item_existente.cantidad += cantidad
                        item_existente.save()
                    else:
                        # Crear nuevo item
                        OrdenItem.objects.create(
                            orden=orden,
                            producto=producto,
                            cantidad=cantidad,
                            precio_unitario=producto.precio
                        )
                    
                    # Recalcular totales de la orden
                    orden.calcular_totales()
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Error al agregar producto a la orden: {str(e)}'}, status=500)
        
        return JsonResponse({
            'success': True,
            'producto': {
                'id': producto.id,
                'nombre': producto.nombre,
                'codigo': producto.codigo,
                'precio_unitario': float(producto.precio),
                'cantidad': float(cantidad),
                'precio_total': float(precio_total),
                'costo_total': float(costo_total),
                'margen': float(margen)
            },
            'detalles_insumos': detalles_insumos
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def api_finalizar_venta(request):
    """API para finalizar una venta y descontar inventario"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        items = data.get('items', [])
        metodo_pago = data.get('metodo_pago', 'efectivo')
        cliente_id = data.get('cliente_id')
        cliente_nombre = data.get('cliente', 'Cliente General')
        orden_id = data.get('orden_id')  # Si viene de una orden existente
        
        if not items and not orden_id:
            return JsonResponse({'success': False, 'message': 'No hay productos en la orden'}, status=400)
        
        # Iniciar transacción
        with transaction.atomic():
            # Si tenemos cliente_id, obtenemos ese cliente, sino buscamos o creamos por nombre
            cliente = None
            if cliente_id:
                cliente = get_object_or_404(Cliente, id=cliente_id)
            elif cliente_nombre:
                cliente, _ = Cliente.objects.get_or_create(
                    nombre=cliente_nombre,
                    defaults={'ultima_visita': timezone.now()}
                )
                if cliente.ultima_visita is None:
                    cliente.ultima_visita = timezone.now()
                    cliente.save()
            
            # Si viene de una orden existente, la usamos
            if orden_id:
                orden = get_object_or_404(Orden, id=orden_id, pagada=False)
                orden_items = orden.items.all()
                
                # Procesar cada item de la orden para descontar inventario
                for item in orden_items:
                    try:
                        producto = item.producto
                        cantidad = item.cantidad
                        
                        # Descontar inventario si tiene receta
                        try:
                            receta = Receta.objects.get(producto=producto)
                            insumos_receta = RecetaInsumo.objects.filter(receta=receta)
                            
                            for item_receta in insumos_receta:
                                insumo = item_receta.insumo
                                cantidad_insumo = item_receta.cantidad * cantidad
                                
                                # Descontar stock usando PEPS
                                HistorialPrecios.descontar_stock_peps(
                                    insumo,
                                    cantidad_insumo,
                                    request.user.sucursal,
                                    f"Venta de {producto.nombre} x{cantidad}"
                                )
                                
                        except Receta.DoesNotExist:
                            pass  # Si no tiene receta, no hay que descontar inventario
                            
                    except Exception as e:
                        return JsonResponse({
                            'success': False, 
                            'message': f'Error al procesar el producto {item.producto.nombre}: {str(e)}'
                        }, status=500)
                
            else:
                # Crear una nueva orden
                orden = Orden.objects.create(
                    cliente=cliente,
                    cajero=request.user,
                    sucursal=request.user.sucursal,
                    tipo='llevar',  # Por defecto si no viene de orden previa
                    estado='cerrada',
                    pagada=True
                )
                
                # Procesar cada producto de la venta
                for item_data in items:
                    producto_id = item_data.get('producto_id')
                    cantidad = Decimal(str(item_data.get('cantidad', 1)))
                    
                    if not producto_id or cantidad <= 0:
                        continue
                    
                    # Obtener producto
                    producto = get_object_or_404(ProductoVenta, id=producto_id, disponible=True)
                    
                    # Calcular precio
                    precio_total = producto.precio * cantidad
                    
                    # Crear ítem de orden
                    orden_item = OrdenItem.objects.create(
                        orden=orden,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=producto.precio
                    )
                    
                    # Descontar inventario si tiene receta
                    try:
                        receta = Receta.objects.get(producto=producto)
                        insumos_receta = RecetaInsumo.objects.filter(receta=receta)
                        
                        costo_producto = Decimal('0')
                        for item_receta in insumos_receta:
                            insumo = item_receta.insumo
                            cantidad_insumo = item_receta.cantidad * cantidad
                            
                            # Descontar stock usando PEPS
                            costo_item, _ = HistorialPrecios.descontar_stock_peps(
                                insumo,
                                cantidad_insumo,
                                request.user.sucursal,
                                f"Venta de {producto.nombre} x{cantidad}"
                            )
                            
                            costo_producto += costo_item
                        
                        # Actualizar costo del ítem
                        orden_item.costo_unitario = costo_producto / cantidad if cantidad > 0 else 0
                        orden_item.costo_total = costo_producto
                        orden_item.save()
                        
                    except Receta.DoesNotExist:
                        # Si no tiene receta, usar el costo registrado
                        costo_producto = producto.costo * cantidad
                        orden_item.costo_unitario = producto.costo
                        orden_item.costo_total = costo_producto
                        orden_item.save()
            
            # Actualizar totales de la orden
            orden.calcular_totales()
            
            # Calcular cambio si es pago en efectivo
            monto_recibido = Decimal(str(data.get('monto_recibido', 0)))
            cambio = monto_recibido - orden.total if metodo_pago == 'efectivo' and monto_recibido > 0 else Decimal('0')
            
            # Registrar la venta
            venta = Venta.objects.create(
                orden=orden,
                cajero=request.user,
                cliente=cliente,
                sucursal=request.user.sucursal,
                metodo_pago=metodo_pago,
                monto_recibido=monto_recibido,
                cambio=cambio,
                subtotal=orden.subtotal,
                descuento=orden.descuento,
                impuestos=orden.impuestos,
                total=orden.total
            )
            
            # Crear detalles de venta a partir de los items de orden
            for item in orden.items.all():
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario,
                    precio_total=item.subtotal,
                    costo_unitario=0,  # OrdenItem no tiene costo_unitario
                    costo_total=0      # OrdenItem no tiene costo_total
                )
            
            # Si la orden tenía una mesa asignada, liberarla
            if orden.mesa:
                mesa = orden.mesa
                mesa.estado = 'disponible'
                mesa.save()
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Venta registrada exitosamente',
                'venta_id': venta.id,
                'venta_numero': f"V-{venta.id:06d}",
                'orden_numero': orden.numero,
                'fecha': venta.fecha_hora.strftime('%d/%m/%Y %H:%M:%S'),
                'cajero': request.user.get_full_name() or request.user.username,
                'sucursal': request.user.sucursal.nombre if request.user.sucursal else 'N/A',
                'total_venta': float(venta.total),
                'subtotal': float(venta.subtotal),
                'descuento': float(venta.descuento),
                'impuestos': float(venta.impuestos),
                'metodo_pago': venta.metodo_pago,
                'monto_recibido': float(venta.monto_recibido),
                'cambio': float(venta.cambio),
                'cliente': cliente.nombre if cliente else 'Cliente General'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def api_guardar_orden(request):
    """API para guardar una orden en estado abierto"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        items = data.get('items', [])
        tipo = data.get('tipo', 'mesa')
        mesa_id = data.get('mesa_id')
        cliente_id = data.get('cliente_id')
        cliente_nombre = data.get('cliente_nombre', 'Cliente General')
        notas = data.get('notas', '')
        
        if not items:
            return JsonResponse({'success': False, 'message': 'No hay productos en la orden'}, status=400)
        
        # Iniciar transacción
        with transaction.atomic():
            # Obtener cliente o crear uno nuevo
            cliente = None
            if cliente_id:
                cliente = get_object_or_404(Cliente, id=cliente_id)
            elif cliente_nombre:
                cliente, _ = Cliente.objects.get_or_create(
                    nombre=cliente_nombre,
                    defaults={'ultima_visita': timezone.now()}
                )
            
            # Obtener mesa si aplica
            mesa = None
            if tipo == 'mesa' and mesa_id:
                mesa = get_object_or_404(Mesa, id=mesa_id, sucursal=request.user.sucursal)
                
                # Actualizar estado de la mesa
                mesa.estado = 'ocupada'
                mesa.save()
            
            # Crear la orden
            orden = Orden.objects.create(
                tipo=tipo,
                mesa=mesa,
                cliente=cliente,
                cajero=request.user,
                sucursal=request.user.sucursal,
                notas=notas,
                estado='abierta'
            )
            
            # Crear items de la orden
            for item_data in items:
                producto_id = item_data.get('producto_id')
                cantidad = Decimal(str(item_data.get('cantidad', 1)))
                notas_item = item_data.get('notas', '')
                
                producto = get_object_or_404(ProductoVenta, id=producto_id)
                
                # Calcular costo del producto
                costo_unitario = Decimal('0')
                try:
                    # Intentar obtener la receta para calcular costos
                    receta = Receta.objects.get(producto=producto)
                    insumos_receta = RecetaInsumo.objects.filter(receta=receta)
                    
                    costo_total = Decimal('0')
                    for item in insumos_receta:
                        insumo = item.insumo
                        cantidad_insumo = item.cantidad * cantidad
                        
                        # Calcular costo usando PEPS
                        costo_item, _ = HistorialPrecios.calcular_costo_peps(
                            insumo, 
                            cantidad_insumo,
                            request.user.sucursal
                        )
                        
                        costo_total += costo_item
                    
                    costo_unitario = costo_total / cantidad if cantidad > 0 else 0
                    
                except Receta.DoesNotExist:
                    # Si no tiene receta, usar el costo registrado en el producto
                    costo_unitario = producto.costo
                
                # Crear el item
                OrdenItem.objects.create(
                    orden=orden,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                    observaciones=notas_item
                )
            
            # Calcular totales
            orden.calcular_totales()
            
            return JsonResponse({
                'success': True,
                'message': 'Orden guardada exitosamente',
                'orden_id': orden.id,
                'orden_numero': orden.numero,
                'fecha': orden.fecha_hora.strftime('%d/%m/%Y %H:%M:%S'),
                'subtotal': float(orden.subtotal),
                'total': float(orden.total)
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def api_get_orden(request, orden_id):
    """API para obtener detalles de una orden"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        orden = get_object_or_404(Orden, id=orden_id, sucursal=request.user.sucursal)
        
        # Detalles del cliente
        cliente_data = None
        if orden.cliente:
            cliente_data = {
                'id': orden.cliente.id,
                'nombre': orden.cliente.nombre,
                'telefono': orden.cliente.telefono,
                'email': orden.cliente.email
            }
        
        # Detalles de la mesa
        mesa_data = None
        if orden.mesa:
            mesa_data = {
                'id': orden.mesa.id,
                'numero': orden.mesa.numero,
                'nombre': orden.mesa.nombre,
                'capacidad': orden.mesa.capacidad
            }
        
        # Items de la orden
        items_data = []
        for item in orden.items.all():
            items_data.append({
                'id': item.id,
                'producto_id': item.producto.id,
                'nombre': item.producto.nombre,
                'codigo': item.producto.codigo,
                'cantidad': float(item.cantidad),
                'precio_unitario': float(item.precio_unitario),
                'precio_total': float(item.subtotal),
                'notas': item.observaciones,
                'estado': item.estado
            })
        
        return JsonResponse({
            'success': True,
            'orden': {
                'id': orden.id,
                'numero': orden.numero,
                'fecha_hora': orden.fecha_hora.strftime('%d/%m/%Y %H:%M:%S'),
                'tipo': orden.tipo,
                'estado': orden.estado,
                'notas': orden.observaciones,
                'subtotal': float(orden.subtotal),
                'descuento': float(orden.descuento),
                'impuestos': float(orden.impuestos),
                'total': float(orden.total),
                'pagada': orden.pagada,
                'cliente': cliente_data,
                'mesa': mesa_data,
                'cajero': orden.cajero.get_full_name() or orden.cajero.username,
                'mesero': orden.mesero.get_full_name() if orden.mesero else None,
                'items': items_data
            }
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def api_cambiar_estado_orden(request, orden_id):
    """API para cambiar el estado de una orden"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        nuevo_estado = data.get('estado')
        
        if not nuevo_estado:
            return JsonResponse({'success': False, 'message': 'Estado no especificado'}, status=400)
        
        # Validar estado
        estados_validos = ['abierta', 'en_proceso', 'lista', 'entregada', 'cancelada', 'cerrada']
        if nuevo_estado not in estados_validos:
            return JsonResponse({'success': False, 'message': 'Estado no válido'}, status=400)
        
        # Obtener la orden
        orden = get_object_or_404(Orden, id=orden_id, sucursal=request.user.sucursal)
        
        # No permitir cambios a órdenes pagadas excepto a administradores
        if orden.pagada and request.user.rol and request.user.rol.nombre not in ['admin', 'gerente']:
            return JsonResponse({'success': False, 'message': 'No se pueden modificar órdenes pagadas'}, status=403)
        
        # Actualizar estado
        orden.estado = nuevo_estado
        
        # Si la orden está cancelada, liberar la mesa
        if nuevo_estado == 'cancelada' and orden.mesa:
            orden.mesa.estado = 'disponible'
            orden.mesa.save()
        
        # Si la orden está entregada o cerrada, marcar los items como completados
        if nuevo_estado in ['entregada', 'cerrada']:
            for item in orden.items.all():
                item.estado = 'completado'
                item.save()
        
        orden.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Estado de la orden actualizado a {nuevo_estado}',
            'orden_id': orden.id,
            'orden_numero': orden.numero,
            'estado': orden.estado
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def api_cancelar_orden(request, orden_id):
    """API para cancelar una orden"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        motivo = data.get('motivo', '')
        
        # Obtener la orden
        orden = get_object_or_404(Orden, id=orden_id, sucursal=request.user.sucursal)
        
        # No permitir cancelar órdenes pagadas excepto a administradores
        if orden.pagada and request.user.rol and request.user.rol.nombre not in ['admin', 'gerente']:
            return JsonResponse({'success': False, 'message': 'No se pueden cancelar órdenes pagadas'}, status=403)
        
        with transaction.atomic():
            # Actualizar estado
            orden.estado = 'cancelada'
            orden.observaciones = (orden.observaciones or '') + f"\n[CANCELADA] {motivo}"
            orden.save()
            
            # Liberar mesa si existe
            if orden.mesa:
                orden.mesa.estado = 'disponible'
                orden.mesa.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Orden cancelada exitosamente',
            'orden_id': orden.id,
            'orden_numero': orden.numero
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def api_procesar_pago(request):
    """API para procesar el pago de una orden"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        orden_id = data.get('orden_id')
        metodo_pago = data.get('metodo_pago', 'efectivo')
        monto_recibido = Decimal(str(data.get('monto_recibido', 0)))
        
        if not orden_id:
            return JsonResponse({'success': False, 'message': 'ID de orden no especificado'}, status=400)
        
        # Obtener la orden
        orden = get_object_or_404(Orden, id=orden_id, sucursal=request.user.sucursal)
        
        # Verificar que la orden no esté ya pagada
        if orden.pagada:
            return JsonResponse({'success': False, 'message': 'La orden ya ha sido pagada'}, status=400)
        
        # Verificar que el monto recibido sea suficiente si es pago en efectivo
        if metodo_pago == 'efectivo' and monto_recibido < orden.total:
            return JsonResponse({
                'success': False, 
                'message': 'El monto recibido es menor al total de la orden'
            }, status=400)
        
        with transaction.atomic():
            # Procesar cada item de la orden para descontar inventario
            for item in orden.items.all():
                try:
                    producto = item.producto
                    cantidad = item.cantidad
                    
                    # Descontar inventario si tiene receta
                    try:
                        receta = Receta.objects.get(producto=producto)
                        insumos_receta = RecetaInsumo.objects.filter(receta=receta)
                        
                        costo_producto = Decimal('0')
                        for item_receta in insumos_receta:
                            insumo = item_receta.insumo
                            cantidad_insumo = item_receta.cantidad * cantidad
                            
                            # Descontar stock usando PEPS
                            costo_item, _ = HistorialPrecios.descontar_stock_peps(
                                insumo,
                                cantidad_insumo,
                                request.user.sucursal,
                                f"Venta de {producto.nombre} x{cantidad}"
                            )
                            
                            costo_producto += costo_item
                        
                        # Actualizar costo del ítem si no estaba calculado
                        if item.costo_total == 0:
                            item.costo_unitario = costo_producto / cantidad if cantidad > 0 else 0
                            item.costo_total = costo_producto
                            item.save()
                        
                    except Receta.DoesNotExist:
                        # Si no tiene receta, usar el costo registrado
                        if item.costo_total == 0:
                            item.costo_unitario = producto.costo
                            item.costo_total = producto.costo * cantidad
                            item.save()
                
                except Exception as e:
                    return JsonResponse({
                        'success': False, 
                        'message': f'Error al procesar el producto {item.producto.nombre}: {str(e)}'
                    }, status=500)
            
            # Calcular cambio si es pago en efectivo
            cambio = monto_recibido - orden.total if metodo_pago == 'efectivo' and monto_recibido > 0 else Decimal('0')
            
            # Actualizar estado de la orden
            orden.estado = 'cerrada'
            orden.pagada = True
            orden.save()
            
            # Liberar mesa si existe
            if orden.mesa:
                orden.mesa.estado = 'disponible'
                orden.mesa.save()
            
            # Registrar la venta
            venta = Venta.objects.create(
                orden=orden,
                cajero=request.user,
                cliente=orden.cliente,
                sucursal=request.user.sucursal,
                metodo_pago=metodo_pago,
                monto_recibido=monto_recibido,
                cambio=cambio,
                subtotal=orden.subtotal,
                descuento=orden.descuento,
                impuestos=orden.impuestos,
                total=orden.total
            )
            
            # Crear detalles de venta a partir de los items de orden
            for item in orden.items.all():
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario,
                    precio_total=item.subtotal,
                    costo_unitario=0,  # OrdenItem no tiene costo_unitario
                    costo_total=0      # OrdenItem no tiene costo_total
                )
            
            # Actualizar última visita del cliente
            if orden.cliente:
                orden.cliente.ultima_visita = timezone.now()
                orden.cliente.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Pago procesado exitosamente',
                'venta_id': venta.id,
                'venta_numero': f"V-{venta.id:06d}",
                'orden_numero': orden.numero,
                'fecha': venta.fecha_hora.strftime('%d/%m/%Y %H:%M:%S'),
                'total': float(venta.total),
                'metodo_pago': venta.metodo_pago,
                'monto_recibido': float(venta.monto_recibido),
                'cambio': float(venta.cambio)
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def api_buscar_clientes(request):
    """API para buscar clientes"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        q = request.GET.get('q', '')
        
        if not q or len(q) < 2:
            return JsonResponse({'success': True, 'clientes': []})
        
        # Buscar clientes que coincidan con el término
        clientes = Cliente.objects.filter(
            nombre__icontains=q
        ).order_by('-ultima_visita')[:10]
        
        clientes_data = []
        for cliente in clientes:
            clientes_data.append({
                'id': cliente.id,
                'nombre': cliente.nombre,
                'telefono': cliente.telefono,
                'email': cliente.email,
                'ultima_visita': cliente.ultima_visita.strftime('%d/%m/%Y') if cliente.ultima_visita else None
            })
        
        return JsonResponse({
            'success': True,
            'clientes': clientes_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def api_guardar_cliente(request):
    """API para guardar un nuevo cliente o actualizar uno existente"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        cliente_id = data.get('cliente_id')
        nombre = data.get('nombre')
        telefono = data.get('telefono')
        email = data.get('email')
        direccion = data.get('direccion')
        notas = data.get('notas')
        
        if not nombre:
            return JsonResponse({'success': False, 'message': 'El nombre del cliente es obligatorio'}, status=400)
        
        # Actualizar cliente existente o crear uno nuevo
        if cliente_id:
            cliente = get_object_or_404(Cliente, id=cliente_id)
            cliente.nombre = nombre
            cliente.telefono = telefono
            cliente.email = email
            cliente.direccion = direccion
            cliente.notas = notas
            cliente.save()
            mensaje = 'Cliente actualizado exitosamente'
        else:
            cliente = Cliente.objects.create(
                nombre=nombre,
                telefono=telefono,
                email=email,
                direccion=direccion,
                notas=notas,
                fecha_registro=timezone.now(),
                ultima_visita=timezone.now()
            )
            mensaje = 'Cliente guardado exitosamente'
        
        return JsonResponse({
            'success': True,
            'message': mensaje,
            'cliente': {
                'id': cliente.id,
                'nombre': cliente.nombre,
                'telefono': cliente.telefono,
                'email': cliente.email,
                'direccion': cliente.direccion,
                'notas': cliente.notas
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def api_get_mesas(request):
    """API para obtener las mesas disponibles de la sucursal"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        # Obtener todas las mesas de la sucursal
        mesas = Mesa.objects.filter(
            sucursal=request.user.sucursal,
            activo=True
        ).order_by('numero')
        
        mesas_data = []
        for mesa in mesas:
            mesas_data.append({
                'id': mesa.id,
                'numero': mesa.numero,
                'nombre': mesa.nombre,
                'capacidad': mesa.capacidad,
                'estado': mesa.estado,
                'disponible': mesa.estado == 'disponible'
            })
        
        return JsonResponse({
            'success': True,
            'mesas': mesas_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def apertura_caja(request):
    """Vista para la apertura de caja"""
    
    # Verificar que el usuario sea cajero y tenga sucursal asignada
    user = request.user
    if not user.sucursal or (user.rol and user.rol.nombre not in ['cajero', 'admin', 'gerente']):
        return redirect('dashboard:principal')
    
    sucursal = user.sucursal
    
    # Verificar si ya hay una caja abierta
    caja_abierta = CajaApertura.objects.filter(
        cajero=user,
        sucursal=sucursal,
        cerrada=False
    ).first()
    
    if caja_abierta:
        return redirect('dashboard:cajero_dashboard')
    
    # Procesar formulario de apertura
    if request.method == 'POST':
        monto_inicial = Decimal(request.POST.get('monto_inicial', '0'))
        notas = request.POST.get('notas', '')
        
        # Crear apertura de caja
        CajaApertura.objects.create(
            cajero=user,
            sucursal=sucursal,
            monto_inicial=monto_inicial,
            notas=notas
        )
        
        return redirect('dashboard:cajero_dashboard')
    
    context = {
        'sucursal': sucursal,
        'cajero': user,
        'cajero_section_active': True,
        'sidebar_active': 'apertura_caja',
        **get_sidebar_context('cajero')
    }
    
    return render(request, 'dashboard/cajero/apertura_caja.html', context)

@login_required
def cierre_caja(request):
    """Vista para el cierre de caja"""
    
    # Verificar que el usuario sea cajero y tenga sucursal asignada
    user = request.user
    if not user.sucursal or (user.rol and user.rol.nombre not in ['cajero', 'admin', 'gerente']):
        return redirect('dashboard:principal')
    
    sucursal = user.sucursal
    
    # Verificar si hay una caja abierta
    caja_abierta = CajaApertura.objects.filter(
        cajero=user,
        sucursal=sucursal,
        cerrada=False
    ).first()
    
    if not caja_abierta:
        return redirect('dashboard:cajero_dashboard')
    
    # Obtener las ventas desde la apertura
    ventas = Venta.objects.filter(
        cajero=user,
        sucursal=sucursal,
        fecha_hora__gte=caja_abierta.fecha_hora,
        anulada=False
    )
    
    # Calcular totales por método de pago
    ventas_efectivo = sum(v.total for v in ventas.filter(metodo_pago='efectivo'))
    ventas_tarjeta = sum(v.total for v in ventas.filter(metodo_pago='tarjeta'))
    ventas_otros = sum(v.total for v in ventas.filter(metodo_pago__in=['transferencia', 'credito', 'mixto']))
    total_ventas = ventas_efectivo + ventas_tarjeta + ventas_otros
    
    # Calcular monto que debe haber en caja
    monto_sistema = caja_abierta.monto_inicial + ventas_efectivo
    
    # Procesar formulario de cierre
    if request.method == 'POST':
        monto_fisico = Decimal(request.POST.get('monto_fisico', '0'))
        notas = request.POST.get('notas', '')
        
        # Crear cierre de caja
        CajaCierre.objects.create(
            apertura=caja_abierta,
            monto_sistema=monto_sistema,
            monto_fisico=monto_fisico,
            diferencia=monto_fisico - monto_sistema,
            ventas_efectivo=ventas_efectivo,
            ventas_tarjeta=ventas_tarjeta,
            ventas_otros=ventas_otros,
            total_ventas=total_ventas,
            notas=notas
        )
        
        return redirect('dashboard:cajero_dashboard')
    
    context = {
        'sucursal': sucursal,
        'cajero': user,
        'caja_abierta': caja_abierta,
        'monto_sistema': monto_sistema,
        'ventas_efectivo': ventas_efectivo,
        'ventas_tarjeta': ventas_tarjeta,
        'ventas_otros': ventas_otros,
        'total_ventas': total_ventas,
        'cantidad_ventas': ventas.count(),
        'cajero_section_active': True,
        'sidebar_active': 'cierre_caja',
        **get_sidebar_context('cajero')
    }
    
    return render(request, 'dashboard/cajero/cierre_caja.html', context)

@login_required
def api_anular_venta(request, venta_id):
    """API para anular una venta"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        motivo = data.get('motivo', '')
        
        if not motivo:
            return JsonResponse({'success': False, 'message': 'El motivo de anulación es obligatorio'}, status=400)
        
        # Obtener la venta
        venta = get_object_or_404(Venta, id=venta_id, sucursal=request.user.sucursal)
        
        # Verificar si el usuario tiene permisos (solo admin y gerente)
        if request.user.rol and request.user.rol.nombre not in ['admin', 'gerente']:
            return JsonResponse({'success': False, 'message': 'No tiene permisos para anular ventas'}, status=403)
        
        with transaction.atomic():
            # Marcar venta como anulada
            venta.anulada = True
            venta.motivo_anulacion = motivo
            venta.save()
            
            # Si la venta tiene orden, marcar como cancelada
            if venta.orden:
                venta.orden.estado = 'cancelada'
                venta.orden.pagada = False
                venta.orden.save()
            
            # Reintegrar stock si es necesario
            # En una implementación real, esto requeriría un proceso más complejo
            # para reintegrar stock correctamente
            
        return JsonResponse({
            'success': True,
            'message': 'Venta anulada exitosamente',
            'venta_id': venta.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def api_reimprimir_ticket(request, venta_id):
    """API para reimprimir un ticket de venta"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    try:
        # Obtener la venta
        venta = get_object_or_404(Venta, id=venta_id, sucursal=request.user.sucursal)
        
        # Obtener detalles de la venta
        detalles = venta.detalles.all()
        
        items = []
        for detalle in detalles:
            items.append({
                'producto_id': detalle.producto.id,
                'nombre': detalle.producto.nombre,
                'codigo': detalle.producto.codigo,
                'cantidad': float(detalle.cantidad),
                'precio_unitario': float(detalle.precio_unitario),
                'precio_total': float(detalle.precio_total)
            })
        
        # Cliente
        cliente_data = None
        if venta.cliente:
            cliente_data = {
                'id': venta.cliente.id,
                'nombre': venta.cliente.nombre,
                'telefono': venta.cliente.telefono
            }
        
        return JsonResponse({
            'success': True,
            'ticket': {
                'venta_id': venta.id,
                'venta_numero': f"V-{venta.id:06d}",
                'orden_numero': venta.orden.numero if venta.orden else '',
                'fecha': venta.fecha_hora.strftime('%d/%m/%Y %H:%M:%S'),
                'cajero': venta.cajero.get_full_name() or venta.cajero.username,
                'sucursal': venta.sucursal.nombre,
                'cliente': cliente_data,
                'metodo_pago': venta.metodo_pago,
                'subtotal': float(venta.subtotal),
                'descuento': float(venta.descuento),
                'impuestos': float(venta.impuestos),
                'total': float(venta.total),
                'monto_recibido': float(venta.monto_recibido),
                'cambio': float(venta.cambio),
                'items': items,
                'anulada': venta.anulada
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def admin_mesas(request):
    """Vista para administrar mesas"""
    
    # Verificar permisos
    if request.user.rol and request.user.rol.nombre not in ['admin', 'gerente']:
        return redirect('dashboard:principal')
    
    sucursal = request.user.sucursal
    
    # Obtener todas las mesas
    mesas = Mesa.objects.filter(sucursal=sucursal).order_by('numero')
    
    # Procesar formulario
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'crear':
            numero = request.POST.get('numero')
            nombre = request.POST.get('nombre')
            capacidad = request.POST.get('capacidad', 4)
            
            # Validar que no exista una mesa con el mismo número
            if Mesa.objects.filter(sucursal=sucursal, numero=numero).exists():
                messages.error(request, 'Ya existe una mesa con ese número')
            else:
                Mesa.objects.create(
                    sucursal=sucursal,
                    numero=numero,
                    nombre=nombre,
                    capacidad=capacidad,
                    estado='disponible',
                    activa=True
                )
                messages.success(request, 'Mesa creada exitosamente')
        
        elif accion == 'editar':
            mesa_id = request.POST.get('mesa_id')
            numero = request.POST.get('numero')
            nombre = request.POST.get('nombre')
            capacidad = request.POST.get('capacidad')
            estado = request.POST.get('estado')
            
            mesa = get_object_or_404(Mesa, id=mesa_id, sucursal=sucursal)
            
            # Validar que no exista otra mesa con el mismo número
            if Mesa.objects.filter(sucursal=sucursal, numero=numero).exclude(id=mesa_id).exists():
                messages.error(request, 'Ya existe otra mesa con ese número')
            else:
                mesa.numero = numero
                mesa.nombre = nombre
                mesa.capacidad = capacidad
                mesa.estado = estado
                mesa.save()
                messages.success(request, 'Mesa actualizada exitosamente')
        
        elif accion == 'eliminar':
            mesa_id = request.POST.get('mesa_id')
            mesa = get_object_or_404(Mesa, id=mesa_id, sucursal=sucursal)
            
            # Verificar que no tenga órdenes activas
            if Orden.objects.filter(mesa=mesa, estado__in=['abierta', 'en_proceso', 'lista']).exists():
                messages.error(request, 'No se puede eliminar la mesa porque tiene órdenes activas')
            else:
                mesa.delete()
                messages.success(request, 'Mesa eliminada exitosamente')
        
        return redirect('dashboard:admin_mesas')
    
    context = {
        'sucursal': sucursal,
        'mesas': mesas,
        'cajero_section_active': True,
        'sidebar_active': 'admin_mesas',
        **get_sidebar_context('cajero')
    }
    
    return render(request, 'dashboard/cajero/admin_mesas.html', context)
