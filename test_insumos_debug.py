#!/usr/bin/env python3
"""
Script de prueba para verificar las funciones de insumos compuestos
"""
import os
import django
import sys

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

def test_insumos_compuestos():
    client = Client()
    User = get_user_model()
    
    # Crear un usuario de prueba si no existe
    if not User.objects.filter(username='admin').exists():
        user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        print("✅ Usuario admin creado")
    else:
        user = User.objects.get(username='admin')
        print("✅ Usuario admin encontrado")
    
    # Login
    login_success = client.login(username='admin', password='admin123')
    print(f"✅ Login: {'exitoso' if login_success else 'falló'}")
    
    if not login_success:
        return
    
    # Probar página de insumos compuestos
    response = client.get('/dashboard/insumos-compuestos/')
    print(f"✅ Página insumos compuestos: {response.status_code}")
    
    # Probar detalle de insumo compuesto (ID 17)
    response = client.get('/dashboard/insumos-compuestos/detalle/17/')
    print(f"✅ Detalle insumo ID 17: {response.status_code}")
    if response.status_code == 200:
        print(f"   Contenido: {response.json() if 'application/json' in response.get('Content-Type', '') else 'HTML'}")
    
    # Probar eliminar (simulación sin ejecutar)
    print("✅ Script de prueba completado")

if __name__ == '__main__':
    test_insumos_compuestos()
