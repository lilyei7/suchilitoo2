import os
import re

# Path to the file to fix
file_path = os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html')

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: In the main verification call, use the current function scope's idProductoVerificacion
content = re.sub(
    r'fetch\(`/dashboard/api/verificar-producto/\${productoIdGlobal}/`',
    r'fetch(`/dashboard/api/verificar-producto/${idProductoVerificacion}/`',
    content
)

# Fix 2: Make sure we get the correct ID in verification messages
content = re.sub(
    r'console\.log\(`✅ \[VERIFICACIÓN\] ÉXITO: Producto ID \${productoIdGlobal} eliminado de la base de datos`\);',
    r'console.log(`✅ [VERIFICACIÓN] ÉXITO: Producto ID ${idProductoVerificacion} eliminado de la base de datos`);',
    content
)

# Fix 3: Make sure the idProductoVerificacion is properly defined before use
verification_function_start = re.search(r'function verificarProducto\(intento = 1, maxIntentos = 3\) {', content)
if verification_function_start:
    pos = verification_function_start.end()
    # Add a variable initialization at the start of the function
    content = content[:pos] + "\n                        // Get the ID for verification from a safe source\n                        const idProductoVerificacion = idProductoActual || productoIdGlobal || formData.get('producto_id') || 'unknown';" + content[pos:]

# Fix 4: Make sure the formData reference in the error handler is correctly using a backup variable
error_handler_formdata_pattern = r'else if \(formData && formData\.get\(\'producto_id\'\)\) {'
error_handler_formdata_replacement = r'else if (typeof formData !== "undefined" && formData && formData.get && formData.get(\'producto_id\')) {'
content = content.replace(error_handler_formdata_pattern, error_handler_formdata_replacement)

# Write the fixed content back to the file
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed verification process references in {file_path}")
