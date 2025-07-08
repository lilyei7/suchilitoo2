import django
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import ProductoVenta
from django.conf import settings

def verificar_imagenes_productos():
    """Verificar las imágenes de los productos"""
    print("=== VERIFICACIÓN DE IMÁGENES DE PRODUCTOS ===")
    
    # Obtener todos los productos
    productos = ProductoVenta.objects.all()
    print(f"Total de productos: {productos.count()}")
    
    # Verificar productos con imágenes
    productos_con_imagen = productos.filter(imagen__isnull=False).exclude(imagen='')
    print(f"Productos con imagen: {productos_con_imagen.count()}")
    
    if productos_con_imagen.exists():
        print("\nProductos con imagen:")
        for producto in productos_con_imagen[:10]:  # Mostrar solo los primeros 10
            print(f"  - {producto.nombre}")
            print(f"    Imagen: {producto.imagen}")
            print(f"    URL: {producto.imagen.url if producto.imagen else 'Sin imagen'}")
            
            # Verificar si el archivo existe
            if producto.imagen:
                ruta_completa = os.path.join(settings.MEDIA_ROOT, str(producto.imagen))
                existe = os.path.exists(ruta_completa)
                print(f"    Archivo existe: {existe}")
                if existe:
                    print(f"    Tamaño: {os.path.getsize(ruta_completa)} bytes")
            print()
    
    # Verificar productos sin imagen
    productos_sin_imagen = productos.filter(imagen__isnull=True) | productos.filter(imagen='')
    print(f"Productos sin imagen: {productos_sin_imagen.count()}")
    
    if productos_sin_imagen.exists():
        print("\nPrimeros 5 productos sin imagen:")
        for producto in productos_sin_imagen[:5]:
            print(f"  - {producto.nombre}")
    
    # Verificar configuración de media
    print(f"\nConfiguración de media:")
    print(f"  MEDIA_URL: {settings.MEDIA_URL}")
    print(f"  MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"  MEDIA_ROOT existe: {os.path.exists(settings.MEDIA_ROOT)}")
    
    # Verificar si hay carpetas de imagen
    if os.path.exists(settings.MEDIA_ROOT):
        contenido = os.listdir(settings.MEDIA_ROOT)
        print(f"  Contenido de MEDIA_ROOT: {contenido}")
        
        # Buscar carpetas relacionadas con productos
        for item in contenido:
            item_path = os.path.join(settings.MEDIA_ROOT, item)
            if os.path.isdir(item_path):
                print(f"    Carpeta {item}: {len(os.listdir(item_path))} archivos")

def crear_imagenes_ejemplo():
    """Crear imágenes de ejemplo para productos que no tienen"""
    print("\n=== CREANDO IMÁGENES DE EJEMPLO ===")
    
    from PIL import Image, ImageDraw, ImageFont
    import random
    
    # Crear directorio de imágenes si no existe
    productos_dir = os.path.join(settings.MEDIA_ROOT, 'productos')
    os.makedirs(productos_dir, exist_ok=True)
    
    # Obtener productos sin imagen
    productos_sin_imagen = ProductoVenta.objects.filter(imagen__isnull=True) | ProductoVenta.objects.filter(imagen='')
    
    colores = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57',
        '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43'
    ]
    
    for i, producto in enumerate(productos_sin_imagen[:10]):  # Solo los primeros 10
        try:
            # Crear imagen
            width, height = 300, 200
            color = random.choice(colores)
            
            # Crear imagen base
            img = Image.new('RGB', (width, height), color)
            draw = ImageDraw.Draw(img)
            
            # Intentar usar una fuente por defecto
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Agregar texto
            texto = producto.nombre[:20] + "..." if len(producto.nombre) > 20 else producto.nombre
            
            # Calcular posición del texto
            bbox = draw.textbbox((0, 0), texto, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # Dibujar texto
            draw.text((x, y), texto, fill='white', font=font)
            
            # Guardar imagen
            filename = f"producto_{producto.id}_{producto.nombre.replace(' ', '_').replace('/', '_')[:20]}.png"
            filepath = os.path.join(productos_dir, filename)
            img.save(filepath)
            
            # Actualizar producto
            producto.imagen = f'productos/{filename}'
            producto.save()
            
            print(f"  ✓ Imagen creada para: {producto.nombre}")
            
        except Exception as e:
            print(f"  ✗ Error creando imagen para {producto.nombre}: {e}")
    
    print(f"\nImágenes creadas exitosamente")

def main():
    """Función principal"""
    try:
        verificar_imagenes_productos()
        
        # Preguntar si crear imágenes de ejemplo
        respuesta = input("\n¿Quieres crear imágenes de ejemplo para productos sin imagen? (s/n): ").lower().strip()
        if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            try:
                from PIL import Image, ImageDraw, ImageFont
                crear_imagenes_ejemplo()
            except ImportError:
                print("Instalando Pillow para crear imágenes...")
                os.system("pip install Pillow")
                try:
                    from PIL import Image, ImageDraw, ImageFont
                    crear_imagenes_ejemplo()
                except Exception as e:
                    print(f"Error instalando Pillow: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
