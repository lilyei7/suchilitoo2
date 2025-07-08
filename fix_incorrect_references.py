import os
import re

# Path to the file to fix
file_path = os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html')

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the incorrect productoIdGlobalGlobal references
content = content.replace('productoIdGlobalGlobal', 'productoIdGlobal')

# Write the fixed content back to the file
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed incorrect variable references in {file_path}")
