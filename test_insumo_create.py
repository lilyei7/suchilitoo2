#!/usr/bin/env python
import os
import sys
import django
import json
from django.test import Client
from django.contrib.auth import get_user_model

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from restaurant.models import Insumo, CategoriaInsumo, UnidadMedida

def test_crear_insumo():
    print("\n=== TEST DE CREACIÓN DE INSUMO ===")
    
    # 1. Verificar que existan categorías y unidades de medida
    categorias = CategoriaInsumo.objects.all()
    if not categorias.exists():
        print("ERROR: No hay categorías en la base de datos")
        return
    else:
        print(f"Hay {categorias.count()} categorías disponibles")
    
    unidades = UnidadMedida.objects.all()
    if not unidades.exists():
        print("ERROR: No hay unidades de medida en la base de datos")
        return
    else:
        print(f"Hay {unidades.count()} unidades de medida disponibles")
    
    # 2. Iniciar el cliente y autenticarse
    client = Client()
    User = get_user_model()
    
    try:
        # Intentar obtener un usuario administrador
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            print("ADVERTENCIA: No se encontró un usuario administrador, intentando con cualquier usuario...")
            user = User.objects.filter(is_active=True).first()
            
        if not user:
            print("ERROR: No hay usuarios disponibles para probar")
            return
            
        print(f"Usando el usuario: {user.username}")
        client.force_login(user)
    except Exception as e:
        print(f"ERROR al autenticar: {e}")
        return
    
    # 3. Obtener datos del formulario (categorías y unidades)
    try:
        response = client.get('/dashboard/insumos/form-data/')
        if response.status_code != 200:
            print(f"ERROR obteniendo datos del formulario: {response.status_code}")
            return
            
        form_data = json.loads(response.content)
        print(f"Datos del formulario obtenidos correctamente: {len(form_data.get('categorias', []))} categorías, {len(form_data.get('unidades', []))} unidades")
    except Exception as e:
        print(f"ERROR al obtener datos del formulario: {e}")
        return
    
    # 4. Crear un nuevo insumo
    try:
        # Generar datos de prueba
        categoria = form_data['categorias'][0]['id']
        unidad = form_data['unidades'][0]['id']
        
        # Contador para probar varios nombres
        counter = 1
        while Insumo.objects.filter(codigo=f"TEST{counter:03d}").exists():
            counter += 1
        
        test_data = {
            'codigo': f"TEST{counter:03d}",
            'nombre': f"Insumo Test {counter}",
            'categoria': categoria,
            'unidad_medida': unidad,
            'tipo': 'basico',
            'precio_unitario': '100',
            'stock_actual': '10',
            'stock_minimo': '5',
        }
        
        print(f"Intentando crear insumo con datos: {test_data}")
        
        # Enviar solicitud POST para crear insumo
        response = client.post('/dashboard/insumos/crear/', test_data)
        
        # Verificar respuesta
        if response.status_code != 200:
            print(f"ERROR: La solicitud falló con código {response.status_code}")
            print(response.content.decode())
            return
            
        result = json.loads(response.content)
        
        if result.get('success'):
            print(f"ÉXITO: {result.get('message')}")
            
            # Verificar si el insumo está en la base de datos
            insumo = Insumo.objects.filter(codigo=test_data['codigo']).first()
            if insumo:
                print(f"Insumo creado correctamente en la base de datos con ID: {insumo.id}")
            else:
                print("ERROR: El insumo no existe en la base de datos a pesar de la respuesta exitosa")
        else:
            print(f"ERROR: {result.get('error')}")
    except Exception as e:
        print(f"ERROR durante la creación del insumo: {e}")

if __name__ == "__main__":
    test_crear_insumo()
