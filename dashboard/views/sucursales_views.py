
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
from dashboard.utils.permissions import require_module_access
from dashboard.models_ventas import Mesa

def is_admin_only(user):
    """Función para verificar que solo admin y superuser tengan acceso"""
    return user.is_superuser or (user.rol and user.rol.nombre == 'admin')

@login_required
@user_passes_test(is_admin_only)
def toggle_activa_mesa(request, mesa_id):
    """Vista para alternar el campo activa de una mesa"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    try:
        mesa = get_object_or_404(Mesa, id=mesa_id)
        mesa.activa = not mesa.activa
        mesa.save()
        estado = 'activada' if mesa.activa else 'inactivada'
        return JsonResponse({
            'success': True,
            'message': f'Mesa "{mesa.numero}" {estado} exitosamente',
            'nueva_activa': mesa.activa
        })
    except Exception as e:
        print(f"Error alternando activa mesa: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })


def is_admin_only(user):
    """Función para verificar que solo admin y superuser tengan acceso"""
    return user.is_superuser or (user.rol and user.rol.nombre == 'admin')

@login_required
@require_module_access('sucursales')
def sucursales_view(request):
    """Vista principal para gestión de sucursales"""
    # Obtener todas las sucursales
    sucursales = Sucursal.objects.all().order_by('nombre')
    
    # Calcular estadísticas
    total_sucursales = sucursales.count()
    sucursales_activas = sucursales.filter(activa=True).count()
    
    # Agregar estadísticas de mesas para cada sucursal
    for sucursal in sucursales:
        # Contar mesas disponibles
        mesas_disponibles = sucursal.mesas.filter(estado='disponible', activa=True).count()
        sucursal.mesas_disponibles_count = mesas_disponibles
    
    context = {
        'sucursales': sucursales,
        'total_sucursales': total_sucursales,
        'sucursales_activas': sucursales_activas,
        **get_sidebar_context('sucursales')
    }
    
    return render(request, 'dashboard/sucursales.html', context)

@login_required
@user_passes_test(is_admin_only)
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
@user_passes_test(is_admin_only)
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
@user_passes_test(is_admin_only)
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
@user_passes_test(is_admin_only)
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
@user_passes_test(is_admin_only)
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

# Vistas para gestión de mesas

@login_required
@require_module_access('sucursales')
def listar_mesas_sucursal(request, sucursal_id):
    """Vista para obtener las mesas de una sucursal"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        sucursal = get_object_or_404(Sucursal, id=sucursal_id)
        mesas = Mesa.objects.filter(sucursal=sucursal).order_by('numero')
        
        mesas_data = []
        for mesa in mesas:
            mesas_data.append({
                'id': mesa.id,
                'numero': mesa.numero,
                'nombre': mesa.nombre,
                'capacidad': mesa.capacidad,
                'estado': mesa.estado,
                'ubicacion': mesa.ubicacion if hasattr(mesa, 'ubicacion') else '',
                'codigo_qr': mesa.codigo_qr,
                'activo': mesa.activa
            })
        
        return JsonResponse({
            'success': True,
            'mesas': mesas_data
        })
        
    except Exception as e:
        print(f"Error listando mesas: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_only)
def crear_mesa(request):
    """Vista para crear una nueva mesa"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        
        # Validar datos requeridos
        numero = data.get('numero', '').strip()
        capacidad = data.get('capacidad')
        sucursal_id = data.get('sucursal_id')
        
        if not numero or not capacidad or not sucursal_id:
            return JsonResponse({
                'success': False,
                'message': 'Número, capacidad y sucursal son requeridos'
            })
        
        # Verificar que la sucursal existe
        sucursal = get_object_or_404(Sucursal, id=sucursal_id)
        
        # Verificar que no existe una mesa con el mismo número en la sucursal
        if Mesa.objects.filter(sucursal=sucursal, numero=numero).exists():
            return JsonResponse({
                'success': False,
                'message': f'Ya existe una mesa con el número "{numero}" en esta sucursal'
            })
        
        # Crear la mesa
        mesa = Mesa.objects.create(
            numero=numero,
            capacidad=int(capacidad),
            sucursal=sucursal,
            estado=data.get('estado', 'disponible'),
            nombre=data.get('ubicacion', ''),  # Usar ubicacion como nombre temporal
            activa=True
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Mesa "{numero}" creada exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Datos JSON inválidos'
        })
    except Exception as e:
        print(f"Error creando mesa: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@require_module_access('sucursales')
def obtener_mesa(request, mesa_id):
    """Vista para obtener los datos de una mesa"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        mesa = get_object_or_404(Mesa, id=mesa_id)
        
        mesa_data = {
            'id': mesa.id,
            'numero': mesa.numero,
            'nombre': mesa.nombre,
            'capacidad': mesa.capacidad,
            'estado': mesa.estado,
            'ubicacion': mesa.nombre,  # Usar nombre como ubicacion
            'codigo_qr': mesa.codigo_qr,
            'activo': mesa.activa
        }
        
        return JsonResponse({
            'success': True,
            'mesa': mesa_data
        })
        
    except Exception as e:
        print(f"Error obteniendo mesa: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_only)
def editar_mesa(request, mesa_id):
    """Vista para editar una mesa"""
    if request.method != 'PUT':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        mesa = get_object_or_404(Mesa, id=mesa_id)
        
        # Validar datos requeridos
        numero = data.get('numero', '').strip()
        capacidad = data.get('capacidad')
        
        if not numero or not capacidad:
            return JsonResponse({
                'success': False,
                'message': 'Número y capacidad son requeridos'
            })
        
        # Verificar que no existe otra mesa con el mismo número en la sucursal
        if Mesa.objects.filter(sucursal=mesa.sucursal, numero=numero).exclude(id=mesa.id).exists():
            return JsonResponse({
                'success': False,
                'message': f'Ya existe otra mesa con el número "{numero}" en esta sucursal'
            })
        
        # Actualizar datos
        mesa.numero = numero
        mesa.capacidad = int(capacidad)
        mesa.estado = data.get('estado', mesa.estado)
        mesa.nombre = data.get('ubicacion', mesa.nombre)
        mesa.activa = data.get('activa', mesa.activa)
        mesa.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Mesa "{numero}" actualizada exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Datos JSON inválidos'
        })
    except Exception as e:
        print(f"Error editando mesa: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_only)
def cambiar_estado_mesa(request, mesa_id):
    """Vista para cambiar el estado de una mesa"""
    if request.method != 'PUT':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        mesa = get_object_or_404(Mesa, id=mesa_id)
        
        nuevo_estado = data.get('estado')
        if nuevo_estado not in ['disponible', 'ocupada', 'reservada', 'mantenimiento']:
            return JsonResponse({
                'success': False,
                'message': 'Estado inválido'
            })
        
        mesa.estado = nuevo_estado
        mesa.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Estado de mesa "{mesa.numero}" cambiado a {nuevo_estado}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Datos JSON inválidos'
        })
    except Exception as e:
        print(f"Error cambiando estado de mesa: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_only)
def eliminar_mesa(request, mesa_id):
    """Vista para eliminar una mesa"""
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        mesa = get_object_or_404(Mesa, id=mesa_id)
        
        # Verificar si la mesa está en uso (ocupada)
        if mesa.estado == 'ocupada':
            return JsonResponse({
                'success': False,
                'message': 'No se puede eliminar una mesa que está ocupada'
            })
        
        numero_mesa = mesa.numero
        mesa.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Mesa "{numero_mesa}" eliminada exitosamente'
        })
        
    except Exception as e:
        print(f"Error eliminando mesa: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })
