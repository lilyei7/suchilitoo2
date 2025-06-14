import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import CategoriaReceta

def crear_categorias_iniciales():
    """Crear categorías iniciales para recetas de sushi"""
    categorias = [
        ('entrada', 'Entradas', 'Platillos para iniciar la comida'),
        ('rollos', 'Rollos', 'Diferentes tipos de rollos de sushi'),
        ('nigiri', 'Nigiri', 'Sushi estilo nigiri con pescado encima del arroz'),
        ('sashimi', 'Sashimi', 'Cortes frescos de pescado sin arroz'),
        ('temaki', 'Temaki', 'Conos de sushi enrollados a mano'),
        ('especial', 'Especialidades', 'Platillos especiales de la casa'),
        ('postre', 'Postres', 'Postres japoneses y fusión'),
        ('bebida', 'Bebidas', 'Bebidas tradicionales y especiales')
    ]
    
    print("Creando categorías de recetas...")
    
    for codigo, nombre, descripcion in categorias:
        categoria, created = CategoriaReceta.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'descripcion': descripcion,
                'activa': True
            }
        )
        
        if created:
            print(f"✅ Categoría '{nombre}' creada")
        else:
            print(f"ℹ️ Categoría '{nombre}' ya existe")
    
    print(f"\n📋 Total de categorías: {CategoriaReceta.objects.count()}")

if __name__ == "__main__":
    crear_categorias_iniciales()
