#!/usr/bin/env python
import os
import sys

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suchilitoo2.settings')

try:
    import django
    django.setup()
    print("Django setup successful!")
    
    from mesero.models import OrdenItem
    print("OrdenItem model imported successfully!")
    
    # Check model fields
    print("OrdenItem fields:")
    for field in OrdenItem._meta.fields:
        print(f"  - {field.name}: {field.__class__.__name__}")
    
    # Check if subtotal field exists
    has_subtotal = any(field.name == 'subtotal' for field in OrdenItem._meta.fields)
    print(f"Has subtotal field: {has_subtotal}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
