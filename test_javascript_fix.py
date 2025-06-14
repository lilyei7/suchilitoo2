#!/usr/bin/env python3
"""
Test para verificar que el error de JavaScript se resolvió
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_javascript_fix():
    """Test para verificar que no hay errores de JavaScript en el template"""
    
    print("=== TEST: VERIFICAR CORRECCION DE ERROR JAVASCRIPT ===")
    
    try:
        # Crear cliente Django
        client = Client()
        
        # Hacer login
        User = get_user_model()
        user = User.objects.get(username='admin')
        login_success = client.login(username='admin', password='admin123')
        
        if not login_success:
            print("❌ Login fallido")
            return False
        
        print("✅ Login exitoso")
        
        # Obtener la página de inventario
        response = client.get('/dashboard/inventario/')
        
        if response.status_code != 200:
            print(f"❌ Error al cargar página de inventario. Status: {response.status_code}")
            return False
        
        html_content = response.content.decode('utf-8')
        print("✅ Página de inventario cargada")
        
        # Verificar que ya no existen declaraciones 'const' duplicadas
        const_declarations = html_content.count('const optionCategoria')
        if const_declarations > 0:
            print(f"❌ Aún hay {const_declarations} declaraciones 'const optionCategoria'")
            return False
        
        const_unidad_declarations = html_content.count('const optionUnidad')
        if const_unidad_declarations > 0:
            print(f"❌ Aún hay {const_unidad_declarations} declaraciones 'const optionUnidad'")
            return False
        
        print("✅ No hay declaraciones 'const' duplicadas")
        
        # Verificar que existen las declaraciones 'let' correctas
        let_categoria_declarations = html_content.count('let optionCategoria;')
        let_unidad_declarations = html_content.count('let optionUnidad;')
        
        if let_categoria_declarations == 1:
            print("✅ Declaración 'let optionCategoria;' encontrada correctamente")
        else:
            print(f"❌ Declaraciones 'let optionCategoria;' encontradas: {let_categoria_declarations} (esperado: 1)")
            return False
        
        if let_unidad_declarations == 1:
            print("✅ Declaración 'let optionUnidad;' encontrada correctamente")
        else:
            print(f"❌ Declaraciones 'let optionUnidad;' encontradas: {let_unidad_declarations} (esperado: 1)")
            return False
        
        # Verificar que la función cargarCategoriasYUnidades existe
        if 'function cargarCategoriasYUnidades()' in html_content:
            print("✅ Función cargarCategoriasYUnidades presente")
        else:
            print("❌ Función cargarCategoriasYUnidades no encontrada")
            return False
        
        # Verificar que se llama la función
        if 'cargarCategoriasYUnidades()' in html_content:
            print("✅ Llamada a cargarCategoriasYUnidades presente")
        else:
            print("❌ Llamada a cargarCategoriasYUnidades no encontrada")
            return False
        
        print("\n🎉 TODAS LAS VERIFICACIONES PASARON:")
        print("   ✅ No hay declaraciones const duplicadas")
        print("   ✅ Declaraciones let correctas")
        print("   ✅ Función JavaScript presente")
        print("   ✅ Llamada a función presente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    from django.contrib.auth import get_user_model
    
    success = test_javascript_fix()
    if success:
        print("\n🎉 CORRECCIÓN EXITOSA")
        print("✅ El error de JavaScript 'Identifier already declared' ha sido resuelto")
        print("✅ Ahora el botón de editar debería funcionar correctamente")
    else:
        print("\n❌ CORRECCIÓN FALLIDA")
        print("❌ Aún hay problemas con el JavaScript")
    
    sys.exit(0 if success else 1)
