#!/usr/bin/env python3
"""
Test simple para verificar que las unidades se pasan al template de inventario
"""

import os
import sys
import django
import requests
from requests.auth import HTTPBasicAuth

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from restaurant.models import UnidadMedida
from django.test import Client
from django.contrib.auth.models import User

def test_unidades_in_template():
    """Test que verifica que las unidades se pasan al template de inventario"""
    
    print("=== TEST: VERIFICAR UNIDADES EN TEMPLATE ===")
    
    try:
        # Verificar que existen unidades en la base de datos
        unidades = list(UnidadMedida.objects.all().values('id', 'nombre', 'abreviacion'))
        print(f"✅ Unidades en BD: {len(unidades)}")
        for unidad in unidades[:5]:  # Solo mostrar las primeras 5
            print(f"   - {unidad['nombre']} ({unidad['abreviacion']})")
        
        if not unidades:
            print("❌ No hay unidades en la base de datos")
            return False
        
        # Crear un cliente de prueba de Django
        client = Client()
        
        # Crear o obtener un usuario admin
        User = get_user_model()
        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            print("❌ Usuario admin no encontrado")
            return False
        
        # Hacer login
        login_success = client.login(username='admin', password='admin123')
        if not login_success:
            print("❌ No se pudo hacer login")
            return False
        
        print("✅ Login exitoso")
        
        # Obtener la página de inventario
        response = client.get('/dashboard/inventario/')
        
        if response.status_code != 200:
            print(f"❌ Error al cargar la página de inventario. Status: {response.status_code}")
            return False
        
        print("✅ Página de inventario cargada correctamente")
        
        # Verificar que el HTML contiene opciones de unidades
        html_content = response.content.decode('utf-8')
        
        # Buscar el dropdown de unidades en el modal de edición
        if 'id="editUnidadMedida"' in html_content:
            print("✅ Dropdown de unidades encontrado en el HTML")
        else:
            print("❌ Dropdown de unidades NO encontrado en el HTML")
            return False
        
        # Contar opciones de unidades en el HTML
        unidades_count = 0
        for unidad in unidades:
            if f'<option value="{unidad["id"]}">{unidad["nombre"]}</option>' in html_content:
                unidades_count += 1
                print(f"   ✅ Unidad '{unidad['nombre']}' encontrada en HTML")
            else:
                print(f"   ❌ Unidad '{unidad['nombre']}' NO encontrada en HTML")
        
        print(f"📊 Resumen: {unidades_count} de {len(unidades)} unidades encontradas en el HTML")
        
        if unidades_count > 0:
            print("✅ Al menos algunas unidades están presentes en el HTML")
            return True
        else:
            print("❌ Ninguna unidad encontrada en el HTML")
            return False
            
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_unidades_in_template()
    if success:
        print("\n🎉 TEST EXITOSO: Las unidades están presentes en el template")
    else:
        print("\n❌ TEST FALLIDO: Problema con las unidades en el template")
    
    sys.exit(0 if success else 1)
