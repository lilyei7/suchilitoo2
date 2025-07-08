import os
import re

# Path to the file to check
file_path = os.path.join('dashboard', 'templates', 'dashboard', 'productos_venta', 'lista.html')

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check for all variable declarations
declarations = re.findall(r'(?:const|let|var)\s+(\w+)\s*=', content)
declaration_counts = {}

for var in declarations:
    if var not in declaration_counts:
        declaration_counts[var] = 0
    declaration_counts[var] += 1

# Print variables declared more than once
print("Variables declared multiple times:")
for var, count in declaration_counts.items():
    if count > 1:
        print(f"- {var}: {count} times")
        # Show line numbers where these are declared
        line_num = 1
        for line in content.split('\n'):
            if re.search(rf'(?:const|let|var)\s+{var}\s*=', line):
                print(f"  Line {line_num}: {line.strip()}")
            line_num += 1

print("\nVerification complete!")
