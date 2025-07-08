import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario, Sucursal
from mesero.models import Mesa

print("\n🏢 INFORMACIÓN DE SUCURSALES Y MESAS")
print("=" * 50)

# 1. Mostrar todas las sucursales
print("\n📍 SUCURSALES EN EL SISTEMA:")
sucursales = Sucursal.objects.all()
for s in sucursales:
    print(f"  ID: {s.id} | Nombre: {s.nombre}")

# 2. Mostrar información del modelo Mesa
print("\n🪑 MODELO MESA (MESERO APP):")
print(f"  Total mesas en sistema: {Mesa.objects.count()}")
print(f"  Total mesas activas: {Mesa.objects.filter(activa=True).count()}")

# 3. Mostrar mesas por sucursal
print("\n📊 MESAS POR SUCURSAL:")
for s in sucursales:
    mesas = Mesa.objects.filter(sucursal=s)
    mesas_activas = mesas.filter(activa=True)
    print(f"  {s.nombre} (ID: {s.id}):")
    print(f"    - Total mesas: {mesas.count()}")
    print(f"    - Mesas activas: {mesas_activas.count()}")
    
    if mesas.count() > 0:
        print(f"    - Listado de mesas:")
        for m in mesas:
            estado_activa = "✅ Activa" if m.activa else "❌ Inactiva"
            print(f"      * Mesa {m.numero} (ID: {m.id}) | Estado: {m.get_estado_display()} | {estado_activa}")

# 4. Mostrar usuarios por sucursal
print("\n👤 USUARIOS POR SUCURSAL:")
for s in sucursales:
    usuarios = Usuario.objects.filter(sucursal=s)
    print(f"  {s.nombre} (ID: {s.id}):")
    print(f"    - Total usuarios: {usuarios.count()}")
    
    if usuarios.count() > 0:
        print(f"    - Listado de usuarios:")
        for u in usuarios:
            grupos = [g.name for g in u.groups.all()]
            print(f"      * {u.username} ({u.first_name} {u.last_name}) | Grupos: {grupos}")

# 5. Mostrar usuarios sin sucursal
print("\n⚠️ USUARIOS SIN SUCURSAL:")
usuarios_sin_sucursal = Usuario.objects.filter(sucursal__isnull=True)
print(f"  Total: {usuarios_sin_sucursal.count()}")
if usuarios_sin_sucursal.count() > 0:
    for u in usuarios_sin_sucursal:
        grupos = [g.name for g in u.groups.all()]
        print(f"    * {u.username} ({u.first_name} {u.last_name}) | Grupos: {grupos}")

print("\n🔍 SOLUCIÓN RECOMENDADA:")
print("1. Si no hay mesas para la sucursal del usuario, CREAR mesas para esa sucursal")
print("2. Si el usuario no tiene sucursal asignada, ASIGNARLE una sucursal")
print("3. Si las mesas existen pero están inactivas, ACTIVARLAS")
