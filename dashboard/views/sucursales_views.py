from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
import json

from accounts.models import Sucursal, Usuario
from .base_views import get_sidebar_context, is_admin_or_manager

@login_required
def sucursales_view(request):
    """Vista principal para gestión de sucursales"""
    # Obtener todas las sucursales
    sucursales = Sucursal.objects.all().order_by('nombre')
    
    # Calcular estadísticas
    total_sucursales = sucursales.count()
    sucursales_activas = sucursales.filter(activa=True).count()
    
    context = {
        'sucursales': sucursales,
        'total_sucursales': total_sucursales,
        'sucursales_activas': sucursales_activas,
        **get_sidebar_context('sucursales')
    }
    
    return render(request, 'dashboard/sucursales.html', context)

@login_required
@user_passes_test(is_admin_or_manager)
def crear_sucursal(request):
    """Vista para crear una nueva sucursal"""
    if request.method == 'POST':
        try:            # Obtener datos del formulario
            nombre = request.POST.get('nombre', '').strip()
            direccion = request.POST.get('direccion', '').strip()
            telefono = request.POST.get('telefono', '').strip()
            email = request.POST.get('email', '').strip()
            fecha_apertura_str = request.POST.get('fecha_apertura', '')
            
            # Procesar fecha de apertura
            fecha_apertura = date.today()  # Default a hoy
            if fecha_apertura_str:
                try:
                    from datetime import datetime
                    fecha_apertura = datetime.strptime(fecha_apertura_str, '%Y-%m-%d').date()
                except ValueError:
                    fecha_apertura = date.today()
            
            # Validaciones básicas
            if not all([nombre, direccion, telefono]):
                return JsonResponse({
                    'success': False,
                    'message': 'Los campos nombre, dirección y teléfono son obligatorios'
                })
            
            # Verificar que no exista una sucursal con el mismo nombre
            if Sucursal.objects.filter(nombre__iexact=nombre).exists():                return JsonResponse({
                    'success': False,
                    'message': f'Ya existe una sucursal con el nombre "{nombre}"'
                })
            
            # Crear la sucursal
            with transaction.atomic():                sucursal = Sucursal.objects.create(
                    nombre=nombre,
                    direccion=direccion,
                    telefono=telefono,
                    email=email if email else f'{nombre.lower().replace(" ", "")}@sushirestaurant.com',
                    fecha_apertura=fecha_apertura,
                    activa=True
                )
            
            return JsonResponse({
                'success': True,
                'message': f'Sucursal "{nombre}" creada exitosamente',
                'sucursal_id': sucursal.id
            })
            
        except Exception as e:
            print(f"Error creando sucursal: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })

@login_required
def detalle_sucursal(request, sucursal_id):
    """Vista para ver detalles de una sucursal"""
    try:
        sucursal = get_object_or_404(Sucursal, id=sucursal_id)
        
        # Obtener empleados de la sucursal
        empleados = Usuario.objects.filter(sucursal=sucursal).select_related('rol')
          # Preparar datos de la sucursal
        sucursal_data = {
            'id': sucursal.id,
            'nombre': sucursal.nombre,
            'direccion': sucursal.direccion,
            'telefono': sucursal.telefono,
            'email': sucursal.email,
            'activa': sucursal.activa,
            'fecha_apertura': sucursal.fecha_apertura.strftime('%d/%m/%Y') if sucursal.fecha_apertura else None,
            'created_at': sucursal.created_at.strftime('%d/%m/%Y %H:%M')
        }
        
        # Preparar datos de empleados
        empleados_data = []
        for empleado in empleados:
            empleados_data.append({
                'id': empleado.id,
                'username': empleado.username,
                'first_name': empleado.first_name,
                'last_name': empleado.last_name,
                'email': empleado.email,
                'rol': empleado.rol.nombre if empleado.rol else 'Sin rol',
                'is_active': empleado.is_active,
                'last_login': empleado.last_login.strftime('%d/%m/%Y %H:%M') if empleado.last_login else 'Nunca'
            })
        
        return JsonResponse({
            'success': True,
            'sucursal': sucursal_data,
            'empleados': empleados_data
        })
        
    except Exception as e:
        print(f"Error obteniendo detalle de sucursal: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def editar_sucursal(request, sucursal_id):
    """Vista para editar una sucursal existente"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        sucursal = get_object_or_404(Sucursal, id=sucursal_id)        # Obtener datos del formulario
        nombre = request.POST.get('nombre', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email = request.POST.get('email', '').strip()
        fecha_apertura_str = request.POST.get('fecha_apertura', '')
        activa = request.POST.get('activa') == 'true'
        
        # Procesar fecha de apertura si se proporciona
        fecha_apertura = None
        if fecha_apertura_str:
            try:
                from datetime import datetime
                fecha_apertura = datetime.strptime(fecha_apertura_str, '%Y-%m-%d').date()
            except ValueError:
                fecha_apertura = None
          # Validaciones básicas
        if not all([nombre, direccion, telefono]):
            return JsonResponse({'success': False, 'message': 'Los campos nombre, dirección y teléfono son obligatorios'})
        
        # Verificar que no exista otra sucursal con el mismo nombre
        if Sucursal.objects.filter(nombre__iexact=nombre).exclude(id=sucursal_id).exists():
            return JsonResponse({'success': False, 'message': f'Ya existe otra sucursal con el nombre "{nombre}"'})
        
        with transaction.atomic():
            # Actualizar datos de la sucursal
            sucursal.nombre = nombre
            sucursal.direccion = direccion
            sucursal.telefono = telefono
            sucursal.email = email if email else None
            if fecha_apertura:
                sucursal.fecha_apertura = fecha_apertura
            sucursal.activa = activa
            sucursal.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Sucursal "{nombre}" actualizada exitosamente'
        })
        
    except Exception as e:
        print(f"Error editando sucursal: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def eliminar_sucursal(request, sucursal_id):
    """Vista para eliminar una sucursal"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        sucursal = get_object_or_404(Sucursal, id=sucursal_id)
        
        # Verificar si hay empleados asignados a esta sucursal
        empleados_count = Usuario.objects.filter(sucursal=sucursal).count()
        
        if empleados_count > 0:
            return JsonResponse({
                'success': False,
                'message': f'No se puede eliminar la sucursal porque tiene {empleados_count} empleado(s) asignado(s)'
            })
        
        nombre_sucursal = sucursal.nombre
        sucursal.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Sucursal "{nombre_sucursal}" eliminada exitosamente'
        })
        
    except Exception as e:
        print(f"Error eliminando sucursal: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_or_manager)
def toggle_estado_sucursal(request, sucursal_id):
    """Vista para activar/desactivar una sucursal"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        sucursal = get_object_or_404(Sucursal, id=sucursal_id)
        
        # Cambiar el estado
        sucursal.activa = not sucursal.activa
        sucursal.save()
        
        estado = "activada" if sucursal.activa else "desactivada"
        
        return JsonResponse({
            'success': True,
            'message': f'Sucursal "{sucursal.nombre}" {estado} exitosamente',
            'nueva_estado': sucursal.activa
        })
        
    except Exception as e:
        print(f"Error cambiando estado de sucursal: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })
