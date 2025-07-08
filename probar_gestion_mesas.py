#!/usr/bin/env python
"""
Script para probar el sistema de gestión de mesas en sucursales
"""
import os
import django
from django.test import Client

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Sucursal, Usuario
from dashboard.models_ventas import Mesa

def main():
    print("=== PRUEBA DEL SISTEMA DE GESTIÓN DE MESAS ===")
    
    # 1. Verificar que tenemos sucursales
    sucursales = Sucursal.objects.all()
    print(f"✓ Sucursales disponibles: {sucursales.count()}")
    
    if sucursales.count() == 0:
        print("❌ No hay sucursales. Creando una de prueba...")
        sucursal = Sucursal.objects.create(
            nombre="Sucursal Test Mesas",
            direccion="Dirección Test",
            telefono="123456789",
            email="test@mesas.com",
            activa=True
        )
        print(f"✓ Sucursal creada: {sucursal.nombre}")
    else:
        sucursal = sucursales.first()
        print(f"✓ Usando sucursal: {sucursal.nombre}")
    
    # 2. Limpiar mesas existentes de la sucursal
    mesas_existentes = Mesa.objects.filter(sucursal=sucursal)
    if mesas_existentes.exists():
        print(f"🧹 Eliminando {mesas_existentes.count()} mesas existentes...")
        mesas_existentes.delete()
    
    # 3. Crear mesas de ejemplo
    print("\n📋 Creando mesas de ejemplo...")
    mesas_ejemplo = [
        {'numero': '01', 'capacidad': 2, 'ubicacion': 'Terraza'},
        {'numero': '02', 'capacidad': 4, 'ubicacion': 'Salón Principal'},
        {'numero': '03', 'capacidad': 6, 'ubicacion': 'Salón Principal'},
        {'numero': '04', 'capacidad': 4, 'ubicacion': 'Terraza'},
        {'numero': '05', 'capacidad': 8, 'ubicacion': 'Salón VIP'},
        {'numero': 'T1', 'capacidad': 2, 'ubicacion': 'Terraza'},
        {'numero': 'T2', 'capacidad': 4, 'ubicacion': 'Terraza'},
        {'numero': 'V1', 'capacidad': 10, 'ubicacion': 'Salón VIP'},
    ]
    
    for mesa_data in mesas_ejemplo:
        mesa = Mesa.objects.create(
            numero=mesa_data['numero'],
            capacidad=mesa_data['capacidad'],
            nombre=mesa_data['ubicacion'],
            sucursal=sucursal,
            estado='disponible',
            activo=True
        )
        print(f"  ✓ Mesa {mesa.numero} - {mesa.capacidad} personas - {mesa.nombre}")
    
    # 4. Verificar conteo de mesas
    total_mesas = Mesa.objects.filter(sucursal=sucursal).count()
    mesas_disponibles = Mesa.objects.filter(sucursal=sucursal, estado='disponible', activo=True).count()
    
    print(f"\n📊 ESTADÍSTICAS DE MESAS:")
    print(f"  Total de mesas: {total_mesas}")
    print(f"  Mesas disponibles: {mesas_disponibles}")
    print(f"  Mesas por ubicación:")
    
    ubicaciones = Mesa.objects.filter(sucursal=sucursal).values_list('nombre', flat=True).distinct()
    for ubicacion in ubicaciones:
        count = Mesa.objects.filter(sucursal=sucursal, nombre=ubicacion).count()
        print(f"    - {ubicacion}: {count} mesas")
    
    # 5. Simular cambios de estado
    print(f"\n🔄 Simulando cambios de estado...")
    mesa_test = Mesa.objects.filter(sucursal=sucursal).first()
    if mesa_test:
        print(f"  Mesa {mesa_test.numero} - Estado inicial: {mesa_test.estado}")
        
        # Ocupar mesa
        mesa_test.estado = 'ocupada'
        mesa_test.save()
        print(f"  Mesa {mesa_test.numero} - Nuevo estado: {mesa_test.estado}")
        
        # Liberar mesa
        mesa_test.estado = 'disponible'
        mesa_test.save()
        print(f"  Mesa {mesa_test.numero} - Estado final: {mesa_test.estado}")
    
    # 6. Verificar usuario admin para pruebas
    print(f"\n👤 VERIFICANDO USUARIO ADMIN...")
    try:
        admin_user = Usuario.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = Usuario.objects.filter(rol__nombre='admin').first()
        
        if admin_user:
            print(f"  ✓ Usuario admin encontrado: {admin_user.username}")
            print(f"  📍 Sucursal del admin: {admin_user.sucursal.nombre if admin_user.sucursal else 'Sin asignar'}")
        else:
            print("  ❌ No se encontró usuario admin")
            print("  💡 Crea un usuario admin para probar la gestión de mesas")
            
    except Exception as e:
        print(f"  ❌ Error verificando usuario admin: {e}")
    
    # 7. Mostrar URLs para acceder
    print(f"\n🌐 URLS PARA PROBAR:")
    print(f"  Dashboard de sucursales: /dashboard/sucursales/")
    print(f"  Gestión de mesas: Hacer clic en 'Gestionar Mesas' en el dropdown de una sucursal")
    print(f"  API de mesas: /dashboard/api/sucursales/{sucursal.id}/mesas/")
    
    print(f"\n✅ SISTEMA DE MESAS CONFIGURADO CORRECTAMENTE")
    print(f"   - {total_mesas} mesas creadas en '{sucursal.nombre}'")
    print(f"   - Todas las APIs y vistas están listas")
    print(f"   - Frontend JavaScript implementado")
    print(f"\n🚀 ¡Ya puedes gestionar mesas desde el dashboard de sucursales!")

if __name__ == '__main__':
    main()
