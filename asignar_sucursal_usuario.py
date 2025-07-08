#!/usr/bin/env python
"""
Script para asignar una sucursal al usuario para probar la navegación
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from accounts.models import Usuario, Sucursal
from django.db import transaction

def asignar_sucursal_usuario():
    """Asignar una sucursal al usuario para testing"""
    print("=== ASIGNACIÓN DE SUCURSAL PARA TESTING ===")
    
    try:
        # Obtener o crear una sucursal
        sucursal, created = Sucursal.objects.get_or_create(
            nombre="Sucursal Centro",
            defaults={
                'direccion': 'Av. Principal 123',
                'telefono': '555-1234',
                'email': 'centro@sushirestaurant.com',
                'activa': True
            }
        )
        
        if created:
            print(f"✅ Sucursal creada: {sucursal.nombre}")
        else:
            print(f"✅ Sucursal encontrada: {sucursal.nombre}")
        
        # Obtener todos los usuarios sin sucursal
        usuarios_sin_sucursal = Usuario.objects.filter(sucursal__isnull=True)
        
        if usuarios_sin_sucursal.exists():
            print(f"\n📋 Usuarios sin sucursal asignada: {usuarios_sin_sucursal.count()}")
            
            with transaction.atomic():
                for usuario in usuarios_sin_sucursal:
                    usuario.sucursal = sucursal
                    usuario.save()
                    print(f"   - {usuario.username} → {sucursal.nombre}")
            
            print(f"\n✅ {usuarios_sin_sucursal.count()} usuarios actualizados")
        else:
            print("\n✅ Todos los usuarios ya tienen sucursal asignada")
        
        # Mostrar resumen
        print(f"\n📊 RESUMEN:")
        total_usuarios = Usuario.objects.count()
        usuarios_con_sucursal = Usuario.objects.filter(sucursal__isnull=False).count()
        
        print(f"   Total usuarios: {total_usuarios}")
        print(f"   Con sucursal: {usuarios_con_sucursal}")
        print(f"   Sin sucursal: {total_usuarios - usuarios_con_sucursal}")
        
        print(f"\n🎯 LISTO PARA PROBAR:")
        print(f"   1. Ve a: http://127.0.0.1:8000/cocina/")
        print(f"   2. Verás el nuevo diseño de navegación")
        print(f"   3. La información del chef y sucursal aparecerá en la navbar")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asignar_sucursal_usuario()
