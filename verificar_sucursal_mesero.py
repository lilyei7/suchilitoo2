import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario, Sucursal

print("=== VERIFICACIÓN Y ASIGNACIÓN DE SUCURSAL ===")

# Buscar el usuario mesero_test
try:
    usuario = Usuario.objects.get(username='mesero_test')
    print(f"Usuario encontrado: {usuario.username}")
    print(f"Nombre completo: {usuario.get_full_name()}")
    print(f"Sucursal actual: {usuario.sucursal}")
    
    if not usuario.sucursal:
        print("\n🔸 Usuario no tiene sucursal asignada. Buscando sucursales disponibles...")
        
        # Buscar sucursales activas
        sucursales = Sucursal.objects.filter(activa=True)
        print(f"Sucursales activas encontradas: {sucursales.count()}")
        
        if sucursales.exists():
            # Asignar la primera sucursal activa
            sucursal = sucursales.first()
            usuario.sucursal = sucursal
            usuario.save()
            
            print(f"✅ Sucursal asignada: {sucursal.nombre}")
            print(f"📍 Dirección: {sucursal.direccion}")
        else:
            print("⚠️  No hay sucursales activas. Creando una sucursal de ejemplo...")
            
            # Crear sucursal de ejemplo
            sucursal = Sucursal.objects.create(
                nombre="Sushi Central",
                direccion="Av. Principal 123, Centro",
                telefono="123-456-7890",
                email="central@sushilitoo.com",
                activa=True,
                fecha_apertura="2024-01-01"
            )
            
            usuario.sucursal = sucursal
            usuario.save()
            
            print(f"✅ Nueva sucursal creada y asignada: {sucursal.nombre}")
    else:
        print(f"✅ Usuario ya tiene sucursal asignada: {usuario.sucursal.nombre}")
        print(f"📍 Dirección: {usuario.sucursal.direccion}")

except Usuario.DoesNotExist:
    print("❌ Usuario 'mesero_test' no encontrado")

print("\n=== RESUMEN DE SUCURSALES ===")
sucursales = Sucursal.objects.all()
for sucursal in sucursales:
    usuarios_count = Usuario.objects.filter(sucursal=sucursal).count()
    print(f"🏢 {sucursal.nombre}")
    print(f"   📍 {sucursal.direccion}")
    print(f"   👥 {usuarios_count} usuarios asignados")
    print(f"   🟢 {'Activa' if sucursal.activa else 'Inactiva'}")
    print()

print("=== FIN DE LA VERIFICACIÓN ===")
