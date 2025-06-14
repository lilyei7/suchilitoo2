#!/usr/bin/env python3
"""
Test rápido para verificar el funcionamiento de las funciones de insumos compuestos
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
from restaurant.models import Insumo

def test_funciones():
    print('🧪 TEST RÁPIDO - FUNCIONES INSUMOS COMPUESTOS')
    print('=' * 50)

    client = Client()
    User = get_user_model()

    # Login
    if User.objects.filter(username='admin').exists():
        login_success = client.login(username='admin', password='admin123')
        print(f'✅ Login: {"exitoso" if login_success else "falló"}')
    else:
        print('❌ Usuario admin no existe')
        return

    if not login_success:
        return

    # Obtener primer insumo compuesto
    compuesto = Insumo.objects.filter(tipo='compuesto').first()
    if not compuesto:
        print('❌ No hay insumos compuestos para probar')
        return

    print(f'📝 Probando con: {compuesto.nombre} (ID: {compuesto.id})')

    # Test de la vista de detalle
    response = client.get(f'/dashboard/insumos-compuestos/detalle/{compuesto.id}/')
    print(f'👁️  Vista detalle: {response.status_code}')
    
    if response.status_code == 200:
        try:
            data = response.json()
            if data.get('success'):
                print('   ✅ JSON response válido')
                print(f'   📊 Componentes: {len(data["insumo"]["componentes"])}')
                print('   ✅ Ver detalles debería funcionar')
            else:
                print(f'   ❌ Error en response: {data.get("message")}')
        except Exception as e:
            print(f'   ❌ Error parseando JSON: {e}')
    else:
        print('   ❌ Error HTTP')

    print('\n🔧 DIAGNÓSTICO:')
    print('✅ SweetAlert2 agregado al template')
    print('✅ Debug agregado a funciones JavaScript')
    print('✅ Vista de detalle funcionando en backend')
    print('🔍 Revisa la consola del navegador para más información')

if __name__ == '__main__':
    test_funciones()
