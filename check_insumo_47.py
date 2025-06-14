print("=== VERIFICACION DE INSUMOS ===")
from restaurant.models import Insumo

# Ver todos los insumos
insumos = Insumo.objects.all()
print(f"Total insumos: {insumos.count()}")

# Ver insumos por tipo
for tipo in ['basico', 'compuesto', 'elaborado']:
    count = Insumo.objects.filter(tipo=tipo).count()
    print(f"Insumos {tipo}: {count}")

# Ver algunos insumos específicos
print("\nInsumos disponibles:")
for insumo in Insumo.objects.filter(activo=True)[:10]:
    print(f"ID {insumo.id}: {insumo.nombre} (tipo: {insumo.tipo})")

# Verificar si existe el ID 47
insumo_47 = Insumo.objects.filter(id=47).first()
if insumo_47:
    print(f"\nInsumo ID 47: {insumo_47.nombre} (tipo: {insumo_47.tipo}, activo: {insumo_47.activo})")
else:
    print("\nInsumo ID 47: NO EXISTE")

exit()
