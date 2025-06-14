#!/usr/bin/env python
"""
Demostración completa de funcionalidades de Sucursales
Este script crea datos de ejemplo para probar todas las funcionalidades CRUD
"""
import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Sucursal, Usuario, Rol

def crear_datos_demo():
    """Crear datos de demostración para sucursales"""
    print("🏢 === DEMO DE SUCURSALES ===")
    print("🚀 Creando datos de demostración...\n")
    
    # Crear sucursales de ejemplo
    sucursales_data = [
        {
            'nombre': 'Sucursal Centro',
            'direccion': 'Av. Reforma #123, Centro Histórico, CDMX 06000',
            'telefono': '555-0101',
            'email': 'centro@sushirestaurant.com',
            'fecha_apertura': date.today() - timedelta(days=365),
            'activa': True
        },
        {
            'nombre': 'Sucursal Polanco',
            'direccion': 'Av. Masaryk #456, Polanco, CDMX 11560',
            'telefono': '555-0202',
            'email': 'polanco@sushirestaurant.com',
            'fecha_apertura': date.today() - timedelta(days=180),
            'activa': True
        },
        {
            'nombre': 'Sucursal Roma Norte',
            'direccion': 'Calle Álvaro Obregón #789, Roma Norte, CDMX 06700',
            'telefono': '555-0303',
            'email': 'roma@sushirestaurant.com',
            'fecha_apertura': date.today() - timedelta(days=90),
            'activa': True
        },
        {
            'nombre': 'Sucursal Guadalajara',
            'direccion': 'Av. Chapultepec #321, Zona Rosa, Guadalajara, JAL 44140',
            'telefono': '333-0404',
            'email': 'guadalajara@sushirestaurant.com',
            'fecha_apertura': date.today() - timedelta(days=60),
            'activa': True
        },
        {
            'nombre': 'Sucursal Monterrey',
            'direccion': 'Av. Constitución #654, Centro, Monterrey, NL 64000',
            'telefono': '811-0505',
            'email': 'monterrey@sushirestaurant.com',
            'fecha_apertura': date.today() - timedelta(days=30),
            'activa': False  # Esta sucursal está temporalmente cerrada
        }
    ]
    
    # Crear o actualizar sucursales
    for sucursal_data in sucursales_data:
        sucursal, created = Sucursal.objects.update_or_create(
            nombre=sucursal_data['nombre'],
            defaults=sucursal_data
        )
        
        status = "✅ Creada" if created else "🔄 Actualizada"
        estado = "🟢 Activa" if sucursal.activa else "🔴 Inactiva"
        print(f"{status}: {sucursal.nombre} - {estado}")
        print(f"   📍 {sucursal.direccion}")
        print(f"   📞 {sucursal.telefono} | 📧 {sucursal.email}")
        print(f"   📅 Apertura: {sucursal.fecha_apertura}")
        print()
    
    # Estadísticas finales
    total = Sucursal.objects.count()
    activas = Sucursal.objects.filter(activa=True).count()
    inactivas = total - activas
    
    print("📊 === ESTADÍSTICAS ===")
    print(f"🏢 Total de sucursales: {total}")
    print(f"🟢 Sucursales activas: {activas}")
    print(f"🔴 Sucursales inactivas: {inactivas}")
    print()
    
    print("🌟 === FUNCIONALIDADES DISPONIBLES ===")
    print("✅ Crear nueva sucursal (con todos los campos)")
    print("✅ Ver detalles completos de sucursal")
    print("✅ Editar información de sucursal")
    print("✅ Activar/Desactivar sucursal")
    print("✅ Eliminar sucursal (con validaciones)")
    print("✅ Vista de empleados por sucursal")
    print("✅ Estadísticas en tiempo real")
    print("✅ Interface responsiva con modales")
    print("✅ Validaciones de formulario")
    print("✅ Mensajes de toast informativos")
    print()
    
    print("🚀 === CÓMO PROBAR ===")
    print("1. Ve a: http://127.0.0.1:8000/dashboard/sucursales/")
    print("2. Haz clic en 'Nueva Sucursal' para crear")
    print("3. Haz clic en 'Ver' para ver detalles")
    print("4. Haz clic en 'Editar' para modificar")
    print("5. Usa el menú '⋮' para más opciones")
    print()
    
    print("✨ ¡Demo completada! Todas las funcionalidades están listas para usar.")

if __name__ == '__main__':
    crear_datos_demo()
