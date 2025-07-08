import os
import re

# Path to the file to fix
file_path = os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html')

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# First fix: The variable productoId is declared inside the modal event but used outside
# Strategy: Create a global variable to store it outside the event context
fix1 = re.sub(
    r'(console\.log\(\'✅ \[MODAL\] Modal de eliminación encontrado\'\);)',
    r'\1\n            \n            // Variable global para almacenar el ID del producto actual\n            let productoIdGlobal = null;',
    content
)

# Second fix: Update the event handler to store the value in the global variable
fix2 = re.sub(
    r'(const productoId = button\.getAttribute\(\'data-id\'\);)',
    r'\1\n                productoIdGlobal = productoId;',
    fix1
)

# Third fix: In the deleteForm submit handler, reference the global variable
fix3 = re.sub(
    r'(console\.log\(`📥 \[AJAX\] Respuesta recibida para producto \${productoId)( \}\(.*?\)\)`)',
    r'console.log(`📥 [AJAX] Respuesta recibida para producto ${productoIdGlobal}$2)',
    fix2
)

# Fourth fix: Find any other place where productoId is used incorrectly
fix4 = re.sub(
    r'(console\.log\(`🔥 \[FORZAR\] Iniciando eliminación forzada para producto ID \${)productoId(\}`\);)',
    r'\1productoIdGlobal\2',
    fix3
)

# Fifth fix: Update the fetch URL in the force delete handler
fix5 = re.sub(
    r'(fetch\(`/dashboard/productos-venta/\${)productoId(\}/eliminar-forzado/`)',
    r'\1productoIdGlobal\2',
    fix4
)

# Write the file back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(fix5)

print(f"Fixed variable reference errors in {file_path}")
