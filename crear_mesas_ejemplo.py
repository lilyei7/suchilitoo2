"""
Script para crear mesas de ejemplo en la base de datos
"""
import os
import django
import sys

# Configurar el entorno de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Sucursal
from dashboard.models import Mesa

def crear_mesas_ejemplo():
    """Crea mesas de ejemplo para las sucursales"""
    # Obtener todas las sucursales
    sucursales = Sucursal.objects.all()
    
    if not sucursales:
        print("No hay sucursales registradas. Por favor, cree al menos una sucursal.")
        return
    
    # Número de mesas a crear por sucursal
    mesas_por_sucursal = 10
    
    # Para cada sucursal, crear mesas
    for sucursal in sucursales:
        print(f"Creando mesas para sucursal: {sucursal.nombre}")
        
        # Verificar si ya existen mesas para esta sucursal
        mesas_existentes = Mesa.objects.filter(sucursal=sucursal).count()
        if mesas_existentes > 0:
            print(f"  La sucursal ya tiene {mesas_existentes} mesas. ¿Desea crear más? (s/n)")
            respuesta = input().lower()
            if respuesta != 's':
                continue
        
        # Crear mesas numeradas
        for i in range(1, mesas_por_sucursal + 1):
            # Definir capacidad según el número de mesa
            if i <= 4:
                capacidad = 2  # Mesas pequeñas (1-4)
            elif i <= 8:
                capacidad = 4  # Mesas medianas (5-8)
            else:
                capacidad = 6  # Mesas grandes (9-10)
            
            # Crear la mesa si no existe
            mesa, creada = Mesa.objects.get_or_create(
                numero=str(i),
                sucursal=sucursal,
                defaults={
                    'capacidad': capacidad,
                    'estado': 'disponible',
                    'activo': True
                }
            )
            
            if creada:
                print(f"  ✓ Mesa {i} creada (capacidad: {capacidad})")
            else:
                print(f"  ✗ La mesa {i} ya existe")
    
    print("\nProceso completado.")

if __name__ == "__main__":
    print("=== Creación de Mesas de Ejemplo ===")
    crear_mesas_ejemplo()
