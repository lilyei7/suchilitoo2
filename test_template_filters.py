#!/usr/bin/env python
"""
Test script para verificar que los template filters funcionen correctamente
"""
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.template import Template, Context
from django.contrib.auth import get_user_model
from accounts.models import Rol

User = get_user_model()

def test_template_filters():
    print("=== Test de Template Filters ===")
    
    # Usar un usuario existente o el primer usuario superuser
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.first()
    
    if not user:
        print("❌ No hay usuarios en la base de datos")
        return False
    
    print(f"Usuario de prueba: {user.username}")
    if user.rol:
        print(f"Rol: {user.rol.nombre}")
    else:
        print("Sin rol asignado")
    
    # Test template con filtros
    template_content = '''
{% load permission_tags %}
Usuario: {{ user.username }}
Rol: {% if user.rol %}{{ user.rol.nombre }}{% else %}Sin rol{% endif %}

Permisos:
- has_feature('ver_costos'): {{ user|has_feature:'ver_costos' }}
- has_feature('ver_datos_sensibles'): {{ user|has_feature:'ver_datos_sensibles' }}
- can_create('usuarios'): {{ user|can_create:'usuarios' }}
- can_update('inventario'): {{ user|can_update:'inventario' }}
- has_module_access('inventario'): {{ user|has_module_access:'inventario' }}
    '''
    
    try:
        template = Template(template_content)
        context = Context({'user': user})
        result = template.render(context)
        print("\n=== Resultado del template ===")
        print(result)
        print("✅ Template filters funcionan correctamente")
        
    except Exception as e:
        print(f"❌ Error al renderizar template: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = test_template_filters()
    sys.exit(0 if success else 1)
