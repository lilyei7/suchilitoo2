import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import Mesa
from accounts.models import Sucursal, Usuario

print("🔍 DIAGNÓSTICO COMPLETO DE MESAS")
print("=" * 60)

# 1. Verificar sucursales
print("\n1. SUCURSALES DISPONIBLES:")
sucursales = Sucursal.objects.all()
for s in sucursales:
    print(f"   ID: {s.id} | Nombre: '{s.nombre}'")

# 2. Verificar usuarios y sus sucursales
print("\n2. USUARIOS Y SUS SUCURSALES:")
usuarios = Usuario.objects.all()
for u in usuarios:
    sucursal_nombre = u.sucursal.nombre if u.sucursal else "SIN SUCURSAL"
    print(f"   {u.username} -> {sucursal_nombre}")

# 3. Verificar mesas en la aplicación mesero
print("\n3. MESAS EN LA APLICACIÓN MESERO:")
mesas_mesero = Mesa.objects.all()
print(f"   Total mesas en mesero.models: {mesas_mesero.count()}")
for m in mesas_mesero:
    print(f"   ID: {m.id} | Número: {m.numero} | Sucursal: {m.sucursal.nombre} | Activa: {m.activa}")

# 4. Verificar mesas en dashboard (si existen)
try:
    from dashboard.models_ventas import Mesa as MesaDashboard
    print("\n4. MESAS EN DASHBOARD:")
    mesas_dashboard = MesaDashboard.objects.all()
    print(f"   Total mesas en dashboard.models_ventas: {mesas_dashboard.count()}")
    for m in mesas_dashboard:
        activo = getattr(m, 'activo', getattr(m, 'activa', 'N/A'))
        print(f"   ID: {m.id} | Número: {m.numero} | Sucursal: {m.sucursal.nombre} | Activo: {activo}")
except ImportError:
    print("\n4. NO HAY MODELO MESA EN DASHBOARD")

# 5. Crear mesas para Sucursal Centro si no existen
print("\n5. CREANDO MESAS PARA SUCURSAL CENTRO:")
try:
    sucursal_centro = Sucursal.objects.get(nombre='Sucursal Centro')
    print(f"   Sucursal encontrada: {sucursal_centro.nombre} (ID: {sucursal_centro.id})")
    
    mesas_existentes = Mesa.objects.filter(sucursal=sucursal_centro).count()
    print(f"   Mesas existentes en Sucursal Centro: {mesas_existentes}")
    
    if mesas_existentes == 0:
        print("   Creando 8 mesas...")
        for num in range(1, 9):
            numero = f"{num:02d}"
            mesa = Mesa.objects.create(
                numero=numero,
                capacidad=4,
                estado='disponible',
                sucursal=sucursal_centro,
                activa=True
            )
            print(f"   ✓ Creada Mesa {numero} (ID: {mesa.id})")
    else:
        print("   Las mesas ya existen")
        
except Sucursal.DoesNotExist:
    print("   ❌ ERROR: No se encontró la Sucursal Centro")

# 6. Verificar mesas después de la creación
print("\n6. MESAS FINALES EN SUCURSAL CENTRO:")
try:
    sucursal_centro = Sucursal.objects.get(nombre='Sucursal Centro')
    mesas_finales = Mesa.objects.filter(sucursal=sucursal_centro, activa=True)
    print(f"   Total mesas activas: {mesas_finales.count()}")
    for m in mesas_finales:
        print(f"   Mesa {m.numero} (ID: {m.id}) - Estado: {m.estado}")
except Sucursal.DoesNotExist:
    print("   ❌ No se encontró la Sucursal Centro")

print("\n" + "=" * 60)
print("🎯 RESUMEN:")
print(f"   - Total sucursales: {sucursales.count()}")
print(f"   - Total usuarios: {usuarios.count()}")
print(f"   - Total mesas en mesero: {Mesa.objects.count()}")

# 7. Simular la consulta de la vista
print("\n7. SIMULANDO CONSULTA DE LA VISTA:")
try:
    # Obtener un usuario de Sucursal Centro
    usuario_centro = Usuario.objects.filter(sucursal__nombre='Sucursal Centro').first()
    if usuario_centro:
        print(f"   Usuario de prueba: {usuario_centro.username}")
        print(f"   Sucursal del usuario: {usuario_centro.sucursal.nombre}")
        
        # Simular la consulta que hace la vista
        mesas_vista = Mesa.objects.filter(
            sucursal=usuario_centro.sucursal,
            activa=True
        ).order_by('numero')
        
        print(f"   Mesas que vería en la vista: {mesas_vista.count()}")
        for m in mesas_vista:
            print(f"   - Mesa {m.numero} (ID: {m.id})")
    else:
        print("   ❌ No hay usuarios en Sucursal Centro")
except Exception as e:
    print(f"   ❌ Error en simulación: {e}")

print("\n✅ DIAGNÓSTICO COMPLETADO")
