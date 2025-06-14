from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET

from restaurant.models import CategoriaInsumo, UnidadMedida

@login_required
@require_GET
def listar_categorias(request):
    """Lista todas las categorías de insumos"""
    categorias = CategoriaInsumo.objects.all().order_by('nombre')
    return JsonResponse({
        'success': True,
        'categorias': [
            {
                'id': cat.id,
                'nombre': cat.nombre,
                'descripcion': cat.descripcion or ""
            } for cat in categorias
        ]
    })

@login_required
@require_POST
def crear_categoria(request):
    """Crea una nueva categoría de insumo"""
    nombre = request.POST.get('nombre', '').strip()
    descripcion = request.POST.get('descripcion', '').strip()
    
    # Validar datos
    if not nombre:
        return JsonResponse({
            'success': False,
            'error': 'El nombre de la categoría es obligatorio'
        }, status=400)
    
    # Verificar si ya existe
    if CategoriaInsumo.objects.filter(nombre__iexact=nombre).exists():
        return JsonResponse({
            'success': False,
            'error': f'Ya existe una categoría con el nombre "{nombre}"'
        }, status=400)
    
    # Crear categoría
    try:
        categoria = CategoriaInsumo.objects.create(
            nombre=nombre,
            descripcion=descripcion
        )
        return JsonResponse({
            'success': True,
            'categoria': {
                'id': categoria.id,
                'nombre': categoria.nombre,
                'descripcion': categoria.descripcion or ""
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al crear la categoría: {str(e)}'
        }, status=500)

@login_required
@require_GET
def listar_unidades(request):
    """Lista todas las unidades de medida"""
    unidades = UnidadMedida.objects.all().order_by('nombre')
    return JsonResponse({
        'success': True,
        'unidades': [
            {
                'id': unidad.id,
                'nombre': unidad.nombre,
                'abreviacion': unidad.abreviacion
            } for unidad in unidades
        ]
    })

@login_required
@require_POST
def crear_unidad(request):
    """Crea una nueva unidad de medida"""
    nombre = request.POST.get('nombre', '').strip()
    abreviacion = request.POST.get('abreviacion', '').strip()
    
    # Validar datos
    if not nombre:
        return JsonResponse({
            'success': False,
            'error': 'El nombre de la unidad es obligatorio'
        }, status=400)
    
    if not abreviacion:
        return JsonResponse({
            'success': False,
            'error': 'La abreviación es obligatoria'
        }, status=400)
    
    # Verificar si ya existe
    if UnidadMedida.objects.filter(nombre__iexact=nombre).exists():
        return JsonResponse({
            'success': False,
            'error': f'Ya existe una unidad con el nombre "{nombre}"'
        }, status=400)
    
    if UnidadMedida.objects.filter(abreviacion__iexact=abreviacion).exists():
        return JsonResponse({
            'success': False,
            'error': f'Ya existe una unidad con la abreviación "{abreviacion}"'
        }, status=400)
    
    # Crear unidad
    try:
        unidad = UnidadMedida.objects.create(
            nombre=nombre,
            abreviacion=abreviacion
        )
        return JsonResponse({
            'success': True,
            'unidad': {
                'id': unidad.id,
                'nombre': unidad.nombre,
                'abreviacion': unidad.abreviacion
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al crear la unidad: {str(e)}'
        }, status=500)
