#!/usr/bin/env python
"""
Script simple para verificar datos del inventario
"""
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario, Sucursal
from restaurant.models import Inventario, Insumo

# Verificar datos básicos
print("=== VERIFICACIÓN DE DATOS ===")

# Usuarios
admin_users = Usuario.objects.filter(is_superuser=True)
gerente_users = Usuario.objects.filter(rol__nombre='gerente')
print(f"✅ Administradores: {admin_users.count()}")
print(f"✅ Gerentes: {gerente_users.count()}")

# Sucursales
sucursales = Sucursal.objects.filter(activa=True)
print(f"✅ Sucursales activas: {sucursales.count()}")
for sucursal in sucursales:
    inventarios_count = Inventario.objects.filter(sucursal=sucursal).count()
    print(f"   - {sucursal.nombre}: {inventarios_count} registros de inventario")

# Insumos e inventarios
insumos_total = Insumo.objects.filter(activo=True).count()
inventarios_total = Inventario.objects.count()
print(f"✅ Insumos activos: {insumos_total}")
print(f"✅ Registros de inventario: {inventarios_total}")

# Verificar que hay inventarios por sucursal
for sucursal in sucursales:
    inventarios = Inventario.objects.filter(sucursal=sucursal)
    insumos_con_stock = inventarios.filter(cantidad_actual__gt=0)
    print(f"✅ {sucursal.nombre}: {inventarios.count()} inventarios, {insumos_con_stock.count()} con stock")

# Importar la vista para probar manualmente
from dashboard.views.inventario_views import inventario_view
from django.http import HttpRequest
from django.contrib.auth import get_user

# Crear request manual
request = HttpRequest()
request.method = 'GET'
request.user = admin_users.first()

try:
    print("\n=== PROBANDO VISTA DIRECTAMENTE ===")
    response = inventario_view(request)
    print(f"✅ Vista ejecutada exitosamente: Status {response.status_code}")
except Exception as e:
    print(f"❌ Error en la vista: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n=== VERIFICACIÓN COMPLETADA ===")
