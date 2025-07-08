import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.core.management import call_command

def aplicar_migraciones():
    """
    Aplica las migraciones pendientes a la base de datos
    """
    print("=== APLICANDO MIGRACIONES ===")
    try:
        # Generar las migraciones si no existen
        call_command('makemigrations')
        print("✓ Migraciones generadas correctamente")
        
        # Aplicar las migraciones
        call_command('migrate')
        print("✓ Migraciones aplicadas correctamente")
        
        print("\n¡Las migraciones se han aplicado con éxito!")
        print("Ahora puedes probar que la relación entre Producto y Receta funciona correctamente.")
        print("Ejecuta 'python verificar_eliminacion_producto_receta.py' para hacer una prueba.")
    except Exception as e:
        print(f"✗ Error al aplicar migraciones: {e}")
        print("\nSi el error está relacionado con una migración específica, intenta:")
        print("1. Eliminar los archivos de migración en 'restaurant/migrations/' excepto __init__.py")
        print("2. Ejecutar 'python manage.py makemigrations restaurant' para generar nuevas migraciones")
        print("3. Ejecutar 'python manage.py migrate' para aplicarlas")

if __name__ == "__main__":
    aplicar_migraciones()
