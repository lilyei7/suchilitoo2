import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta, CategoriaProducto
from django.db.models import Q

def simular_vista():
    print("\n=== SIMULANDO LA VISTA lista_productos_venta ===")
    print("=" * 50)
    
    # Simular exactamente lo que hace la vista
    print("1. Obteniendo todos los productos...")
    productos = ProductoVenta.objects.select_related('categoria').all()
    print(f"   Query: {productos.query}")
    print(f"   Total productos encontrados: {productos.count()}")
    
    # Aplicar ordenamiento
    productos = productos.order_by('categoria__nombre', 'nombre')
    print(f"   Después del ordenamiento: {productos.count()}")
    
    # Mostrar cada producto
    print("\n2. LISTA COMPLETA DE PRODUCTOS:")
    print("-" * 80)
    print(f"{'ID':<5} {'CÓDIGO':<12} {'NOMBRE':<25} {'CATEGORÍA':<15} {'DISPONIBLE':<10}")
    print("-" * 80)
    
    for producto in productos:
        categoria_nombre = producto.categoria.nombre if producto.categoria else "Sin categoría"
        print(f"{producto.id:<5} {producto.codigo:<12} {producto.nombre:<25} {categoria_nombre:<15} {str(producto.disponible):<10}")
    
    # Contar productos
    total_productos = productos.count()
    activos = sum(1 for p in productos if p.disponible)
    inactivos = total_productos - activos
    
    print(f"\n3. CONTADORES:")
    print(f"   Total productos: {total_productos}")
    print(f"   Productos activos: {activos}")
    print(f"   Productos inactivos: {inactivos}")
    
    # Verificar categorías
    print(f"\n4. CATEGORÍAS DISPONIBLES:")
    categorias = CategoriaProducto.objects.filter(activo=True).order_by('nombre')
    print(f"   Total categorías activas: {categorias.count()}")
    for categoria in categorias:
        print(f"   - {categoria.nombre} (ID: {categoria.id})")
    
    # Simular filtros
    print(f"\n5. SIMULANDO FILTROS:")
    
    # Sin filtros (caso normal)
    productos_sin_filtro = productos
    print(f"   Sin filtros: {productos_sin_filtro.count()} productos")
    
    # Con filtro de categoría inexistente
    productos_con_categoria = productos.filter(categoria_id=999)
    print(f"   Con categoría 999 (inexistente): {productos_con_categoria.count()} productos")
    
    # Con búsqueda por nombre
    productos_busqueda = productos.filter(
        Q(nombre__icontains='rollo') | 
        Q(codigo__icontains='rollo') | 
        Q(descripcion__icontains='rollo')
    )
    print(f"   Búsqueda 'rollo': {productos_busqueda.count()} productos")
    
    return productos

if __name__ == '__main__':
    try:
        productos = simular_vista()
        print("\n=== FIN DE LA SIMULACIÓN ===")
    except Exception as e:
        print(f"\nError en la simulación: {str(e)}")
        import traceback
        traceback.print_exc()
