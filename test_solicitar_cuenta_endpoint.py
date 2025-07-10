#!/usr/bin/env python
import os
import sys
import django
import json
from django.test import Client
from django.contrib.auth.models import User

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def test_solicitar_cuenta_endpoint():
    """Prueba el endpoint de solicitar cuenta"""
    print("=== TEST SOLICITAR CUENTA ENDPOINT ===")
    
    # Importar modelos después de configurar Django
    from mesero.models import Orden, Mesa, NotificacionCuenta
    from restaurant.models import ProductoVenta
    
    # Crear cliente de prueba
    client = Client()
    
    # Crear o obtener un usuario de prueba
    try:
        user = User.objects.get(username='testuser')
        print(f"✓ Usuario existente: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        print(f"✓ Usuario creado: {user.username}")
    
    # Crear o obtener una mesa de prueba
    try:
        mesa = Mesa.objects.get(numero=1)
        print(f"✓ Mesa existente: {mesa.numero}")
    except Mesa.DoesNotExist:
        mesa = Mesa.objects.create(
            numero=1,
            capacidad=4,
            disponible=True
        )
        print(f"✓ Mesa creada: {mesa.numero}")
    
    # Crear o obtener una orden de prueba
    try:
        orden = Orden.objects.filter(mesero=user, estado='entregada').first()
        if not orden:
            # Crear una orden nueva
            orden = Orden.objects.create(
                mesa=mesa,
                mesero=user,
                estado='entregada',
                total=100.00
            )
        print(f"✓ Orden de prueba: {orden.id}")
    except Exception as e:
        print(f"✗ Error creando orden: {e}")
        return False
    
    # Hacer login
    login_success = client.login(username='testuser', password='testpass123')
    if not login_success:
        print("✗ Error al hacer login")
        return False
    print("✓ Login exitoso")
    
    # Probar el endpoint con petición AJAX
    print("\n--- Probando endpoint con AJAX ---")
    response = client.post(
        f'/mesero/solicitar-cuenta/{orden.id}/',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        content_type='application/json'
    )
    
    print(f"Status code: {response.status_code}")
    print(f"Content-Type: {response.get('Content-Type', 'No especificado')}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Respuesta JSON: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print("✓ Solicitud exitosa")
                
                # Verificar que se creó la notificación
                notificacion = NotificacionCuenta.objects.filter(orden=orden).first()
                if notificacion:
                    print(f"✓ Notificación creada: {notificacion.id}")
                else:
                    print("✗ No se creó la notificación")
                
                # Verificar que la orden se actualizó
                orden.refresh_from_db()
                if orden.cuenta_solicitada:
                    print("✓ Orden actualizada correctamente")
                else:
                    print("✗ La orden no se actualizó")
                
                return True
            else:
                print(f"✗ Solicitud falló: {data.get('message', 'Sin mensaje')}")
                return False
                
        except json.JSONDecodeError as e:
            print(f"✗ Error decodificando JSON: {e}")
            print(f"Contenido raw: {response.content}")
            return False
    else:
        print(f"✗ Error HTTP: {response.status_code}")
        print(f"Contenido: {response.content}")
        return False

if __name__ == '__main__':
    try:
        success = test_solicitar_cuenta_endpoint()
        if success:
            print("\n🎉 TEST EXITOSO - El endpoint funciona correctamente")
        else:
            print("\n❌ TEST FALLIDO - El endpoint tiene problemas")
    except Exception as e:
        print(f"\n💥 ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
