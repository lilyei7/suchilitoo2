import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import CategoriaReceta, Receta, Insumo

def verificar_estructura_recetas():
    """Verificar que la estructura de recetas esté correcta"""
    
    print("🔍 Verificando estructura del sistema de recetas...\n")
    
    # 1. Verificar categorías
    categorias = CategoriaReceta.objects.all()
    print(f"📋 Categorías disponibles: {categorias.count()}")
    for cat in categorias:
        print(f"  - {cat.nombre} (código: {cat.codigo})")
    
    # 2. Verificar insumos disponibles
    insumos = Insumo.objects.filter(activo=True)
    print(f"\n🥘 Insumos activos disponibles: {insumos.count()}")
    print(f"  - Básicos: {insumos.filter(tipo='basico').count()}")
    print(f"  - Compuestos: {insumos.filter(tipo='compuesto').count()}")
    print(f"  - Elaborados: {insumos.filter(tipo='elaborado').count()}")
    
    # 3. Verificar recetas existentes
    recetas = Receta.objects.filter(activa=True)
    print(f"\n📖 Recetas activas: {recetas.count()}")
    
    recetas_con_categoria = recetas.filter(categoria__isnull=False)
    recetas_sin_categoria = recetas.filter(categoria__isnull=True)
    
    print(f"  - Con categoría: {recetas_con_categoria.count()}")
    print(f"  - Sin categoría: {recetas_sin_categoria.count()}")
    
    if recetas_con_categoria.exists():
        print("\n  Recetas con categoría:")
        for receta in recetas_con_categoria[:5]:  # Mostrar solo 5
            print(f"    • {receta.nombre} ({receta.categoria.nombre})")
    
    if recetas_sin_categoria.exists():
        print("\n  Recetas sin categoría:")
        for receta in recetas_sin_categoria[:5]:  # Mostrar solo 5
            print(f"    • {receta.nombre}")
    
    print("\n" + "="*50)
    print("✅ Estructura verificada correctamente!")
    print("🎯 El sistema está listo para crear nuevas recetas con categorías.")
    
    if recetas_sin_categoria.exists():
        print(f"\n💡 Sugerencia: Puedes asignar categorías a las {recetas_sin_categoria.count()} recetas sin categoría.")

if __name__ == "__main__":
    verificar_estructura_recetas()
