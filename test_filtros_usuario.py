#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario, Sucursal
from dashboard.models import Proveedor

print('=== TESTING FILTROS POR USUARIO ===')

# Buscar usuarios de ejemplo
print('\n1. Usuarios disponibles:')
for user in Usuario.objects.all()[:5]:
    rol_nombre = user.rol.nombre if user.rol else 'Sin rol'
    sucursal_nombre = user.sucursal.nombre if user.sucursal else 'Sin sucursal'
    print(f'   - {user.username} | Rol: {rol_nombre} | Sucursal: {sucursal_nombre} | Admin: {user.is_superuser}')

# Buscar sucursales
print('\n2. Sucursales disponibles:')
for sucursal in Sucursal.objects.filter(activa=True):
    print(f'   - ID: {sucursal.id} | Nombre: {sucursal.nombre}')

# Buscar proveedores por sucursal
print('\n3. Proveedores por sucursal:')
for sucursal in Sucursal.objects.filter(activa=True):
    proveedores_sucursal = Proveedor.objects.filter(sucursal=sucursal, estado='activo')
    print(f'   Sucursal {sucursal.nombre}: {proveedores_sucursal.count()} proveedores')
    for proveedor in proveedores_sucursal[:3]:
        print(f'     * {proveedor.nombre_comercial}')

# Crear un test con usuario específico
print('\n4. Test de filtrado por usuario:')
test_user = Usuario.objects.filter(rol__nombre='gerente', sucursal__isnull=False).first()

if test_user:
    print(f'   Usuario test: {test_user.username}')
    print(f'   Rol: {test_user.rol.nombre}')
    print(f'   Sucursal: {test_user.sucursal.nombre}')
    
    # Simular la lógica del view
    if test_user.rol.nombre == 'gerente' and test_user.sucursal:
        proveedores_usuario = Proveedor.objects.filter(
            estado='activo',
            sucursal=test_user.sucursal
        )
        print(f'   Proveedores que debería ver: {proveedores_usuario.count()}')
        for p in proveedores_usuario:
            print(f'     * {p.nombre_comercial}')
    else:
        print('   Usuario no es gerente con sucursal')
else:
    print('   No se encontró un gerente con sucursal asignada')

print('\n=== TEST COMPLETO ===')
