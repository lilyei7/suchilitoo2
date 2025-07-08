import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suchilitoo2.settings')
django.setup()

from mesero.models import Mesa

def listar_mesas():
    print('Mesas existentes:')
    for m in Mesa.objects.all():
        print(f' - ID: {m.id}, Nombre: {m.nombre}, Sucursal: {m.sucursal.nombre if m.sucursal else "Sin sucursal"}, Activa: {m.activa}, Capacidad: {m.capacidad}')

if __name__ == '__main__':
    listar_mesas()
