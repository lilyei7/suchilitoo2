from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count
from decimal import Decimal
import json

# Importar modelos desde los diferentes apps
from restaurant.models import ProductoVenta
from dashboard.models_ventas import Orden, OrdenItem, Venta
from accounts.models import Sucursal

# Importar el sistema de permisos personalizado
from .permissions import cajero_required, admin_or_gerente_required, get_user_permissions

def login_view(request):
    """Vista de login dedicada para cajeros, gerentes y admins - tablet optimized"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Verificar que el usuario tenga un rol permitido
            user_permissions = get_user_permissions(user)
            allowed_roles = ['cajero', 'gerente', 'admin']
            user_role = getattr(user.rol, 'nombre', None) if user.rol else None
            
            # Permitir acceso a cajeros, gerentes y admins
            if (user.is_superuser or 
                user_role in allowed_roles or 
                user.groups.filter(name__in=allowed_roles).exists()):
                
                login(request, user)
                messages.success(request, f'Bienvenido, {user.first_name or user.username}!')
                return redirect('cajero:dashboard')
            else:
                messages.error(request, 'No tienes permisos para acceder al sistema de cajero.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'cajero/login.html')

def logout_view(request):
    """Logout para cajeros"""
    logout(request)
    return redirect('cajero:login')

@cajero_required
def dashboard(request):
    """Dashboard principal del cajero - tablet optimized"""
    
    # Obtener estadísticas del día
    hoy = timezone.now().date()
    
    # Ventas del día
    ventas_hoy = Venta.objects.filter(
        fecha_hora__date=hoy,
        sucursal=request.user.sucursal
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Tickets emitidos
    tickets_hoy = Orden.objects.filter(
        fecha_hora__date=hoy,
        sucursal=request.user.sucursal
    ).count()
    
    # Venta promedio
    promedio_venta = (ventas_hoy / tickets_hoy) if tickets_hoy > 0 else 0
    
    # Obtener permisos del usuario
    user_permissions = get_user_permissions(request.user)
    
    # Obtener sucursal del usuario
    sucursal = request.user.sucursal
    
    # Obtener notificaciones pendientes
    from mesero.models import NotificacionCuenta
    notificaciones_pendientes = NotificacionCuenta.objects.filter(
        estado__in=['pendiente', 'procesando']
    ).count()
    
    context = {
        'ventas_hoy': ventas_hoy,
        'tickets_hoy': tickets_hoy,
        'promedio_venta': promedio_venta,
        'sucursal': sucursal,
        'user_permissions': user_permissions,
        'notificaciones_pendientes': notificaciones_pendientes,
    }
    
    return render(request, 'cajero/dashboard.html', context)

@cajero_required
def punto_venta(request):
    """Punto de venta moderno - tablet optimized"""
    
    # Obtener productos activos
    productos = ProductoVenta.objects.filter(disponible=True).order_by('categoria', 'nombre')
    
    context = {
        'productos': productos,
    }
    
    return render(request, 'cajero/pos.html', context)

@cajero_required
def crear_pedido(request):
    """Vista para que el cajero cree pedidos como si fuera mesero"""
    from mesero.models import Mesa
    from collections import defaultdict
    
    # Obtener mesas disponibles
    mesas = Mesa.objects.filter(
        sucursal=request.user.sucursal,
        activo=True
    ).order_by('numero')
    
    # Obtener productos activos organizados por categoría
    productos_activos = ProductoVenta.objects.filter(
        disponible=True
    ).select_related('categoria').order_by('categoria__nombre', 'nombre')
    
    # Organizar productos por categoría
    productos_por_categoria = defaultdict(list)
    for producto in productos_activos:
        categoria_nombre = producto.categoria.nombre if producto.categoria else 'Sin Categoría'
        productos_por_categoria[categoria_nombre].append({
            'id': producto.id,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'precio': float(producto.precio),
            'imagen': producto.imagen.url if producto.imagen else None,
        })
    
    context = {
        'mesas': mesas,
        'productos_por_categoria': dict(productos_por_categoria),
    }
    
    return render(request, 'cajero/crear_pedido.html', context)

@cajero_required
def notificaciones_cuenta(request):
    """Vista para gestionar notificaciones de cuenta solicitada"""
    from mesero.models import NotificacionCuenta
    
    # Obtener notificaciones pendientes
    notificaciones = NotificacionCuenta.objects.filter(
        estado__in=['pendiente', 'procesando']
    ).select_related('orden', 'orden__mesa', 'mesero').order_by('-fecha_creacion')
    
    context = {
        'notificaciones': notificaciones,
    }
    
    return render(request, 'cajero/notificaciones_cuenta.html', context)

@cajero_required
def procesar_cuenta(request, notificacion_id):
    """Vista para procesar una cuenta solicitada"""
    from mesero.models import NotificacionCuenta
    
    notificacion = get_object_or_404(NotificacionCuenta, id=notificacion_id)
    orden = notificacion.orden
    
    # Calcular total de la orden
    total = sum(item.subtotal for item in orden.items.all())
    
    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago')
        monto_recibido = request.POST.get('monto_recibido')
        referencia = request.POST.get('referencia', '')
        
        try:
            # Actualizar la orden con información de pago
            orden.metodo_pago_cuenta = metodo_pago
            orden.monto_recibido = Decimal(monto_recibido) if monto_recibido else total
            orden.referencia_pago = referencia
            orden.cajero_procesa_cuenta = request.user
            orden.fecha_procesamiento_cuenta = timezone.now()
            orden.cuenta_procesada = True
            orden.ticket_generado = True
            
            # Calcular cambio si es efectivo
            if metodo_pago == 'efectivo':
                cambio = orden.monto_recibido - total
                orden.cambio_dado = cambio if cambio > 0 else Decimal('0.00')
            
            orden.save()
            
            # Actualizar la notificación
            notificacion.estado = 'completada'
            notificacion.cajero = request.user
            notificacion.fecha_procesamiento = timezone.now()
            notificacion.save()
            
            messages.success(request, f'Cuenta procesada exitosamente. Total: ${total}')
            return redirect('cajero:notificaciones_cuenta')
            
        except Exception as e:
            messages.error(request, f'Error al procesar cuenta: {str(e)}')
    
    context = {
        'notificacion': notificacion,
        'orden': orden,
        'total': total,
        'items': orden.items.all(),
    }
    
    return render(request, 'cajero/procesar_cuenta.html', context)

@cajero_required
def historial_ventas(request):
    """Historial de ventas del cajero"""
    
    # Obtener ventas del día actual
    hoy = timezone.now().date()
    ventas = Orden.objects.filter(
        fecha_hora__date=hoy,
        sucursal=request.user.sucursal
    ).order_by('-fecha_hora')
    
    # Obtener permisos del usuario
    user_permissions = get_user_permissions(request.user)
    
    context = {
        'ventas': ventas,
        'fecha': hoy,
        'user_permissions': user_permissions,
    }
    
    return render(request, 'cajero/historial_ventas.html', context)

# APIs para el POS

@cajero_required
def api_productos(request):
    """API para obtener productos por categoría"""
    categoria = request.GET.get('categoria', '')
    
    productos = ProductoVenta.objects.filter(disponible=True)
    if categoria:
        productos = productos.filter(categoria=categoria)
    
    productos_data = []
    for producto in productos:
        productos_data.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'categoria': producto.categoria,
            'imagen': producto.imagen.url if producto.imagen else None,
        })
    
    return JsonResponse({'productos': productos_data})

@csrf_exempt
@cajero_required
def api_guardar_orden(request):
    """API para guardar una orden"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        
        if not items:
            return JsonResponse({'error': 'No hay items en la orden'}, status=400)
        
        # Crear la orden
        orden = Orden.objects.create(
            cajero=request.user,
            sucursal=request.user.sucursal,
            total=0,  # Se calculará después
            estado='abierta'
        )
        
        total = 0
        for item_data in items:
            producto = ProductoVenta.objects.get(id=item_data['producto_id'])
            cantidad = item_data['cantidad']
            subtotal = producto.precio * cantidad
            
            OrdenItem.objects.create(
                orden=orden,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )
            
            total += subtotal
        
        # Actualizar total de la orden
        orden.total = total
        orden.save()
        
        return JsonResponse({
            'success': True,
            'orden_id': orden.id,
            'total': float(total)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@cajero_required
def api_procesar_pago(request):
    """API para procesar el pago de una orden"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        orden_id = data.get('orden_id')
        metodo_pago = data.get('metodo_pago')
        monto_recibido = data.get('monto_recibido')
        referencia = data.get('referencia', '')
        
        orden = Orden.objects.get(id=orden_id)
        
        # Crear la venta
        venta = Venta.objects.create(
            orden=orden,
            metodo_pago=metodo_pago,
            monto_recibido=monto_recibido or orden.total,
            cajero=request.user,
            sucursal=request.user.sucursal
        )
        
        # Actualizar estado de la orden
        orden.estado = 'cerrada'
        orden.save()
        
        return JsonResponse({
            'success': True,
            'venta_id': venta.id,
            'cambio': float(venta.cambio) if venta.cambio else 0
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@cajero_required
def api_crear_pedido(request):
    """API para que el cajero cree pedidos usando el sistema del mesero"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        from mesero.models import Orden, OrdenItem, Mesa
        
        data = json.loads(request.body)
        mesa_id = data.get('mesa_id')
        items = data.get('items', [])
        notas = data.get('notas', '')
        
        if not items:
            return JsonResponse({'error': 'No hay items en el pedido'}, status=400)
        
        # Obtener la mesa
        mesa = Mesa.objects.get(id=mesa_id) if mesa_id else None
        
        # Crear la orden usando el modelo del mesero
        orden = Orden.objects.create(
            mesa=mesa,
            mesero=request.user,  # El cajero actúa como mesero
            sucursal=request.user.sucursal,
            estado='activa',
            notas=notas
        )
        
        # Crear los items de la orden
        total = Decimal('0.00')
        for item_data in items:
            producto = ProductoVenta.objects.get(id=item_data['producto_id'])
            cantidad = int(item_data['cantidad'])
            precio_unitario = producto.precio
            subtotal = precio_unitario * cantidad
            
            OrdenItem.objects.create(
                orden=orden,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal
            )
            
            total += subtotal
        
        # Actualizar el total de la orden
        orden.total = total
        orden.save()
        
        # Marcar la mesa como ocupada si existe
        if mesa:
            mesa.estado = 'ocupada'
            mesa.save()
        
        return JsonResponse({
            'success': True,
            'orden_id': orden.id,
            'numero_orden': orden.numero_orden,
            'total': float(total),
            'mensaje': f'Pedido creado exitosamente - Orden #{orden.numero_orden}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@cajero_required
def api_procesar_cuenta(request, notificacion_id):
    """API para procesar una cuenta solicitada"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        from mesero.models import NotificacionCuenta
        
        data = json.loads(request.body)
        metodo_pago = data.get('metodo_pago')
        monto_recibido = data.get('monto_recibido')
        referencia = data.get('referencia', '')
        
        notificacion = NotificacionCuenta.objects.get(id=notificacion_id)
        orden = notificacion.orden
        
        # Calcular total
        total = sum(item.subtotal for item in orden.items.all())
        
        # Actualizar orden
        orden.metodo_pago_cuenta = metodo_pago
        orden.monto_recibido = Decimal(str(monto_recibido)) if monto_recibido else total
        orden.referencia_pago = referencia
        orden.cajero_procesa_cuenta = request.user
        orden.fecha_procesamiento_cuenta = timezone.now()
        orden.cuenta_procesada = True
        orden.ticket_generado = True
        
        # Calcular cambio
        cambio = Decimal('0.00')
        if metodo_pago == 'efectivo':
            cambio = orden.monto_recibido - total
            orden.cambio_dado = cambio if cambio > 0 else Decimal('0.00')
        
        orden.save()
        
        # Actualizar notificación
        notificacion.estado = 'completada'
        notificacion.cajero = request.user
        notificacion.fecha_procesamiento = timezone.now()
        notificacion.save()
        
        return JsonResponse({
            'success': True,
            'total': float(total),
            'cambio': float(cambio),
            'mensaje': f'Cuenta procesada exitosamente. Total: ${total}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@admin_or_gerente_required
def api_cancelar_venta(request, venta_id):
    """API para cancelar ventas - solo gerentes y admins"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        venta = Venta.objects.get(id=venta_id, sucursal=request.user.sucursal)
        
        # Verificar que la venta se pueda cancelar
        if venta.anulada:
            return JsonResponse({'error': 'La venta ya está cancelada'}, status=400)
        
        # Cancelar la venta
        venta.anulada = True
        venta.motivo_anulacion = f'Cancelada por {request.user.get_full_name() or request.user.username}'
        venta.save()
        
        # Actualizar el estado de la orden
        if venta.orden:
            venta.orden.estado = 'cancelada'
            venta.orden.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Venta cancelada exitosamente'
        })
        
    except Venta.DoesNotExist:
        return JsonResponse({'error': 'Venta no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
