#!/usr/bin/env python
"""
Script para crear más escenarios de prueba visual de proveedores.
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Insumo
from dashboard.models import Proveedor, ProveedorInsumo
from accounts.models import Usuario

def main():
    print("🎨 CREANDO ESCENARIOS VISUALES PARA PROVEEDORES")
    print("=" * 60)
    
    try:
        # Buscar un usuario admin
        admin_user = Usuario.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = Usuario.objects.filter(rol__nombre='admin').first()
        
        if not admin_user:
            print("❌ No se encontró un usuario administrador")
            return
        
        # Crear proveedores de ejemplo si no existen suficientes
        proveedores_existentes = Proveedor.objects.count()
        print(f"📊 Proveedores existentes: {proveedores_existentes}")
        
        if proveedores_existentes < 5:
            print("🔧 Creando proveedores adicionales para mejores pruebas visuales...")
            
            proveedores_ejemplo = [
                {
                    'nombre_comercial': 'Súper Distribuidora XYZ',
                    'persona_contacto': 'Carlos Mendoza',
                    'telefono': '+51 987 654 321',
                    'email': 'ventas@superdistribuidora.com',
                    'direccion': 'Av. Los Proceres 123, Lima'
                },
                {
                    'nombre_comercial': 'Fresh Ingredients Co.',
                    'persona_contacto': 'María González',
                    'telefono': '+51 976 543 210',
                    'email': 'maria@freshingredients.pe',
                    'direccion': 'Jr. Comercio 456, Miraflores'
                },
                {
                    'nombre_comercial': 'Mariscos del Pacífico Premium',
                    'persona_contacto': 'Roberto Silva',
                    'telefono': '+51 965 432 109',
                    'email': 'roberto@mariscospacifico.com',
                    'direccion': 'Malecón de la Marina 789, Callao'
                }
            ]
            
            for prov_data in proveedores_ejemplo:
                if not Proveedor.objects.filter(nombre_comercial=prov_data['nombre_comercial']).exists():
                    proveedor = Proveedor.objects.create(
                        creado_por=admin_user,
                        **prov_data
                    )
                    print(f"   ✅ Creado: {proveedor.nombre_comercial}")
        
        # Crear escenarios específicos para visualización
        print(f"\n🎯 CREANDO ESCENARIOS ESPECÍFICOS")
        
        # Escenario 1: Insumo con 3 proveedores (visual atractivo)
        insumo_multiple = Insumo.objects.filter(nombre__icontains='arroz').first()
        if not insumo_multiple:
            from restaurant.models import CategoriaInsumo, UnidadMedida
            categoria = CategoriaInsumo.objects.first()
            unidad = UnidadMedida.objects.first()
            
            insumo_multiple = Insumo.objects.create(
                codigo="ARZ-001",
                nombre="Arroz Premium Koshihikari",
                categoria=categoria,
                unidad_medida=unidad,
                precio_unitario=25.50,
                stock_minimo=50,
                descripcion="Arroz japonés de alta calidad para sushi"
            )
        
        # Limpiar relaciones existentes
        ProveedorInsumo.objects.filter(insumo=insumo_multiple).delete()
        
        # Asignar múltiples proveedores con diferentes características
        proveedores = Proveedor.objects.all()[:3]
        precios_ejemplo = [22.50, 25.00, 23.75]
        tiempos_entrega = [2, 3, 1]
        cantidades_min = [25, 50, 30]
        notas_ejemplo = [
            "Excelente calidad, siempre puntual",
            "Mejor precio del mercado, buena relación calidad-precio",
            "Entrega más rápida, ideal para pedidos urgentes"
        ]
        
        for i, proveedor in enumerate(proveedores):
            relacion = ProveedorInsumo.objects.create(
                proveedor=proveedor,
                insumo=insumo_multiple,
                precio_unitario=precios_ejemplo[i],
                cantidad_minima=cantidades_min[i],
                tiempo_entrega_dias=tiempos_entrega[i],
                notas=notas_ejemplo[i]
            )
            print(f"   ✅ Asignado {proveedor.nombre_comercial} - ${relacion.precio_unitario}")
        
        # Escenario 2: Insumo con solo proveedor principal (diseño limpio)
        insumo_principal = Insumo.objects.filter(proveedor_principal__isnull=False).first()
        if insumo_principal:
            ProveedorInsumo.objects.filter(insumo=insumo_principal).delete()
            print(f"   ✅ {insumo_principal.nombre} configurado solo con proveedor principal")
        
        # Mostrar resumen
        print(f"\n📋 RESUMEN DE ESCENARIOS VISUALES:")
        print(f"   🎨 Múltiples proveedores: {insumo_multiple.nombre} (ID: {insumo_multiple.id})")
        print(f"   🎨 Solo principal: {insumo_principal.nombre if insumo_principal else 'N/A'}")
        
        print(f"\n🌐 INSTRUCCIONES PARA PROBAR:")
        print(f"   1. Ve a: http://127.0.0.1:8000/dashboard/inventario/")
        print(f"   2. Busca '{insumo_multiple.nombre}' - debe mostrar dropdown con 3 proveedores")
        print(f"   3. Haz clic en 'Ver detalles' para ver el modal mejorado")
        print(f"   4. Observa las tarjetas de proveedores con colores y badges")
        print(f"   5. Verifica que los iconos y animaciones funcionen")
        
        print(f"\n✨ CARACTERÍSTICAS NUEVAS:")
        print(f"   • Tarjetas de proveedores con gradientes de color")
        print(f"   • Badges animados para diferenciar tipos de proveedor")
        print(f"   • Dropdown elegante con contador animado")
        print(f"   • Modal con diseño tipo cards moderno")
        print(f"   • Iconos animados y hover effects")
        print(f"   • Información organizada en secciones")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
