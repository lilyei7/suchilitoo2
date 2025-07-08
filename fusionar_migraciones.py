import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.core.management import call_command

def fusionar_migraciones():
    """
    Fusiona migraciones conflictivas
    """
    print("=== FUSIONANDO MIGRACIONES CONFLICTIVAS ===")
    try:
        # Fusionar migraciones
        call_command('makemigrations', '--merge')
        print("✓ Migraciones fusionadas correctamente")
        
        # Aplicar las migraciones
        call_command('migrate')
        print("✓ Migraciones aplicadas correctamente")
        
        print("\n¡Las migraciones se han fusionado y aplicado con éxito!")
        print("Ahora puedes probar que la relación entre Producto y Receta funciona correctamente.")
        print("Ejecuta 'python verificar_eliminacion_producto_receta.py' para hacer una prueba.")
    except Exception as e:
        print(f"✗ Error al fusionar migraciones: {e}")

if __name__ == "__main__":
    fusionar_migraciones()
