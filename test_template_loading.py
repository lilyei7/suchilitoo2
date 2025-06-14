#!/usr/bin/env python
"""
Script para probar la carga de templates directamente
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.template.loader import get_template, TemplateDoesNotExist

def test_template_loading():
    print("🔍 PROBANDO CARGA DE TEMPLATES")
    print("=" * 40)
    
    templates_to_test = [
        'dashboard/insumos_elaborados.html',
        'dashboard/modals/gestionar_categorias.html',
        'dashboard/modals/gestionar_unidades.html',
    ]
    
    for template_name in templates_to_test:
        try:
            template = get_template(template_name)
            print(f"✅ {template_name}")
            print(f"   📁 Origen: {template.origin.name}")
        except TemplateDoesNotExist as e:
            print(f"❌ {template_name}")
            print(f"   Error: {str(e)}")
        except Exception as e:
            print(f"⚠️  {template_name}")
            print(f"   Error: {str(e)}")
    
    # Probar renderizado manual de los includes
    print(f"\n🔧 PROBANDO RENDERIZADO MANUAL:")
    
    from django.template import Context, Template
    
    # Crear un template que incluye los modales
    test_template_content = """
    <div>Test Template</div>
    {% include 'dashboard/modals/gestionar_categorias.html' %}
    {% include 'dashboard/modals/gestionar_unidades.html' %}
    """
    
    try:
        template = Template(test_template_content)
        context = Context({})
        rendered = template.render(context)
        
        print(f"✅ Renderizado exitoso")
        print(f"📄 Tamaño: {len(rendered)} caracteres")
        
        # Verificar contenido
        if 'nuevaCategoriaModal' in rendered:
            print(f"✅ Modal categorías incluido")
        else:
            print(f"❌ Modal categorías NO incluido")
            
        if 'nuevaUnidadModal' in rendered:
            print(f"✅ Modal unidades incluido")
        else:
            print(f"❌ Modal unidades NO incluido")
            
    except Exception as e:
        print(f"❌ Error en renderizado manual: {str(e)}")

if __name__ == "__main__":
    test_template_loading()
