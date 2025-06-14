from restaurant.models import Insumo
from dashboard.views import crear_insumo_elaborado
from django.test import RequestFactory
from accounts.models import Usuario

# Verificar insumos disponibles
print("=== VERIFICACIÓN DE INSUMOS DISPONIBLES ===")
insumos_basicos = Insumo.objects.filter(tipo='basico', activo=True)
insumos_compuestos = Insumo.objects.filter(tipo='compuesto', activo=True)

print(f"Insumos básicos: {insumos_basicos.count()}")
for insumo in insumos_basicos[:5]:
    print(f"  ID {insumo.id}: {insumo.nombre} (Tipo: {insumo.tipo})")

print(f"Insumos compuestos: {insumos_compuestos.count()}")
for insumo in insumos_compuestos[:5]:
    print(f"  ID {insumo.id}: {insumo.nombre} (Tipo: {insumo.tipo})")

print("\n=== VERIFICACIÓN DE USUARIOS ===")
usuarios = Usuario.objects.filter(is_superuser=True)
print(f"Usuarios admin: {usuarios.count()}")
if usuarios.exists():
    print(f"Usuario a usar: {usuarios.first().username}")

# Probar directamente el filtro que usa la vista
print("\n=== PRUEBA DEL FILTRO DE LA VISTA ===")
if insumos_basicos.exists():
    insumo_test = insumos_basicos.first()
    print(f"Probando insumo básico ID {insumo_test.id}: {insumo_test.nombre}")
    
    # Simular el filtro de la vista
    resultado = Insumo.objects.filter(
        id=insumo_test.id, 
        tipo__in=['basico', 'compuesto'],
        activo=True
    )
    print(f"Resultado del filtro: {resultado.count()}")
    if resultado.exists():
        print(f"  ✅ Encontrado: {resultado.first().nombre}")
    else:
        print(f"  ❌ No encontrado con el filtro de la vista")

if insumos_compuestos.exists():
    insumo_test = insumos_compuestos.first()
    print(f"Probando insumo compuesto ID {insumo_test.id}: {insumo_test.nombre}")
    
    # Simular el filtro de la vista
    resultado = Insumo.objects.filter(
        id=insumo_test.id, 
        tipo__in=['basico', 'compuesto'],
        activo=True
    )
    print(f"Resultado del filtro: {resultado.count()}")
    if resultado.exists():
        print(f"  ✅ Encontrado: {resultado.first().nombre}")
    else:
        print(f"  ❌ No encontrado con el filtro de la vista")

print("\n=== VERIFICACIÓN COMPLETA ===")
