#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suchilitoo2.settings')
django.setup()

from django.db import connection
from mesero.models import OrdenItem

def check_ordenitem_table():
    """Check the actual database table structure for OrdenItem"""
    print("=== Checking OrdenItem Table Schema ===")
    
    with connection.cursor() as cursor:
        # Get table info
        cursor.execute("PRAGMA table_info(mesero_ordenitem)")
        columns = cursor.fetchall()
        
        print("Current table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]}) - NOT NULL: {bool(col[3])}")
        
        # Check if subtotal column exists
        subtotal_exists = any(col[1] == 'subtotal' for col in columns)
        print(f"\nSubtotal column exists: {subtotal_exists}")
        
        if subtotal_exists:
            subtotal_info = next((col for col in columns if col[1] == 'subtotal'), None)
            print(f"Subtotal column info: {subtotal_info}")
    
    print("\n=== Django Model Fields ===")
    print("OrdenItem model fields:")
    for field in OrdenItem._meta.fields:
        print(f"  - {field.name} ({field.__class__.__name__})")
    
    # Check if model has subtotal field
    model_has_subtotal = any(field.name == 'subtotal' for field in OrdenItem._meta.fields)
    print(f"\nModel has subtotal field: {model_has_subtotal}")

if __name__ == "__main__":
    check_ordenitem_table()
