#!/usr/bin/env python
"""
Script para probar el login y acceso al menú del mesero
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client

def probar_login_mesero():
    """Probar el login completo del mesero y acceso al menú"""
    print("=" * 60)
    print("PRUEBA COMPLETA: LOGIN Y ACCESO AL MENÚ")
    print("=" * 60)
    
    client = Client()
    
    # 1. Probar página de login
    print("1. Probando página de login...")
    response = client.get('/mesero/login/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Página de login accesible")
    else:
        print("   ❌ Error en página de login")
        return
    
    # 2. Intentar login con credenciales
    print("\n2. Probando login con credenciales...")
    login_data = {
        'username': 'mesero_test',
        'password': '123456'
    }
    
    response = client.post('/mesero/login/', login_data, follow=True)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Login exitoso")
        
        # Verificar si fue redirigido al menú
        final_url = response.request['PATH_INFO']
        print(f"   URL final: {final_url}")
        
        if '/mesero/menu/' in final_url:
            print("   ✅ Redirigido correctamente al menú")
            
            # 3. Verificar contenido del menú
            print("\n3. Verificando contenido del menú...")
            content = response.content.decode('utf-8')
            
            # Buscar indicadores de que el menú tiene datos
            indicadores = [
                'productos-grid',
                'categoria-header',
                'producto-card',
                'Edamame',
                'Dragon Roll',
                'Gyozas'
            ]
            
            productos_encontrados = []
            for indicador in indicadores:
                if indicador in content:
                    productos_encontrados.append(indicador)
            
            print(f"   Indicadores encontrados: {len(productos_encontrados)}/{len(indicadores)}")
            
            if productos_encontrados:
                print("   ✅ El menú contiene productos reales")
                print(f"   Productos detectados: {productos_encontrados}")
            else:
                print("   ⚠️  No se detectaron productos en el HTML")
                
                # Buscar posibles problemas
                if 'Sin productos disponibles' in content:
                    print("   ❌ Mensaje: Sin productos disponibles")
                elif len(content) < 1000:
                    print("   ❌ Respuesta muy pequeña, posible error")
                else:
                    print("   ⚠️  Respuesta grande pero sin productos detectados")
                    
            print(f"   Tamaño total del HTML: {len(content)} caracteres")
            
        else:
            print(f"   ⚠️  No fue redirigido al menú (URL: {final_url})")
    else:
        print(f"   ❌ Error en login (Status: {response.status_code})")
    
    print("\n" + "=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)
    print("🌐 Para acceder manualmente:")
    print("   1. Abre: http://127.0.0.1:8000/mesero/login/")
    print("   2. Usuario: mesero_test")
    print("   3. Contraseña: 123456")
    print("   4. Deberías ver el menú con 13 productos en 5 categorías")
    print("\n📱 URLs útiles:")
    print("   - Login: http://127.0.0.1:8000/mesero/login/")
    print("   - Menú: http://127.0.0.1:8000/mesero/menu/ (después del login)")
    print("   - Dashboard: http://127.0.0.1:8000/dashboard/login/ (admin)")

if __name__ == '__main__':
    probar_login_mesero()
