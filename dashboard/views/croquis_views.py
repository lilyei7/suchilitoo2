from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import ValidationError
import json

from accounts.models import Sucursal
from dashboard.models_ventas import Mesa
from dashboard.models_croquis import CroquisLayout
from .base_views import get_sidebar_context, is_admin_or_manager
from dashboard.utils.permissions import require_module_access

def is_admin_only(user):
    """Función para verificar que solo admin y superuser tengan acceso"""
    return user.is_authenticated and (user.is_superuser or (hasattr(user, 'rol') and user.rol and user.rol.nombre.lower() in ['administrador', 'admin']))

def ajax_login_required(function):
    """
    Decorador personalizado para vistas AJAX que devuelve JSON en lugar de redirigir
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'Se requiere autenticación',
                'redirect': '/login/'
            }, status=401)
        return function(request, *args, **kwargs)
    return wrapper

def ajax_admin_required(function):
    """
    Decorador personalizado para vistas AJAX que requieren permisos de admin
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'Se requiere autenticación',
                'redirect': '/login/'
            }, status=401)
        
        if not is_admin_only(request.user):
            return JsonResponse({
                'success': False,
                'message': 'Permisos insuficientes - Se requieren permisos de administrador'
            }, status=403)
        
        return function(request, *args, **kwargs)
    return wrapper

@login_required
@require_module_access('sucursales')
def croquis_editor_view(request, sucursal_id):
    """Vista principal del editor de croquis"""
    try:
        sucursal = get_object_or_404(Sucursal, id=sucursal_id)
        
        context = {
            'sucursal': sucursal,
            **get_sidebar_context('sucursales')
        }
        
        return render(request, 'dashboard/croquis_editor.html', context)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error en croquis_editor_view: {e}")
        print(f"Traceback completo: {error_details}")
        
        return render(request, 'dashboard/error.html', {
            'error_message': f'Error al cargar el editor de croquis: {str(e)}',
            **get_sidebar_context('sucursales')
        })

@ajax_admin_required
def guardar_layout_croquis(request):
    """Vista para guardar el layout del croquis"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        
        sucursal_id = data.get('sucursalId')
        objetos = data.get('objetos', [])
        version = data.get('version', '1.0')
        
        if not sucursal_id:
            return JsonResponse({
                'success': False,
                'message': 'ID de sucursal requerido'
            })
        
        sucursal = get_object_or_404(Sucursal, id=sucursal_id)
        
        # Validar que los objetos de tipo mesa tengan mesaId válidos
        mesas_vinculadas = []
        for obj in objetos:
            if obj.get('tipo') == 'mesa' and obj.get('mesaId'):
                mesa_id = obj.get('mesaId')
                if mesa_id in mesas_vinculadas:
                    return JsonResponse({
                        'success': False,
                        'message': f'La mesa con ID {mesa_id} está vinculada múltiples veces'
                    })
                
                # Verificar que la mesa existe y pertenece a la sucursal
                try:
                    mesa = Mesa.objects.get(id=mesa_id, sucursal=sucursal)
                    mesas_vinculadas.append(mesa_id)
                except Mesa.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': f'Mesa con ID {mesa_id} no encontrada en esta sucursal'
                    })
        
        # Guardar o actualizar layout
        with transaction.atomic():
            layout, created = CroquisLayout.objects.get_or_create(
                sucursal=sucursal,
                defaults={
                    'layout_data': data,
                    'version': version
                }
            )
            
            if not created:
                layout.layout_data = data
                layout.version = version
                layout.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Layout guardado exitosamente',
            'created': created
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Datos JSON inválidos'
        })
    except Exception as e:
        print(f"Error guardando layout: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@require_module_access('sucursales')
def cargar_layout_croquis(request, sucursal_id):
    """Vista para cargar el layout del croquis"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        sucursal = get_object_or_404(Sucursal, id=sucursal_id)
        
        try:
            layout = CroquisLayout.objects.get(sucursal=sucursal)
            return JsonResponse({
                'success': True,
                'layout': layout.layout_data,
                'version': layout.version,
                'last_updated': layout.updated_at.isoformat()
            })
            
        except CroquisLayout.DoesNotExist:
            return JsonResponse({
                'success': True,
                'layout': None,
                'message': 'No hay layout guardado para esta sucursal'
            })
            
    except Exception as e:
        print(f"Error cargando layout: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@ajax_login_required
@require_module_access('sucursales')
def obtener_mesas_croquis(request, sucursal_id):
    """Vista para obtener las mesas disponibles para el croquis"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        sucursal = get_object_or_404(Sucursal, id=sucursal_id)
        mesas = Mesa.objects.filter(sucursal=sucursal, activa=True).order_by('numero')
        
        mesas_data = []
        for mesa in mesas:
            mesas_data.append({
                'id': mesa.id,
                'numero': mesa.numero,
                'nombre': mesa.nombre,
                'capacidad': mesa.capacidad,
                'estado': mesa.estado,
                'ubicacion': getattr(mesa, 'ubicacion', ''),
                'activo': mesa.activa
            })
        
        return JsonResponse({
            'success': True,
            'mesas': mesas_data
        })
        
    except Exception as e:
        print(f"Error obteniendo mesas para croquis: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@user_passes_test(is_admin_only)
def eliminar_layout_croquis(request, sucursal_id):
    """Vista para eliminar el layout del croquis"""
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        sucursal = get_object_or_404(Sucursal, id=sucursal_id)
        
        try:
            layout = CroquisLayout.objects.get(sucursal=sucursal)
            layout.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Layout eliminado exitosamente'
            })
            
        except CroquisLayout.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'No hay layout para eliminar'
            })
            
    except Exception as e:
        print(f"Error eliminando layout: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })

@login_required
@require_module_access('sucursales')
def preview_croquis(request, sucursal_id):
    """Vista para previsualizar el croquis de una sucursal"""
    try:
        sucursal = get_object_or_404(Sucursal, id=sucursal_id)
        
        # Intentar cargar el layout
        layout_data = None
        layout_json = None
        try:
            layout = CroquisLayout.objects.get(sucursal=sucursal)
            layout_data = layout.layout_data
            # Serializar correctamente para JavaScript
            if layout_data:
                import json
                
                def convert_python_to_js(obj):
                    """Convertir recursivamente True/False de Python a true/false de JS"""
                    if isinstance(obj, dict):
                        return {k: convert_python_to_js(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [convert_python_to_js(item) for item in obj]
                    elif isinstance(obj, bool):
                        return obj  # JSON dumps manejará esto correctamente
                    else:
                        return obj
                
                # Convertir datos
                clean_data = convert_python_to_js(layout_data)
                
                # Serializar con configuración específica para evitar problemas
                layout_json = json.dumps(clean_data, ensure_ascii=False, separators=(',', ':'))
                
                # Debug: verificar que el JSON es válido
                try:
                    json.loads(layout_json)
                    print(f"✅ JSON válido generado para sucursal {sucursal_id}")
                except json.JSONDecodeError as decode_error:
                    print(f"❌ JSON inválido generado: {decode_error}")
                    layout_json = None
                
        except CroquisLayout.DoesNotExist:
            pass
        except json.JSONDecodeError as e:
            print(f"Error serializando layout_data: {e}")
            layout_json = None
        except Exception as e:
            print(f"Error general procesando layout: {e}")
            layout_json = None
        
        context = {
            'sucursal': sucursal,
            'layout_data': layout_data,
            'layout_json': layout_json,
            'preview_mode': True,
            **get_sidebar_context('sucursales')
        }
        
        return render(request, 'dashboard/croquis_preview.html', context)
        
    except Exception as e:
        print(f"Error en preview_croquis: {e}")
        return render(request, 'dashboard/error.html', {
            'error_message': 'Error al cargar la vista previa del croquis',
            **get_sidebar_context('sucursales')
        })

@login_required
@require_module_access('sucursales')
def estadisticas_croquis(request, sucursal_id):
    """Vista para obtener estadísticas del croquis"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        sucursal = get_object_or_404(Sucursal, id=sucursal_id)
        
        # Contar mesas totales
        total_mesas = Mesa.objects.filter(sucursal=sucursal, activa=True).count()
        
        # Contar objetos en el croquis
        objetos_en_croquis = 0
        mesas_ubicadas = 0
        
        try:
            layout = CroquisLayout.objects.get(sucursal=sucursal)
            objetos = layout.layout_data.get('objetos', [])
            objetos_en_croquis = len(objetos)
            
            # Contar mesas vinculadas
            mesas_con_vinculo = [obj for obj in objetos if obj.get('tipo') == 'mesa' and obj.get('mesaId')]
            mesas_ubicadas = len(mesas_con_vinculo)
            
        except CroquisLayout.DoesNotExist:
            pass
        
        estadisticas = {
            'total_mesas': total_mesas,
            'mesas_ubicadas': mesas_ubicadas,
            'mesas_sin_ubicar': total_mesas - mesas_ubicadas,
            'objetos_en_croquis': objetos_en_croquis,
            'tiene_layout': objetos_en_croquis > 0,
            'porcentaje_ubicacion': round((mesas_ubicadas / total_mesas * 100) if total_mesas > 0 else 0, 1)
        }
        
        return JsonResponse({
            'success': True,
            'estadisticas': estadisticas
        })
        
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}'
        })
