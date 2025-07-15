from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from PIL import Image
import io
import os
import sys

def compress_image(image_file):
    """
    Comprime una imagen manteniendo calidad aceptable
    - Reduce tamaño a máximo 1200x1200 pixels
    - Comprime con calidad 85%
    - Mantiene el formato original
    - Preserva metadatos importantes
    
    Args:
        image_file: El archivo de imagen subido
        
    Returns:
        Archivo de imagen comprimido
    """
    # Verificar que se haya recibido un archivo
    if not image_file:
        return None
        
    # Determinar el formato de la imagen original
    img_format = os.path.splitext(image_file.name)[1].lower().replace('.', '')
    if img_format == 'jpg':
        img_format = 'jpeg'
    
    # Solo comprimir imágenes JPEG y PNG
    if img_format not in ['jpeg', 'png']:
        return image_file
        
    # Abrir la imagen con Pillow
    img = Image.open(image_file)
    
    # Verificar si la imagen necesita redimensionarse
    max_size = 1200
    if img.width > max_size or img.height > max_size:
        # Calcular proporción para mantener aspect ratio
        ratio = min(max_size / img.width, max_size / img.height)
        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Preparar buffer para guardar la imagen comprimida
    output = io.BytesIO()
    
    # Guardar la imagen comprimida
    if img_format == 'jpeg':
        # Preservar la información EXIF para JPEGs
        exif = None
        if 'exif' in img.info:
            exif = img.info['exif']
        img.save(output, format='JPEG', quality=85, optimize=True, exif=exif)
    elif img_format == 'png':
        # Comprimir PNG, manteniendo transparencia
        img.save(output, format='PNG', optimize=True)
    
    # Reiniciar el puntero al principio del buffer
    output.seek(0)
    
    # Crear un nuevo archivo Django con el contenido comprimido
    filename = os.path.basename(image_file.name)
    if isinstance(image_file, InMemoryUploadedFile):
        return InMemoryUploadedFile(
            output, 
            'ImageField',
            filename,
            f'image/{img_format}',
            sys.getsizeof(output),
            None
        )
    elif isinstance(image_file, TemporaryUploadedFile):
        content = ContentFile(output.getvalue())
        content.name = filename
        return content
    else:
        content = ContentFile(output.getvalue())
        content.name = filename
        return content
