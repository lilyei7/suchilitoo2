import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import CategoriaProducto, CategoriaInsumo, UnidadMedida, Insumo, Proveedor

def crear_datos_para_recetas():
    """
    Crea datos básicos para probar el módulo de recetas
    """
    print("Creando datos básicos para recetas...")
    
    # Crear categorías de productos (para recetas)
    categorias_productos = [
        {'nombre': 'Sushi', 'descripcion': 'Variedades de sushi'},
        {'nombre': 'Entradas', 'descripcion': 'Platos de entrada'},
        {'nombre': 'Bebidas', 'descripcion': 'Bebidas y refrescos'},
        {'nombre': 'Postres', 'descripcion': 'Postres y dulces'},
    ]
    
    for cat in categorias_productos:
        CategoriaProducto.objects.get_or_create(
            nombre=cat['nombre'],
            defaults={'descripcion': cat['descripcion']}
        )
      # Verificar unidades de medida
    unidades = [
        {'nombre': 'Kilogramo', 'abreviacion': 'kg'},
        {'nombre': 'Gramo', 'abreviacion': 'g'},
        {'nombre': 'Litro', 'abreviacion': 'L'},
        {'nombre': 'Mililitro', 'abreviacion': 'ml'},
        {'nombre': 'Unidad', 'abreviacion': 'ud'},
        {'nombre': 'Unidad', 'abreviacion': 'unidad'},  # Alternativa
        {'nombre': 'Cucharada', 'abreviacion': 'cda'},
        {'nombre': 'Cucharadita', 'abreviacion': 'cdta'},
    ]
    
    for unidad in unidades:
        try:
            UnidadMedida.objects.get_or_create(
                nombre=unidad['nombre'],
                defaults={'abreviacion': unidad['abreviacion']}
            )
            
            # También crear por abreviación en caso de que haya inconsistencias
            UnidadMedida.objects.get_or_create(
                abreviacion=unidad['abreviacion'],
                defaults={'nombre': unidad['nombre']}
            )
        except Exception as e:
            print(f"Error creando unidad {unidad['nombre']}: {e}")
    
    # Verificar categorías de insumos
    categorias_insumos = [
        {'nombre': 'Pescados', 'descripcion': 'Pescados y mariscos'},
        {'nombre': 'Vegetales', 'descripcion': 'Vegetales y frutas'},
        {'nombre': 'Cereales', 'descripcion': 'Arroz y otros cereales'},
        {'nombre': 'Lácteos', 'descripcion': 'Productos lácteos'},
        {'nombre': 'Condimentos', 'descripcion': 'Salsas y condimentos'},
    ]
    
    for cat in categorias_insumos:
        CategoriaInsumo.objects.get_or_create(
            nombre=cat['nombre'],
            defaults={'descripcion': cat['descripcion']}
        )
    
    # Crear un proveedor si no existe
    proveedor, _ = Proveedor.objects.get_or_create(
        nombre="Proveedor General",
        defaults={
            'ruc': '1234567890',
            'direccion': 'Dirección de ejemplo',
            'contacto': 'Juan Pérez',
            'telefono': '555-123-4567',
            'email': 'proveedor@example.com'
        }
    )
      # Crear insumos básicos
    insumos_data = [
        {
            'codigo': 'ARR001',
            'nombre': 'Arroz para sushi',
            'descripcion': 'Arroz de grano corto para sushi',
            'tipo': 'basico',
            'categoria': 'Cereales',
            'unidad_medida': 'kg',
            'precio_unitario': 5.50,
            'stock_actual': 25.0
        },
        {
            'codigo': 'PES001',
            'nombre': 'Salmón fresco',
            'descripcion': 'Salmón fresco de alta calidad',
            'tipo': 'basico',
            'categoria': 'Pescados',
            'unidad_medida': 'kg',
            'precio_unitario': 45.00,
            'stock_actual': 8.5
        },
        {
            'codigo': 'VEG001',
            'nombre': 'Aguacate',
            'descripcion': 'Aguacate maduro',
            'tipo': 'basico',
            'categoria': 'Vegetales',
            'unidad_medida': 'ud',  # Cambiado a ud
            'precio_unitario': 2.00,
            'stock_actual': 50.0
        },
        {
            'codigo': 'VEG002',
            'nombre': 'Pepino',
            'descripcion': 'Pepino fresco',
            'tipo': 'basico',
            'categoria': 'Vegetales',
            'unidad_medida': 'ud',  # Cambiado a ud
            'precio_unitario': 1.00,
            'stock_actual': 40.0
        },
        {
            'codigo': 'COND001',
            'nombre': 'Vinagre de arroz',
            'descripcion': 'Vinagre de arroz para sushi',
            'tipo': 'basico',
            'categoria': 'Condimentos',
            'unidad_medida': 'ml',
            'precio_unitario': 0.02,
            'stock_actual': 2000.0
        },
    ]
    
    for insumo_data in insumos_data:
        try:
            categoria = CategoriaInsumo.objects.get(nombre=insumo_data['categoria'])
            unidad_medida = UnidadMedida.objects.get(abreviacion=insumo_data['unidad_medida'])
            
            insumo, created = Insumo.objects.get_or_create(
                codigo=insumo_data['codigo'],
                defaults={
                    'nombre': insumo_data['nombre'],
                    'descripcion': insumo_data['descripcion'],
                    'tipo': insumo_data['tipo'],
                    'categoria': categoria,
                    'unidad_medida': unidad_medida,
                    'precio_unitario': insumo_data['precio_unitario'],
                    'stock_actual': insumo_data['stock_actual'],
                    'proveedor_principal': proveedor
                }
            )
            
            if created:
                print(f"Creado insumo: {insumo.nombre}")
            
        except Exception as e:
            print(f"Error creando insumo {insumo_data['nombre']}: {e}")
    
    print("Datos básicos para recetas creados correctamente.")

if __name__ == "__main__":
    crear_datos_para_recetas()
