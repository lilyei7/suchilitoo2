"""
Script para crear mesas en la Sucursal Centro (ID=1)
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import Mesa
from accounts.models import Sucursal
import sys

def main():
    # Verificar que la Sucursal Centro existe
    try:
        sucursal_centro = Sucursal.objects.get(id=1)
        print(f"✓ Sucursal encontrada: {sucursal_centro.nombre} (ID: {sucursal_centro.id})")
    except Sucursal.DoesNotExist:
        print("❌ La Sucursal Centro (ID=1) no existe.")
        return
    
    # Mostrar mesas actuales en la Sucursal Centro
    mesas_existentes = Mesa.objects.filter(sucursal=sucursal_centro)
    print(f"\nMesas actuales en {sucursal_centro.nombre}: {mesas_existentes.count()}")
    for mesa in mesas_existentes:
        print(f"  - Mesa {mesa.numero} (ID: {mesa.id}, Estado: {mesa.estado}, Activa: {mesa.activa})")
    
    if mesas_existentes.count() > 0:
        print("\n¡Ya existen mesas en esta sucursal!")
        respuesta = input("¿Deseas crear más mesas? (s/n): ")
        if respuesta.lower() != 's':
            return
    
    # Crear nuevas mesas
    num_mesas = input("\n¿Cuántas mesas deseas crear? (predeterminado: 8): ")
    try:
        num_mesas = int(num_mesas) if num_mesas.strip() else 8
    except ValueError:
        num_mesas = 8
    
    print(f"\nCreando {num_mesas} mesas para {sucursal_centro.nombre}...")
    
    mesas_creadas = []
    for i in range(1, num_mesas + 1):
        # Verificar si el número de mesa ya existe
        numero_mesa = str(i).zfill(2)  # 01, 02, etc.
        
        # Verificar si ya existe una mesa con ese número
        if Mesa.objects.filter(numero=numero_mesa, sucursal=sucursal_centro).exists():
            print(f"  ⚠️ Mesa {numero_mesa} ya existe en esta sucursal, omitiendo...")
            continue
        
        # Crear la mesa
        mesa = Mesa.objects.create(
            numero=numero_mesa,
            sucursal=sucursal_centro,
            capacidad=4,
            estado='disponible',
            activa=True
        )
        mesas_creadas.append(mesa)
        print(f"  ✓ Mesa {mesa.numero} creada (ID: {mesa.id})")
    
    print(f"\n✅ {len(mesas_creadas)} mesas creadas exitosamente.")
    
    # Mostrar instrucciones
    print("\nINSTRUCCIONES:")
    print("1. Accede a http://127.0.0.1:8000/mesero/seleccionar-mesa/ con un usuario de la Sucursal Centro")
    print("2. Recomendación: usa el usuario 'gerente_test'")
    print("3. Deberías ver las mesas que acabamos de crear")

if __name__ == "__main__":
    main()
