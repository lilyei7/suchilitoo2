import os
import re

# Path to the file to fix
file_path = os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html')

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all occurrences of let productoIdGlobal = null;
matches = list(re.finditer(r'let productoIdGlobal = null;', content))

# Keep only the first occurrence and remove the others
if len(matches) > 1:
    lines = content.split('\n')
    # Remove duplicate declarations (keep only the first one)
    declaration_lines = []
    
    for i, line in enumerate(lines):
        if 'let productoIdGlobal = null;' in line and i not in declaration_lines:
            declaration_lines.append(i)
    
    # Remove all declarations after the first one
    for i in sorted(declaration_lines[1:], reverse=True):
        lines.pop(i)
    
    # Remove duplicate assignments
    assignment_lines = []
    for i, line in enumerate(lines):
        if 'productoIdGlobal = productoId;' in line and i not in assignment_lines:
            assignment_lines.append(i)
    
    # Keep only the first assignment
    for i in sorted(assignment_lines[1:], reverse=True):
        lines.pop(i)
    
    content = '\n'.join(lines)

# Write the fixed content back to the file
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed variable declaration errors in {file_path}")
