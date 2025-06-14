"""
Script simple para debuggear la validación de componentes.
Usa el servidor de Django y navegador manual.
"""

import django
import os
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant.settings')
django.setup()

from restaurant.models import InsumoBasico

def analizar_validacion_js():
    """Analiza el JavaScript de validación para encontrar el problema"""
    
    print("🔍 Analizando validación de componentes...")
    
    # Leer el archivo HTML
    html_file = r"c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\insumos_compuestos.html"
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraer la función de validación
    start_marker = "// Validar que todos los componentes estén completos"
    end_marker = "if (!componentesValidos) {"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        validation_code = content[start_idx:end_idx + len(end_marker)]
        print("📋 Código de validación encontrado:")
        print(validation_code)
        print("\n" + "="*50 + "\n")
    
    # Buscar problemas potenciales
    problems = []
    
    # 1. Verificar si la validación se ejecuta correctamente
    if "componentesValidos = false;" in content:
        problems.append("✅ La validación puede marcar componentes como inválidos")
    
    # 2. Verificar la lógica de validación
    if "!selectValue || !inputValue || inputNumber <= 0" in content:
        problems.append("✅ Condiciones de validación presentes")
    
    # 3. Verificar el mensaje de error
    if "Todos los componentes deben tener insumo y cantidad válida" in content:
        problems.append("✅ Mensaje de error encontrado")
    
    # 4. Buscar posibles problemas
    if "showToast('❌ Todos los componentes deben tener insumo y cantidad válida', 'error');" in content:
        # Verificar si hay un return después
        error_idx = content.find("showToast('❌ Todos los componentes deben tener insumo y cantidad válida', 'error');")
        if error_idx != -1:
            # Buscar las siguientes 200 caracteres
            next_code = content[error_idx:error_idx + 200]
            if "return;" in next_code:
                problems.append("✅ Hay return después del error")
            else:
                problems.append("❌ NO hay return después del error - POSIBLE PROBLEMA")
    
    print("🔍 Análisis de problemas:")
    for problem in problems:
        print(f"  {problem}")
    
    print("\n🔍 Verificando insumos básicos disponibles...")
    insumos = InsumoBasico.objects.all()
    print(f"📦 Insumos básicos en DB: {insumos.count()}")
    
    if insumos.count() > 0:
        print("📋 Primeros 5 insumos:")
        for insumo in insumos[:5]:
            print(f"  - {insumo.nombre} ({insumo.categoria}) - ${insumo.precio_unitario}/{insumo.unidad_medida.abreviatura}")
    else:
        print("❌ NO HAY INSUMOS BÁSICOS - Este podría ser el problema")
    
    # Buscar el problema específico
    print("\n🔍 Buscando el problema específico en el código...")
    
    # Extraer toda la función de envío del formulario
    form_start = content.find("document.getElementById('formCrearCompuesto').addEventListener('submit'")
    if form_start != -1:
        # Buscar el final de la función (buscar el siguiente event listener o final del script)
        form_end = content.find("});", form_start) + 3
        if form_end > form_start:
            form_code = content[form_start:form_end]
            
            # Buscar la estructura exacta de validación
            print("📋 Función completa de envío del formulario:")
            lines = form_code.split('\n')
            for i, line in enumerate(lines[:50]):  # Primeras 50 líneas
                if i < 10 or "validar" in line.lower() or "componentes" in line.lower():
                    print(f"{i+1:2d}: {line}")
    
    print("\n💡 Recomendaciones:")
    print("1. Verificar que hay insumos básicos en la base de datos")
    print("2. Verificar en el navegador que los selects se llenan correctamente")
    print("3. Verificar en consola del navegador los valores exactos de los componentes")
    print("4. Usar las herramientas de desarrollador para depurar el JavaScript paso a paso")

if __name__ == "__main__":
    analizar_validacion_js()
