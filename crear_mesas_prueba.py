"""
Script para crear mesas de prueba si no existen
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

# Importar modelos después de configurar Django
from mesero.models import Mesa
from accounts.models import Sucursal

def crear_mesas_prueba():
    print("Verificando si existen mesas en el sistema...")
    
    # Verificar si ya existen mesas
    if Mesa.objects.exists():
        mesas_count = Mesa.objects.count()
        print(f"Ya existen {mesas_count} mesas en el sistema.")
        return
    
    # Obtener o crear sucursal
    sucursal, created = Sucursal.objects.get_or_create(
        nombre="Sucursal Principal",
        defaults={
            'direccion': 'Calle Principal #123',
            'telefono': '555-1234',
            'activa': True
        }
    )
    
    if created:
        print(f"Se creó la sucursal: {sucursal.nombre}")
    else:
        print(f"Usando sucursal existente: {sucursal.nombre}")
    
    # Crear mesas
    mesas_a_crear = []
    for i in range(1, 11):  # Crear 10 mesas
        mesas_a_crear.append(
            Mesa(
                numero=i,
                capacidad=4 if i <= 6 else 6,  # Mesas 1-6: 4 personas, 7-10: 6 personas
                sucursal=sucursal,
                activa=True
            )
        )
    
    # Guardar todas las mesas en una sola operación
    Mesa.objects.bulk_create(mesas_a_crear)
    print(f"Se crearon {len(mesas_a_crear)} mesas nuevas.")

if __name__ == "__main__":
    crear_mesas_prueba()
    print("Proceso completado.")
