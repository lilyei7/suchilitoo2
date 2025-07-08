import os
import re

# Path to the file to check
file_path = os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html')

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all references to productoId
productoId_refs = re.findall(r'productoId(?!\w)', content)
productoIdGlobal_refs = re.findall(r'productoIdGlobal(?!\w)', content)

print(f"Found {len(productoId_refs)} references to 'productoId'")
print(f"Found {len(productoIdGlobal_refs)} references to 'productoIdGlobal'")

# Find lines with productoId references
lines_with_productoId = []
for i, line in enumerate(content.split('\n')):
    if re.search(r'productoId(?!\w)', line):
        lines_with_productoId.append((i+1, line.strip()))

print("\nLines with 'productoId' references:")
for line_num, line in lines_with_productoId:
    print(f"Line {line_num}: {line}")

# Check for any remaining variable declaration issues
declarations = re.findall(r'(?:const|let|var)\s+productoId\s*=', content)
print(f"\nFound {len(declarations)} declarations of 'productoId'")

# Check for any incorrect uses of the global variable
incorrect_refs = []
for i, line in enumerate(content.split('\n')):
    # Look for lines that reference productoId outside of declaration/assignment contexts
    if ('productoId' in line and 
        not re.search(r'(?:const|let|var)\s+productoId\s*=', line) and 
        not 'button.getAttribute' in line and
        not 'producto_id_input' in line and 
        not 'productoIdGlobal' in line):
        incorrect_refs.append((i+1, line.strip()))

print("\nPotentially incorrect references to 'productoId':")
for line_num, line in incorrect_refs:
    print(f"Line {line_num}: {line}")

# Check for idProductoActual and idProductoError
idProducto_refs = re.findall(r'idProducto(?:Actual|Error|Form|Forzar)(?!\w)', content)
print(f"\nFound {len(idProducto_refs)} references to idProducto variants")

print("\nVerification complete!")
