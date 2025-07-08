from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from restaurant.models import Receta, CategoriaProducto

@login_required
def menu_dinamico(request):
    # Obtiene todas las categorías activas
    categorias = CategoriaProducto.objects.filter(activo=True)

    productos_por_categoria = {}
    for categoria in categorias:
        # Busca recetas activas cuyo producto pertenezca a la categoría
        recetas = Receta.objects.filter(
            activo=True,
            producto__categoria=categoria
        ).select_related('producto')
        productos = []
        for receta in recetas:
            producto = receta.producto
            if getattr(producto, 'activo', True):  # Solo incluir productos activos
                productos.append({
                    'nombre': producto.nombre,
                    'descripcion': producto.descripcion,
                    'precio': producto.precio,
                    'imagen': producto.imagen.url if hasattr(producto, 'imagen') and producto.imagen else None,
                    'disponible': producto.disponible,
                    'tiempo_preparacion': receta.tiempo_preparacion,
                    'calorias': getattr(producto, 'calorias', None),
                })
        if productos:
            productos_por_categoria[categoria.nombre] = productos

    context = {
        'productos_por_categoria': productos_por_categoria
    }
    return render(request, 'mesero/menu_moderno.html', context)