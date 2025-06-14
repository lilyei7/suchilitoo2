#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from accounts.models import Usuario

def test_login_and_create_insumo():
    print("=== PRUEBA DE LOGIN Y CREACIÓN DE INSUMO ===")
    
    # Crear cliente de prueba
    client = Client()
    
    # Intentar login
    login_data = {
        'username': 'jhayco',
        'password': 'admin123'
    }
    
    response = client.post('/dashboard/login/', login_data)
    print(f"Response status login: {response.status_code}")
    print(f"Response redirect: {response.url if hasattr(response, 'url') else 'No redirect'}")
    
    # Verificar si el login fue exitoso
    if response.status_code == 302:  # Redirect significa login exitoso
        print("✅ Login exitoso")
        
        # Ahora probar la creación de insumo
        insumo_data = {
            'codigo': 'API001',
            'nombre': 'Insumo desde API',
            'categoria': '1',
            'unidad_medida': '1',
            'tipo': 'basico',
            'precio_unitario': '15.50',
            'stock_actual': '50',
            'stock_minimo': '10'
        }
        
        response = client.post('/dashboard/insumos/crear/', insumo_data)
        print(f"Response status crear insumo: {response.status_code}")
        
        if response.status_code == 200:
            try:
                import json
                data = json.loads(response.content)
                print(f"Response data: {data}")
            except:
                print(f"Response content: {response.content}")
        else:
            print(f"Error response: {response.content}")
    else:
        print("❌ Error en login")
        print(f"Content: {response.content}")

if __name__ == "__main__":
    test_login_and_create_insumo()
