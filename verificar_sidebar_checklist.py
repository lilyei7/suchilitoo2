import os
import sys
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suchilitoo.settings')
django.setup()

from dashboard.views.base_views import get_sidebar_context
from dashboard.views.checklist_views import (
    checklist_dashboard, manage_categories, manage_tasks, task_history
)

def test_sidebar_context():
    """
    Prueba que los contextos del sidebar se estén generando correctamente
    para todas las vistas de checklist.
    """
    print("Probando contextos del sidebar para las vistas de checklist...")
    
    # Valores esperados para cada vista
    expected_values = {
        'checklist_dashboard': {
            'sidebar_active': 'checklist_dashboard',
            'checklist_section_active': True
        },
        'manage_categories': {
            'sidebar_active': 'checklist_categories',
            'checklist_section_active': True
        },
        'manage_tasks': {
            'sidebar_active': 'checklist_tasks',
            'checklist_section_active': True
        },
        'task_history': {
            'sidebar_active': 'checklist_history',
            'checklist_section_active': True
        }
    }
    
    # Probar cada vista
    test_failed = False
    for view_name, expected in expected_values.items():
        # Obtener el contexto generado por la vista
        context = get_sidebar_context(expected['sidebar_active'])
        
        # Verificar valores
        sidebar_active = context.get('sidebar_active')
        checklist_active = context.get('checklist_section_active')
        
        # Imprimir resultados
        print(f"\nProbando vista: {view_name}")
        print(f"  Esperado: sidebar_active='{expected['sidebar_active']}', checklist_section_active={expected['checklist_section_active']}")
        print(f"  Obtenido: sidebar_active='{sidebar_active}', checklist_section_active={checklist_active}")
        
        if sidebar_active != expected['sidebar_active'] or checklist_active != expected['checklist_section_active']:
            print("  ❌ PRUEBA FALLIDA")
            test_failed = True
        else:
            print("  ✅ PRUEBA EXITOSA")
    
    print("\nResultado de las pruebas:")
    if test_failed:
        print("❌ Algunas pruebas fallaron. Revisa los resultados.")
    else:
        print("✅ Todas las pruebas pasaron. La configuración del sidebar es correcta.")

    # Ahora verificar que la plantilla HTML pueda reconocer estas combinaciones
    print("\nVerificando condiciones en la plantilla HTML:")
    
    # Patrones que deben estar presentes en la plantilla base.html
    patterns = [
        "{% if sidebar_active == 'manage_categories' or sidebar_active == 'checklist_categories' %}active{% endif %}",
        "{% if sidebar_active == 'manage_tasks' or sidebar_active == 'checklist_tasks' %}active{% endif %}",
        "{% if sidebar_active == 'task_history' or sidebar_active == 'checklist_history' %}active{% endif %}"
    ]
    
    try:
        # Ruta al archivo de plantilla base.html
        template_path = "dashboard/templates/dashboard/base.html"
        
        with open(template_path, 'r', encoding='utf-8') as file:
            template_content = file.read()
        
        all_patterns_found = True
        for pattern in patterns:
            if pattern in template_content:
                print(f"  ✅ Patrón encontrado: {pattern}")
            else:
                print(f"  ❌ Patrón NO encontrado: {pattern}")
                all_patterns_found = False
        
        if all_patterns_found:
            print("\n✅ La plantilla contiene todas las condiciones necesarias.")
        else:
            print("\n❌ La plantilla no contiene todas las condiciones necesarias.")
    
    except FileNotFoundError:
        print(f"  ❌ No se pudo encontrar el archivo de plantilla: {template_path}")

if __name__ == "__main__":
    test_sidebar_context()
