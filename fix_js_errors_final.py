import os
import re

def fix_js_errors():
    """Fix specific JavaScript errors in inventario.html"""
    # Path to the file
    file_path = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\inventario.html'
    
    # Create backup
    backup_path = file_path + '.js_fix_backup'
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    print(f"✅ Backup created: {backup_path}")
    
    # Define critical functions that need to be fixed
    critical_functions = {
        'abrirModalCategoria': """
// Función para abrir modal de nueva categoría
function abrirModalCategoria() {
    const modal = new bootstrap.Modal(document.getElementById('nuevaCategoriaModal'));
    modal.show();
}
""",
        'abrirModalUnidad': """
// Función para abrir modal de nueva unidad
function abrirModalUnidad() {
    const modal = new bootstrap.Modal(document.getElementById('nuevaUnidadModal'));
    modal.show();
}
""",
        'cargarDatosFormulario': """
// Función para cargar datos del formulario
function cargarDatosFormulario() {
    const url = '{% url "dashboard:get_form_data" %}';
    
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Cargar categorías
            const categoriaSelect = document.getElementById('categoria');
            if (categoriaSelect) {
                categoriaSelect.innerHTML = '<option value="">Seleccionar categoría</option>';
                data.categorias.forEach(categoria => {
                    const option = document.createElement('option');
                    option.value = categoria.id;
                    option.textContent = categoria.nombre;
                    categoriaSelect.appendChild(option);
                });
            }
            
            // Cargar unidades de medida
            const unidadSelect = document.getElementById('unidad_medida');
            if (unidadSelect) {
                unidadSelect.innerHTML = '<option value="">Seleccionar unidad</option>';
                data.unidades.forEach(unidad => {
                    const option = document.createElement('option');
                    option.value = unidad.id;
                    option.textContent = `${unidad.nombre} (${unidad.abreviacion})`;
                    unidadSelect.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('Error cargando datos del formulario:', error);
            alert('Error al cargar categorías y unidades. Por favor, recarga la página.');
        });
}
"""
    }
    
    # Find the extra_js block position
    extra_js_match = re.search(r'{% block extra_js %}(.*?){% endblock %}', original_content, re.DOTALL)
    
    if extra_js_match:
        # Extract the block content
        block_content = extra_js_match.group(1)
        
        # Find the DOMContentLoaded event
        dom_content_match = re.search(r'document\.addEventListener\(\'DOMContentLoaded\', function\(\) \{(.*?)\}\);', block_content, re.DOTALL)
        
        if dom_content_match:
            dom_content = dom_content_match.group(1)
            
            # Add the critical functions right after the DOMContentLoaded callback
            new_block_content = block_content.replace(
                "});", # End of DOMContentLoaded
                "});\n\n// ===== CRITICAL FUNCTIONS INJECTED BY FIX SCRIPT =====\n" + 
                critical_functions['abrirModalCategoria'] + 
                critical_functions['abrirModalUnidad'] + 
                critical_functions['cargarDatosFormulario']
            )
            
            # Replace the block content
            new_content = original_content.replace(extra_js_match.group(0), "{% block extra_js %}" + new_block_content + "{% endblock %}")
            
            # Write the updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ Critical functions injected into the JavaScript block")
            return True
        else:
            print("❌ Could not find DOMContentLoaded event in the extra_js block")
    else:
        print("❌ Could not find the extra_js block in the template")
    
    return False

if __name__ == "__main__":
    if fix_js_errors():
        print("✅ JavaScript errors fixed successfully!")
        print("Restart your Django server and check the inventory page")
    else:
        print("❌ Failed to fix JavaScript errors")
        print("Try manually adding the missing functions to the template")
