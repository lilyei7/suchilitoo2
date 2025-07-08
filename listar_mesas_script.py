from mesero.models import Mesa

def run():
    print('Mesas existentes:')
    for m in Mesa.objects.all():
        print(f' - ID: {m.id}, Nombre: {m.nombre}, Sucursal: {m.sucursal.nombre if m.sucursal else "Sin sucursal"}, Activa: {m.activa}, Capacidad: {m.capacidad}')
