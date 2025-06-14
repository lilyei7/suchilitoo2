"""
Script para corregir errores de JavaScript en inventario.html
"""
import os
import re

# Ruta al archivo de inventario
inventario_path = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\inventario.html'

# Crear copia de seguridad
backup_path = inventario_path + '.complete_fix_backup'
with open(inventario_path, 'r', encoding='utf-8') as file:
    original_content = file.read()
    
with open(backup_path, 'w', encoding='utf-8') as file:
    file.write(original_content)
    
print(f"✅ Archivo de respaldo creado: {backup_path}")

# Correcciones específicas a realizar:
corrections = [
    # 1. Fix modalUnidad event listener closure
    (r'modalUnidad\.addEventListener\(\'show\.bs\.modal\'\, function\(\) \{\s+cargarUnidades\(\);\s+\}\);\s+\}\);', 
     'modalUnidad.addEventListener(\'show.bs.modal\', function() {\n            cargarUnidades();\n        });\n    });\n'),
    
    # 2. Fix configurarFormularioUnidad fetch headers
    (r'headers: \{\s+\'X-CSRFToken\': formData\.get\(\'csrfmiddlewaretoken\'\)\s+\}\);', 
     'headers: {\n                    \'X-CSRFToken\': formData.get(\'csrfmiddlewaretoken\')\n                }\n            });'),
    
    # 3. Fix catch block in configurarFormularioUnidad
    (r'} catch \(error\) \{\s+mostrarNotificacionElegante\(.*?error\'\s+\);\s+\} finally', 
     '} catch (error) {\n            mostrarNotificacionElegante(\n                \'Error de Conexión\',\n                \'No se pudo conectar con el servidor. Inténtalo de nuevo.\',\n                \'error\'\n            );\n        } finally'),
    
    # 4. Fix actualizarSelectCategorias function missing brace
    (r'select\.appendChild\(option\);\s+\}(\s+\/\/ Función para actualizar)', 
     'select.appendChild(option);\n    }\n}\n\1'),
    
    # 5. Fix extra braces at the end of the file if needed
    (r'select\.appendChild\(option\);\s+\}\s+\}\s+\}\); \/\/ Closing for DOMContentLoaded', 
     'select.appendChild(option);\n    }\n}\n\n}); // Closing for DOMContentLoaded'),
]

# Aplicar las correcciones
content = original_content
for pattern, replacement in corrections:
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Verificar balances de llaves y paréntesis
open_braces = content.count('{')
close_braces = content.count('}')
open_parens = content.count('(')
close_parens = content.count(')')

print(f"Llaves: {open_braces} abiertas, {close_braces} cerradas. Diferencia: {open_braces - close_braces}")
print(f"Paréntesis: {open_parens} abiertos, {close_parens} cerrados. Diferencia: {open_parens - close_parens}")

# Si hay desbalance significativo, no guardar para evitar problemas mayores
if abs(open_braces - close_braces) > 5 or abs(open_parens - close_parens) > 5:
    print("❌ Diferencia excesiva en llaves o paréntesis. No se guardaron los cambios.")
else:
    # Guardar cambios
    with open(inventario_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print("✅ Correcciones aplicadas y guardadas.")

# Estrategia alternativa: Crear un nuevo archivo con las funciones críticas corregidas manualmente
critical_functions = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Verificar elementos críticos
    const elementos = {
        'nuevoInsumoModal': document.getElementById('nuevoInsumoModal'),
        'nuevoInsumoForm': document.getElementById('nuevoInsumoForm'),
        'nombre': document.getElementById('nombre'),
        'codigo': document.getElementById('codigo'),
        'categoria': document.getElementById('categoria'),
        'unidad_medida': document.getElementById('unidad_medida'),
        'tipo': document.getElementById('tipo'),
    };
    
    // Cargar datos iniciales para los selects
    cargarDatosFormulario();
    
    // Configurar modal de nuevo insumo
    if (elementos.nuevoInsumoModal) {
        const modal = new bootstrap.Modal(elementos.nuevoInsumoModal);
        
        // Event listener para detectar cuando el modal se abre
        elementos.nuevoInsumoModal.addEventListener('show.bs.modal', function() {
            // Cuando se abre el modal, cargar las categorías y unidades
            cargarDatosFormulario();
            
            // Mostrar notificación elegante después de un breve retraso
            setTimeout(() => {
                mostrarNotificacionElegante(
                    'Nuevo Insumo',
                    'Completa la información para crear un nuevo insumo básico en el sistema.',
                    'info'
                );
            }, 500);
        });
    }
    
    // Configurar formularios de gestión
    configurarFormularioCategoria();
    configurarFormularioUnidad();
    
    // Configurar event listeners para modales de gestión
    const modalCategoria = document.getElementById('nuevaCategoriaModal');
    const modalUnidad = document.getElementById('nuevaUnidadModal');
    
    if (modalCategoria) {
        modalCategoria.addEventListener('show.bs.modal', function() {
            cargarCategorias();
        });
    }
    
    if (modalUnidad) {
        modalUnidad.addEventListener('show.bs.modal', function() {
            cargarUnidades();
        });
    }
});

// Función para cargar categorías y unidades en los selects
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
            mostrarNotificacionElegante(
                'Error de Carga',
                'No se pudieron cargar las categorías y unidades. Recarga la página e intenta nuevamente.',
                'error'
            );
        });
}

// Función para abrir modal de nueva categoría
function abrirModalCategoria() {
    const modal = new bootstrap.Modal(document.getElementById('nuevaCategoriaModal'));
    modal.show();
}

// Función para abrir modal de nueva unidad
function abrirModalUnidad() {
    const modal = new bootstrap.Modal(document.getElementById('nuevaUnidadModal'));
    modal.show();
}
</script>
"""

# Guardar las funciones críticas en un archivo aparte para referencia
critical_path = os.path.join(os.path.dirname(inventario_path), 'critical_functions.html')
with open(critical_path, 'w', encoding='utf-8') as file:
    file.write(critical_functions)
print(f"✅ Funciones críticas guardadas en: {critical_path}")

print("\n✅ PROCESO COMPLETADO")
print("Para verificar los resultados, inicia el servidor Django y prueba la página de inventario.")
print("Si continúan los errores, puedes restaurar el archivo de respaldo o usar las funciones críticas como referencia.")
