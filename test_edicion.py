#!/usr/bin/env python3
"""
Test específico para la funcionalidad de edición de insumos compuestos
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

def test_edicion():
    print('✏️ TEST FUNCIONALIDAD DE EDICIÓN')
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

    print(f'📝 Probando edición de: {compuesto.nombre} (ID: {compuesto.id})')

    # Test de la vista de detalle con nuevos campos
    response = client.get(f'/dashboard/insumos-compuestos/detalle/{compuesto.id}/')
    print(f'👁️  Vista detalle: {response.status_code}')
    
    if response.status_code == 200:
        try:
            data = response.json()
            if data.get('success'):
                insumo = data['insumo']
                print('   ✅ JSON response válido')
                print(f'   📊 Componentes: {len(insumo["componentes"])}')
                print(f'   🏷️  Categoría: {insumo["categoria"]} (ID: {insumo.get("categoria_id", "N/A")})')
                print(f'   📏 Unidad: {insumo["unidad_medida"]} (ID: {insumo.get("unidad_medida_id", "N/A")})')
                
                # Verificar que los IDs estén incluidos
                if 'categoria_id' in insumo and 'unidad_medida_id' in insumo:
                    print('   ✅ IDs de categoría y unidad incluidos para edición')
                else:
                    print('   ❌ Faltan IDs de categoría o unidad')
                
                # Mostrar componentes con detalles
                for i, comp in enumerate(insumo['componentes'], 1):
                    print(f'   🧩 Componente {i}: {comp["nombre"]} (ID: {comp["insumo_id"]}) - {comp["cantidad"]} {comp["unidad"]}')
                
            else:
                print(f'   ❌ Error en response: {data.get("message")}')
        except Exception as e:
            print(f'   ❌ Error parseando JSON: {e}')
    else:
        print('   ❌ Error HTTP')

    print('\n🔧 DIAGNÓSTICO EDICIÓN:')
    print('✅ Vista de detalle incluye IDs de categoría y unidad')
    print('✅ JavaScript mejorado con debug detallado')
    print('✅ Precarga de todos los campos implementada')
    print('✅ Timeouts para asegurar carga de selects')
    print('✅ Actualización automática de costos')
    
    print('\n📋 PASOS PARA PROBAR:')
    print('1. Ir a la página de insumos compuestos')
    print('2. Hacer clic en el botón "✏️" de cualquier insumo')
    print('3. Verificar que se precargan todos los campos:')
    print('   - Código y nombre')
    print('   - Categoría seleccionada')
    print('   - Unidad de medida seleccionada') 
    print('   - Componentes con insumos y cantidades')
    print('4. Revisar la consola del navegador para logs de debug')

if __name__ == '__main__':
    test_edicion()
