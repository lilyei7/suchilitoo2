#!/usr/bin/env python
"""
Script para verificar si el usuario puede acceder al menú del mesero
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from restaurant.models import ProductoVenta, CategoriaProducto

User = get_user_model()

def verificar_acceso_menu():
    """Verificar si se puede acceder al menú del mesero"""
    print("=" * 60)
    print("VERIFICACIÓN DE ACCESO AL MENÚ DEL MESERO")
    print("=" * 60)
    
    # Crear un cliente de prueba
    client = Client()
    
    # 1. Verificar productos en la base de datos
    productos_count = ProductoVenta.objects.filter(disponible=True).count()
    print(f"1. Productos disponibles en DB: {productos_count}")
    
    # 2. Verificar usuarios disponibles
    usuarios = User.objects.all()
    print(f"2. Usuarios en el sistema: {usuarios.count()}")
    for usuario in usuarios:
        print(f"   - {usuario.username} (activo: {usuario.is_active})")
    
    # 3. Intentar acceder sin login
    print("\n3. Probando acceso sin login...")
    response = client.get('/mesero/menu/')
    print(f"   Status code: {response.status_code}")
    if response.status_code == 302:
        print(f"   Redirección a: {response.url}")
        print("   ✅ Correcto: Redirige al login porque requiere autenticación")
    
    # 4. Verificar si existe un usuario mesero
    try:
        # Buscar un usuario que pueda ser mesero
        usuario_mesero = None
        for user in usuarios:
            if 'mesero' in user.username.lower() or user.groups.filter(name__icontains='mesero').exists():
                usuario_mesero = user
                break
        
        if not usuario_mesero and usuarios.exists():
            # Usar el primer usuario disponible
            usuario_mesero = usuarios.first()
            
        if usuario_mesero:
            print(f"\n4. Probando login con usuario: {usuario_mesero.username}")
            # Intentar login (necesitamos la contraseña, pero podemos forzar el login)
            client.force_login(usuario_mesero)
            
            # Ahora intentar acceder al menú
            response = client.get('/mesero/menu/')
            print(f"   Status code después del login: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ ¡ÉXITO! El menú es accesible después del login")
                print(f"   Tamaño de respuesta: {len(response.content)} bytes")
                
                # Verificar si el contexto tiene datos
                if hasattr(response, 'context') and response.context:
                    productos_context = response.context.get('productos_por_categoria', {})
                    print(f"   Productos en contexto: {len(productos_context)} categorías")
                    for categoria, productos in productos_context.items():
                        print(f"     - {categoria}: {len(productos)} productos")
                else:
                    print("   ⚠️  No se pudo acceder al contexto de la respuesta")
            else:
                print(f"   ❌ Error: Status {response.status_code}")
        else:
            print("\n4. ❌ No se encontró ningún usuario para hacer login")
            
    except Exception as e:
        print(f"\n4. ❌ Error durante la prueba de login: {e}")
    
    print("\n" + "=" * 60)
    print("DIAGNÓSTICO:")
    print("=" * 60)
    
    if productos_count == 0:
        print("❌ PROBLEMA: No hay productos disponibles en la base de datos")
        print("   SOLUCIÓN: Ejecutar script para crear productos de ejemplo")
    elif usuarios.count() == 0:
        print("❌ PROBLEMA: No hay usuarios en el sistema")
        print("   SOLUCIÓN: Crear un usuario mesero")
    else:
        print("✅ Base de datos tiene productos y usuarios")
        print("💡 POSIBLES CAUSAS del problema:")
        print("   1. No estás logueado - ve a: http://127.0.0.1:8000/mesero/login/")
        print("   2. Error en el template - revisa la consola del navegador")
        print("   3. Error de JavaScript - abre Developer Tools (F12)")
        print("   4. Problema de CSS - los elementos están ocultos")
    
    print("\n🔧 PRÓXIMOS PASOS:")
    print("   1. Ve a: http://127.0.0.1:8000/mesero/login/")
    print("   2. Abre Developer Tools (F12) para ver errores")
    print("   3. Verifica la consola del servidor Django")

if __name__ == '__main__':
    verificar_acceso_menu()
