from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count
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
    
    context = {
        'ventas_hoy': ventas_hoy,
        'tickets_hoy': tickets_hoy,
        'promedio_venta': promedio_venta,
        'sucursal': sucursal,
        'user_permissions': user_permissions,
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
