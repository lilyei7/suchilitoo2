import os
import re

# Path to the file to fix
file_path = os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html')

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Create a global variable to store product ID 
content = re.sub(
    r'(console\.log\(\'✅ \[MODAL\] Modal de eliminación encontrado\'\);)',
    r'\1\n            \n            // Variable global para almacenar el ID del producto actual\n            let productoIdGlobal = null;',
    content
)

# Fix 2: Update the event handler to store the value in the global variable
content = re.sub(
    r'(const productoId = button\.getAttribute\(\'data-id\'\);)',
    r'\1\n                productoIdGlobal = productoId;',
    content
)

# Fix 3: Replace productoId with productoIdGlobal in all places EXCEPT where it's defined
# First get all the lines with the definition
definition_lines = [
    "const productoId = button.getAttribute('data-id');",
    "productoIdGlobal = productoId;"
]

# Replace all occurrences OUTSIDE of the definition context
lines = content.split('\n')
for i in range(len(lines)):
    if 'productoId' in lines[i] and lines[i].strip() not in definition_lines:
        lines[i] = lines[i].replace('productoId', 'productoIdGlobal')

content = '\n'.join(lines)

# Fix 4: Fix specific occurrences that we know are problematic
content = re.sub(
    r'console\.log\(`📥 \[AJAX\] Respuesta recibida para producto \${productoIdGlobal} \(\${productoNombre}\)`\);',
    r'console.log(`📥 [AJAX] Respuesta recibida para producto ${productoIdGlobal} (${productoNombre})`);',
    content
)

# Fix 5: Replace references to fetch API URLs
content = re.sub(
    r'fetch\(`/dashboard/api/verificar-producto/\${productoIdGlobal}/`',
    r'fetch(`/dashboard/api/verificar-producto/${productoIdGlobal}/`',
    content
)

# Write the fixed content back to the file
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed variable reference errors in {file_path}")
