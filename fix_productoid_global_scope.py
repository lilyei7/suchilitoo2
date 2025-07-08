import os
import re

# Path to the file to fix
file_path = os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html')

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find where the global variable is declared and move it to a more global scope
# First, remove the current declaration inside the modal block
content = re.sub(
    r'(\s+)// Variable global para almacenar el ID del producto actual\s*\n\s+let productoIdGlobal = null;\s*\n',
    r'',
    content
)

# Add the global variable declaration at the beginning of the DOMContentLoaded function
dom_content_loaded_pattern = r"(document\.addEventListener\('DOMContentLoaded', function\(\) \{)"
global_variable_declaration = r"""\1
    // Variable global para almacenar el ID del producto actual
    let productoIdGlobal = null;
"""

content = re.sub(dom_content_loaded_pattern, global_variable_declaration, content)

# Fix the error verification to be more robust and not rely on productoIdGlobal if it's not available
error_verification_pattern = r'} else if \(productoIdGlobal\) \{\s*\n\s*idProductoError = productoIdGlobal;\s*\n\s*}'
safe_error_verification = """} else if (typeof productoIdGlobal !== 'undefined' && productoIdGlobal) {
                            idProductoError = productoIdGlobal;
                        }"""

content = content.replace(error_verification_pattern, safe_error_verification)

# Add additional safety check before using productoIdGlobal in other places
content = re.sub(
    r'(\s+)else if \(formData && formData\.get\(\'producto_id\'\)\) \{',
    r'\1else if (typeof formData !== "undefined" && formData && formData.get && formData.get(\'producto_id\')) {',
    content
)

# Write the fixed content back to the file
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed productoIdGlobal scope and error verification in {file_path}")
print("Changes made:")
print("1. Moved productoIdGlobal declaration to global scope")
print("2. Added typeof checks before using productoIdGlobal")
print("3. Made error verification more robust")
