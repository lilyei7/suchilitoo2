#!/usr/bin/env python
"""
Script simple para probar la funcionalidad del formulario de proveedores
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from dashboard.models import Proveedor
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import Client
from django.urls import reverse
import json

User = get_user_model()

def create_test_user():
    """Crea un usuario de prueba"""
    try:
        # Eliminar usuario de prueba si existe
        User.objects.filter(username='test_supplier').delete()
        
        # Crear nuevo usuario de prueba
        user = User.objects.create(
            username='test_supplier',
            password=make_password('test123'),
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        return user
    except Exception as e:
        print(f"Error creando usuario: {e}")
        return None

def test_supplier_creation():
    """Prueba la creación de proveedores usando Django Test Client"""
    
    print("=== PROBANDO CREACIÓN DE PROVEEDORES ===\n")
    
    # Crear usuario de prueba
    user = create_test_user()
    if not user:
        print("❌ No se pudo crear usuario de prueba")
        return False
    
    print("✅ Usuario de prueba creado")
    
    # Crear cliente de Django
    client = Client()
    
    # Hacer login
    login_success = client.login(username='test_supplier', password='test123')
    if not login_success:
        print("❌ No se pudo hacer login")
        return False
    
    print("✅ Login exitoso")    # Datos de prueba
    test_data = {
        'nombre_comercial': 'Proveedor Test Django',
        'razon_social': 'Proveedor Test S.A. de C.V.',
        'rfc': 'XAXX010101000',  # RFC válido de ejemplo
        'persona_contacto': 'Juan Pérez Test',
        'telefono': '+52 55 1234-5678',
        'email': 'test@proveedor.com',
        'forma_pago_preferida': 'transferencia',
        'dias_credito': '30',
        'direccion': 'Av. Test 123',
        'ciudad_estado': 'Ciudad de México, CDMX',
        'categoria_productos': 'ingredientes',
        'notas_adicionales': 'Proveedor creado mediante test automatizado'
    }
    
    # Contar proveedores antes
    proveedores_antes = Proveedor.objects.count()
    print(f"Proveedores antes: {proveedores_antes}")
    
    # Enviar solicitud POST
    response = client.post(
        reverse('dashboard:crear_proveedor'),
        data=test_data,
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"Respuesta: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print("✅ API respondió exitosamente")
                
                # Verificar en base de datos
                proveedores_despues = Proveedor.objects.count()
                print(f"Proveedores después: {proveedores_despues}")
                
                if proveedores_despues > proveedores_antes:
                    print("✅ Proveedor creado exitosamente en la base de datos")
                    
                    # Verificar datos específicos
                    nuevo_proveedor = Proveedor.objects.filter(
                        nombre_comercial='Proveedor Test Django'
                    ).first()
                    
                    if nuevo_proveedor:
                        print("\n📋 Datos del proveedor creado:")
                        print(f"   - ID: {nuevo_proveedor.id}")
                        print(f"   - Nombre comercial: {nuevo_proveedor.nombre_comercial}")
                        print(f"   - Razón social: {nuevo_proveedor.razon_social}")
                        print(f"   - RFC: {nuevo_proveedor.rfc}")
                        print(f"   - Email: {nuevo_proveedor.email}")
                        print(f"   - Teléfono: {nuevo_proveedor.telefono}")
                        print(f"   - Estado: {nuevo_proveedor.estado}")
                        print(f"   - Forma de pago: {nuevo_proveedor.forma_pago_preferida}")
                        print(f"   - Días de crédito: {nuevo_proveedor.dias_credito}")
                        
                        # Limpiar - eliminar proveedor de prueba
                        nuevo_proveedor.delete()
                        print("\n🧹 Proveedor de prueba eliminado")
                        
                        # Limpiar usuario de prueba
                        user.delete()
                        print("🧹 Usuario de prueba eliminado")
                        
                        return True
                    else:
                        print("❌ No se pudo encontrar el proveedor creado")
                else:
                    print("❌ El proveedor no se creó en la base de datos")
            else:
                print(f"❌ API retornó error: {result.get('message', 'Error desconocido')}")
                if 'errors' in result:
                    print(f"   Errores específicos: {result['errors']}")
                    
        except json.JSONDecodeError as e:
            print(f"❌ Error al parsear respuesta JSON: {e}")
            print(f"   Respuesta cruda: {response.content.decode()[:500]}")
            
    else:
        print(f"❌ Error HTTP: {response.status_code}")
        print(f"   Respuesta: {response.content.decode()[:500]}")
    
    # Limpiar usuario de prueba
    try:
        user.delete()
    except:
        pass
        
    return False

def test_validations():
    """Prueba las validaciones del formulario"""
    
    print("\n=== PROBANDO VALIDACIONES ===\n")
    
    # Crear usuario de prueba
    user = create_test_user()
    if not user:
        print("❌ No se pudo crear usuario de prueba")
        return False
    
    client = Client()
    client.login(username='test_supplier', password='test123')
    
    success_count = 0
    
    # Prueba 1: Campo requerido vacío
    print("1. Probando campo requerido vacío...")
    response = client.post(
        reverse('dashboard:crear_proveedor'),
        data={'nombre_comercial': ''},  # Campo requerido vacío
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    if response.status_code == 200:
        result = response.json()
        if not result.get('success') and 'nombre_comercial' in result.get('errors', {}):
            print("✅ Validación de campo requerido funciona")
            success_count += 1
        else:
            print(f"❌ Validación de campo requerido falló: {result}")
    
    # Prueba 2: RFC inválido
    print("2. Probando RFC inválido...")
    response = client.post(
        reverse('dashboard:crear_proveedor'),
        data={
            'nombre_comercial': 'Test RFC',
            'rfc': 'INVALID_RFC'  # RFC inválido
        },
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    if response.status_code == 200:
        result = response.json()
        if not result.get('success') and 'rfc' in result.get('errors', {}):
            print("✅ Validación de RFC funciona")
            success_count += 1
        else:
            print(f"❌ Validación de RFC falló: {result}")
    
    # Prueba 3: Email inválido
    print("3. Probando email inválido...")
    response = client.post(
        reverse('dashboard:crear_proveedor'),
        data={
            'nombre_comercial': 'Test Email',
            'email': 'invalid-email'  # Email inválido
        },
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    if response.status_code == 200:
        result = response.json()
        if not result.get('success') and 'email' in result.get('errors', {}):
            print("✅ Validación de email funciona")
            success_count += 1
        else:
            print(f"❌ Validación de email falló: {result}")
    
    # Limpiar usuario de prueba
    try:
        user.delete()
    except:
        pass
    
    return success_count == 3

def check_database_model():
    """Verifica el modelo de base de datos"""
    
    print("=== VERIFICANDO MODELO DE BASE DE DATOS ===\n")
    
    try:
        # Verificar que el modelo existe y tiene los campos esperados
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(dashboard_proveedor);")
            columns = cursor.fetchall()
            
        field_names = [col[1] for col in columns]
        
        expected_fields = [
            'id', 'nombre_comercial', 'razon_social', 'rfc', 'persona_contacto',
            'telefono', 'email', 'forma_pago_preferida', 'dias_credito',
            'direccion', 'ciudad_estado', 'categoria_productos', 'notas_adicionales',
            'estado', 'fecha_registro'
        ]
        
        print("📋 Campos en la tabla:")
        for field in field_names:
            status = "✅" if field in expected_fields else "❓"
            print(f"   {status} {field}")
        
        missing_fields = [field for field in expected_fields if field not in field_names]
        if missing_fields:
            print(f"\n❌ Campos faltantes: {missing_fields}")
            return False
        else:
            print("\n✅ Todos los campos esperados están presentes")
            return True
            
    except Exception as e:
        print(f"❌ Error al verificar modelo: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE PROVEEDORES\n")
    
    # Ejecutar pruebas
    db_ok = check_database_model()
    creation_ok = test_supplier_creation()
    validation_ok = test_validations()
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS:")
    print("="*60)
    print(f"📊 Modelo de BD:     {'✅ OK' if db_ok else '❌ ERROR'}")
    print(f"🔗 Creación:         {'✅ OK' if creation_ok else '❌ ERROR'}")
    print(f"🛡️ Validaciones:     {'✅ OK' if validation_ok else '❌ ERROR'}")
    print("="*60)
    
    if all([db_ok, creation_ok, validation_ok]):
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está funcionando correctamente!")
        print("\n✨ Características verificadas:")
        print("   ✅ Modelo de base de datos completo")
        print("   ✅ Endpoint API funcional")
        print("   ✅ Validaciones del lado del servidor")
        print("   ✅ Respuestas JSON correctas")
        print("   ✅ Manejo de errores")
        print("   ✅ Creación exitosa de proveedores")
        
        print("\n🎯 El formulario de proveedores está listo para usar!")
        print("   - Inicie el servidor: python manage.py runserver")
        print("   - Abra http://127.0.0.1:8000/dashboard/proveedores/")
        print("   - Haga clic en 'Nuevo Proveedor'")
        print("   - Complete el formulario")
        print("   - El proveedor se creará automáticamente con AJAX")
        
    else:
        print("\n❌ Algunas pruebas fallaron. Revise los errores anteriores.")
