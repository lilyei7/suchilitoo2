import os
import re

# Path to the file to fix
file_path = os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html')

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Fix error verification
# The main issue is in the catch block where "this.action" is used but "this" might not be defined
# We need to ensure the product ID comes from a properly defined variable
error_verification_pattern = r'const urlParts = this\.action\.split\(\'/\'\);\s*\n\s*const idProductoError = urlParts\[urlParts\.length - 2\];'
fixed_error_verification = """                    // Extraer ID del producto de forma segura
                    let idProductoError = 'unknown';
                    try {
                        if (this && this.action) {
                            const urlParts = this.action.split('/');
                            idProductoError = urlParts[urlParts.length - 2];
                        } else if (formData && formData.get('producto_id')) {
                            idProductoError = formData.get('producto_id');
                        } else if (productoIdGlobal) {
                            idProductoError = productoIdGlobal;
                        }
                    } catch (e) {
                        console.error('Error al extraer ID del producto:', e);
                    }"""

content = re.sub(error_verification_pattern, fixed_error_verification, content)

# Fix 2: Fix any references to "productoId" in the error verification
content = re.sub(
    r'fetch\(`/dashboard/api/verificar-producto/\${productoId}/`',
    r'fetch(`/dashboard/api/verificar-producto/${idProductoError}/`',
    content
)

# Fix 3: Fix the check for 'eliminar' in the idProductoError
content = re.sub(
    r'if \(idProductoError === \'eliminar\'\)',
    r'if (idProductoError === \'eliminar\' || idProductoError === \'unknown\')',
    content
)

# Write the fixed content back to the file
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed error verification in {file_path}")
