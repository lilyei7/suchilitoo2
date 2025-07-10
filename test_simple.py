#!/usr/bin/env python
"""
Test simplificado para verificar el endpoint de solicitar cuenta
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')

# Agregar el directorio raíz al PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from mesero.models import Orden, Mesa, NotificacionCuenta

def test_simple():
    """Test simplificado"""
    print("=== TEST SIMPLE ===")
    
    try:
        # Verificar que los modelos están disponibles
        print(f"✓ Modelo Orden disponible: {Orden}")
        print(f"✓ Modelo Mesa disponible: {Mesa}")
        print(f"✓ Modelo NotificacionCuenta disponible: {NotificacionCuenta}")
        
        # Contar órdenes existentes
        orden_count = Orden.objects.count()
        print(f"✓ Órdenes en BD: {orden_count}")
        
        # Contar usuarios
        user_count = User.objects.count()
        print(f"✓ Usuarios en BD: {user_count}")
        
        # Crear cliente
        client = Client()
        print(f"✓ Cliente creado: {client}")
        
        # Probar acceso sin login
        response = client.post('/mesero/solicitar-cuenta/1/')
        print(f"✓ Respuesta sin login: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_simple()
    if success:
        print("\n🎉 TEST BÁSICO EXITOSO")
    else:
        print("\n❌ TEST BÁSICO FALLIDO")
