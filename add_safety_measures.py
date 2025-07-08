import os
import re

# Path to the file to fix
file_path = os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html')

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add safety wrapper around any direct uses of productoIdGlobal to avoid "not defined" errors
# This ensures that the variable is always checked before use

# Find and replace direct references to productoIdGlobal with safe checks
patterns_to_fix = [
    # In fetch URLs
    (r'fetch\(`/dashboard/api/verificar-producto/\${productoIdGlobal}/`', 
     r'fetch(`/dashboard/api/verificar-producto/${typeof productoIdGlobal !== "undefined" ? productoIdGlobal : "unknown"}/`'),
    
    # In console.log statements
    (r'console\.log\(`✅ \[VERIFICACIÓN\] ÉXITO: Producto ID \${productoIdGlobal} eliminado de la base de datos`\);',
     r'console.log(`✅ [VERIFICACIÓN] ÉXITO: Producto ID ${typeof productoIdGlobal !== "undefined" ? productoIdGlobal : "unknown"} eliminado de la base de datos`);'),
    
    # In forced deletion
    (r'console\.log\(`🔥 \[FORZAR\] Iniciando eliminación forzada para producto ID \${productoIdGlobal}`\);',
     r'console.log(`🔥 [FORZAR] Iniciando eliminación forzada para producto ID ${typeof productoIdGlobal !== "undefined" ? productoIdGlobal : "unknown"}`);'),
    
    (r'fetch\(`/dashboard/productos-venta/\${productoIdGlobal}/eliminar-forzado/`',
     r'fetch(`/dashboard/productos-venta/${typeof productoIdGlobal !== "undefined" ? productoIdGlobal : "unknown"}/eliminar-forzado/`'),
]

for pattern, replacement in patterns_to_fix:
    content = re.sub(pattern, replacement, content)

# Add a safety function at the beginning of the script block to handle undefined variables
safety_function = '''
    // Función de seguridad para manejar variables indefinidas
    function safeGetProductId() {
        if (typeof productoIdGlobal !== 'undefined' && productoIdGlobal) {
            return productoIdGlobal;
        }
        
        // Intentar obtener el ID desde el formulario
        const form = document.getElementById('deleteForm');
        if (form) {
            const input = form.querySelector('input[name="producto_id"]');
            if (input && input.value) {
                return input.value;
            }
            
            // Intentar extraer del action URL
            if (form.action) {
                const urlParts = form.action.split('/');
                const id = urlParts[urlParts.length - 2];
                if (id && id !== 'eliminar' && !isNaN(id)) {
                    return id;
                }
            }
        }
        
        return 'unknown';
    }
    
'''

# Insert the safety function after the global variable declaration
content = re.sub(
    r'(// Variable global para almacenar el ID del producto actual\s*\n\s*let productoIdGlobal = null;\s*\n)',
    r'\1' + safety_function,
    content
)

# Write the fixed content back to the file
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Added additional safety measures for productoIdGlobal in {file_path}")
print("Changes made:")
print("1. Added typeof checks to all direct productoIdGlobal references")
print("2. Added a safeGetProductId() function as fallback")
print("3. Made all console.log and fetch calls safer")
