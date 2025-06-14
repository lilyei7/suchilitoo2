from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from restaurant.models import CategoriaInsumo, UnidadMedida, Insumo as RestaurantInsumo

# Usamos el Insumo de restaurant para tener consistencia
Insumo = RestaurantInsumo
Categoria = CategoriaInsumo

@login_required
def get_form_data(request):
    """Vista para obtener datos para los formularios"""
    # Comprobar si el usuario está autenticado
    if not request.user.is_authenticated:
        print("Usuario no autenticado accediendo a get_form_data")
        # Para depuración - permitir acceso incluso sin autenticación
        # pass  # Descomentar esta línea para permitir acceso sin autenticación
        
    # Obtener datos
    categorias = CategoriaInsumo.objects.all().values('id', 'nombre')
    unidades = UnidadMedida.objects.all().values('id', 'nombre', 'abreviacion')
    
    data = {
        'categorias': list(categorias),
        'unidades': list(unidades)
    }
      # Para depuración
    print(f"Devolviendo datos: {len(data['categorias'])} categorías y {len(data['unidades'])} unidades")
    
    return JsonResponse(data)

@login_required
def obtener_categorias(request):
    """API para obtener todas las categorías"""
    categorias = CategoriaInsumo.objects.all().order_by('nombre')
    categorias_data = [{'id': cat.id, 'nombre': cat.nombre} for cat in categorias]
    
    return JsonResponse({
        'success': True,
        'categorias': categorias_data
    })

@login_required
def obtener_unidades_medida(request):
    """API para obtener todas las unidades de medida"""
    unidades = UnidadMedida.objects.all().order_by('nombre')
    unidades_data = [
        {
            'id': u.id, 
            'nombre': u.nombre, 
            'abreviacion': u.abreviacion
        } 
        for u in unidades
    ]
    
    return JsonResponse({
        'success': True,
        'unidades': unidades_data
    })

@login_required
def crear_categoria(request):
    """Vista para crear una nueva categoría"""
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            
            if not nombre:
                return JsonResponse({
                    'success': False,
                    'error': 'El nombre de la categoría es obligatorio'
                })
            
            # Verificar si ya existe
            if Categoria.objects.filter(nombre=nombre).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Ya existe una categoría con el nombre "{nombre}"'
                })
            
            categoria = Categoria.objects.create(
                nombre=nombre,
                descripcion=descripcion
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Categoría "{nombre}" creada exitosamente',
                'categoria': {
                    'id': categoria.id,
                    'nombre': categoria.nombre,
                    'descripcion': categoria.descripcion if hasattr(categoria, 'descripcion') else ''
                }
            })
            
        except Exception as e:
            print(f"Error creando categoría: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Error al crear la categoría: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })

@login_required
def eliminar_categoria(request, categoria_id):
    """Vista para eliminar una categoría"""
    if request.method == 'POST':
        try:
            categoria = get_object_or_404(Categoria, id=categoria_id)
            
            # Verificar si tiene insumos asociados
            if Insumo.objects.filter(categoria=categoria).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'No se puede eliminar la categoría porque tiene insumos asociados'
                })
            
            nombre = categoria.nombre
            categoria.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Categoría "{nombre}" eliminada exitosamente'
            })
            
        except Exception as e:
            print(f"Error eliminando categoría: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Error al eliminar la categoría: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })

@login_required
def crear_unidad(request):
    """Vista para crear una nueva unidad de medida"""
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre', '').strip()
            abreviacion = request.POST.get('abreviacion', '').strip()
            tipo = request.POST.get('tipo', '').strip()
            
            if not all([nombre, abreviacion]):
                return JsonResponse({
                    'success': False,
                    'error': 'El nombre y abreviación son obligatorios'
                })
            
            # Verificar si ya existe
            if UnidadMedida.objects.filter(nombre=nombre).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Ya existe una unidad con el nombre "{nombre}"'
                })
            
            if UnidadMedida.objects.filter(abreviacion=abreviacion).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Ya existe una unidad con la abreviación "{abreviacion}"'
                })
            
            # Crear la unidad
            unidad_data = {
                'nombre': nombre,
                'abreviacion': abreviacion
            }
            
            # Solo agregar tipo si el modelo lo soporta
            if hasattr(UnidadMedida, 'tipo') and tipo:
                unidad_data['tipo'] = tipo
            
            unidad = UnidadMedida.objects.create(**unidad_data)
            
            return JsonResponse({
                'success': True,
                'message': f'Unidad de medida "{nombre}" creada exitosamente',
                'unidad': {
                    'id': unidad.id,
                    'nombre': unidad.nombre,
                    'abreviacion': unidad.abreviacion,
                    'tipo': getattr(unidad, 'tipo', '') if hasattr(unidad, 'tipo') else ''
                }
            })
            
        except Exception as e:
            print(f"Error creando unidad: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Error al crear la unidad: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })

@login_required
def eliminar_unidad(request, unidad_id):
    """Vista para eliminar una unidad de medida"""
    if request.method == 'POST':
        try:
            unidad = get_object_or_404(UnidadMedida, id=unidad_id)
            
            # Verificar si tiene insumos asociados
            if Insumo.objects.filter(unidad_medida=unidad).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'No se puede eliminar la unidad porque tiene insumos asociados'
                })
            
            nombre = unidad.nombre
            unidad.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Unidad de medida "{nombre}" eliminada exitosamente'
            })
            
        except Exception as e:
            print(f"Error eliminando unidad: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Error al eliminar la unidad: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    })
