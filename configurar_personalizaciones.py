import django
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import OpcionPersonalizacion, ProductoPersonalizacion
from restaurant.models import ProductoVenta, CategoriaProducto

def crear_opciones_personalizacion():
    """Crear opciones de personalización comunes para restaurante de sushi"""
    print("=== CREANDO OPCIONES DE PERSONALIZACIÓN ===")
    
    # Opciones generales para quitar ingredientes
    opciones_quitar = [
        "Sin cebolla",
        "Sin ajonjolí",
        "Sin aguacate",
        "Sin pepino",
        "Sin zanahoria",
        "Sin salsa de soya",
        "Sin wasabi",
        "Sin jengibre",
        "Sin alga nori",
        "Sin picante",
        "Sin salsa teriyaki",
        "Sin salsa de anguila",
    ]
    
    # Opciones para agregar extras
    opciones_agregar = [
        ("Extra aguacate", 15.00),
        ("Extra salmón", 25.00),
        ("Extra atún", 30.00),
        ("Extra queso crema", 10.00),
        ("Extra tempura", 20.00),
        ("Extra ajonjolí", 5.00),
        ("Extra salsa spicy", 8.00),
        ("Extra wasabi", 5.00),
        ("Extra jengibre", 5.00),
        ("Porción extra de arroz", 12.00),
    ]
    
    # Opciones de cambios
    opciones_cambiar = [
        "Cambiar salmón por atún",
        "Cambiar atún por salmón",
        "Cambiar pollo por camarón",
        "Cambiar camarón por pollo",
        "Arroz integral en lugar de blanco",
        "Salsa teriyaki en lugar de soya",
    ]
    
    # Crear opciones para quitar
    for opcion in opciones_quitar:
        obj, created = OpcionPersonalizacion.objects.get_or_create(
            nombre=opcion,
            tipo='quitar',
            defaults={
                'precio_extra': 0.00,
                'activa': True
            }
        )
        if created:
            print(f"✓ Creada opción: {opcion}")
    
    # Crear opciones para agregar
    for opcion, precio in opciones_agregar:
        obj, created = OpcionPersonalizacion.objects.get_or_create(
            nombre=opcion,
            tipo='agregar',
            defaults={
                'precio_extra': precio,
                'activa': True
            }
        )
        if created:
            print(f"✓ Creada opción: {opcion} (+${precio})")
    
    # Crear opciones para cambiar
    for opcion in opciones_cambiar:
        obj, created = OpcionPersonalizacion.objects.get_or_create(
            nombre=opcion,
            tipo='cambiar',
            defaults={
                'precio_extra': 0.00,
                'activa': True
            }
        )
        if created:
            print(f"✓ Creada opción: {opcion}")
    
    # Crear opción para notas especiales
    obj, created = OpcionPersonalizacion.objects.get_or_create(
        nombre="Nota especial",
        tipo='nota',
        defaults={
            'precio_extra': 0.00,
            'activa': True
        }
    )
    if created:
        print("✓ Creada opción: Nota especial")

def asignar_personalizaciones_productos():
    """Asignar opciones de personalización a productos"""
    print("\n=== ASIGNANDO PERSONALIZACIONES A PRODUCTOS ===")
    
    # Obtener productos
    productos = ProductoVenta.objects.filter(disponible=True)
    
    # Obtener opciones
    opciones_quitar = OpcionPersonalizacion.objects.filter(tipo='quitar')
    opciones_agregar = OpcionPersonalizacion.objects.filter(tipo='agregar')
    opciones_cambiar = OpcionPersonalizacion.objects.filter(tipo='cambiar')
    opcion_nota = OpcionPersonalizacion.objects.filter(tipo='nota').first()
    
    for producto in productos:
        print(f"\nConfigurando personalizaciones para: {producto.nombre}")
        
        # Asignar opciones básicas de quitar a todos los productos
        opciones_basicas_quitar = [
            "Sin cebolla", "Sin picante", "Sin wasabi", 
            "Sin jengibre", "Sin salsa de soya"
        ]
        
        for opcion_nombre in opciones_basicas_quitar:
            try:
                opcion = opciones_quitar.get(nombre=opcion_nombre)
                obj, created = ProductoPersonalizacion.objects.get_or_create(
                    producto=producto,
                    opcion=opcion,
                    defaults={'activa': True}
                )
                if created:
                    print(f"  ✓ {opcion_nombre}")
            except OpcionPersonalizacion.DoesNotExist:
                continue
        
        # Asignar opciones específicas según el tipo de producto
        nombre_lower = producto.nombre.lower()
        
        # Para rolls y makis
        if any(palabra in nombre_lower for palabra in ['roll', 'maki', 'sushi']):
            opciones_sushi = [
                "Sin ajonjolí", "Sin aguacate", "Sin pepino", 
                "Sin alga nori", "Sin salsa teriyaki", "Sin salsa de anguila"
            ]
            
            for opcion_nombre in opciones_sushi:
                try:
                    opcion = opciones_quitar.get(nombre=opcion_nombre)
                    obj, created = ProductoPersonalizacion.objects.get_or_create(
                        producto=producto,
                        opcion=opcion,
                        defaults={'activa': True}
                    )
                    if created:
                        print(f"  ✓ {opcion_nombre}")
                except OpcionPersonalizacion.DoesNotExist:
                    continue
            
            # Extras para sushi
            extras_sushi = [
                "Extra aguacate", "Extra ajonjolí", "Extra salsa spicy"
            ]
            
            if 'salmón' in nombre_lower or 'salmon' in nombre_lower:
                extras_sushi.append("Extra salmón")
            if 'atún' in nombre_lower or 'atun' in nombre_lower:
                extras_sushi.append("Extra atún")
            if 'queso' in nombre_lower:
                extras_sushi.append("Extra queso crema")
            
            for opcion_nombre in extras_sushi:
                try:
                    opcion = opciones_agregar.get(nombre=opcion_nombre)
                    obj, created = ProductoPersonalizacion.objects.get_or_create(
                        producto=producto,
                        opcion=opcion,
                        defaults={'activa': True}
                    )
                    if created:
                        print(f"  ✓ {opcion_nombre}")
                except OpcionPersonalizacion.DoesNotExist:
                    continue
        
        # Para tempuras
        if 'tempura' in nombre_lower:
            opciones_tempura = ["Sin zanahoria", "Sin salsa teriyaki"]
            extras_tempura = ["Extra tempura"]
            
            for opcion_nombre in opciones_tempura:
                try:
                    opcion = opciones_quitar.get(nombre=opcion_nombre)
                    obj, created = ProductoPersonalizacion.objects.get_or_create(
                        producto=producto,
                        opcion=opcion,
                        defaults={'activa': True}
                    )
                    if created:
                        print(f"  ✓ {opcion_nombre}")
                except OpcionPersonalizacion.DoesNotExist:
                    continue
            
            for opcion_nombre in extras_tempura:
                try:
                    opcion = opciones_agregar.get(nombre=opcion_nombre)
                    obj, created = ProductoPersonalizacion.objects.get_or_create(
                        producto=producto,
                        opcion=opcion,
                        defaults={'activa': True}
                    )
                    if created:
                        print(f"  ✓ {opcion_nombre}")
                except OpcionPersonalizacion.DoesNotExist:
                    continue
        
        # Asignar opción de nota especial a todos los productos
        if opcion_nota:
            obj, created = ProductoPersonalizacion.objects.get_or_create(
                producto=producto,
                opcion=opcion_nota,
                defaults={'activa': True}
            )
            if created:
                print(f"  ✓ Nota especial")

def mostrar_resumen():
    """Mostrar resumen de las personalizaciones creadas"""
    print("\n=== RESUMEN DE PERSONALIZACIONES ===")
    
    total_opciones = OpcionPersonalizacion.objects.count()
    total_productos = ProductoVenta.objects.filter(disponible=True).count()
    total_asignaciones = ProductoPersonalizacion.objects.count()
    
    print(f"Total opciones creadas: {total_opciones}")
    print(f"Total productos disponibles: {total_productos}")
    print(f"Total asignaciones: {total_asignaciones}")
    
    # Mostrar opciones por tipo
    for tipo, nombre_tipo in OpcionPersonalizacion.TIPO_CHOICES:
        count = OpcionPersonalizacion.objects.filter(tipo=tipo).count()
        print(f"  {nombre_tipo}: {count} opciones")
    
    print("\n✅ Sistema de personalización configurado correctamente")
    print("Ahora los meseros podrán personalizar los pedidos según las preferencias del cliente")

def main():
    """Función principal"""
    try:
        crear_opciones_personalizacion()
        asignar_personalizaciones_productos()
        mostrar_resumen()
        
        print("\n🎯 PRÓXIMOS PASOS:")
        print("1. Actualizar la interfaz del mesero para mostrar opciones de personalización")
        print("2. Implementar modal de personalización")
        print("3. Actualizar la lógica de creación de órdenes")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
