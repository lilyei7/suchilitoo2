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
from mesero.models import OrdenItem, Orden, Mesa
from restaurant.models import ProductoVenta
from accounts.models import Sucursal
from django.contrib.auth import get_user_model

User = get_user_model()

def test_ordenitem_creation():
    """Test creating an OrdenItem to reproduce the error"""
    print("=== Testing OrdenItem Creation ===")
    
    try:
        # Get or create required objects
        sucursal = Sucursal.objects.first()
        if not sucursal:
            print("No sucursal found, creating one...")
            sucursal = Sucursal.objects.create(
                nombre="Test Sucursal",
                direccion="Test Address",
                telefono="123456789"
            )
        
        # Create a mesa
        mesa = Mesa.objects.filter(activa=True).first()
        if not mesa:
            print("No mesa found, creating one...")
            mesa = Mesa.objects.create(
                numero="TEST-1",
                capacidad=4,
                sucursal=sucursal,
                activa=True
            )
        
        # Get a user
        user = User.objects.first()
        if not user:
            print("No user found, creating one...")
            user = User.objects.create_user(
                username="testuser",
                email="test@test.com",
                password="testpass123"
            )
        
        # Create an order
        orden = Orden.objects.create(
            mesa=mesa,
            mesero=user,
            observaciones="Test order"
        )
        print(f"Created order: {orden}")
        
        # Get a product
        producto = ProductoVenta.objects.first()
        if not producto:
            print("No product found, cannot continue test")
            return
        
        print(f"Using product: {producto}")
        
        # Try to create OrdenItem
        print("Creating OrdenItem...")
        orden_item = OrdenItem.objects.create(
            orden=orden,
            producto=producto,
            cantidad=1,
            precio_unitario=producto.precio
        )
        print(f"SUCCESS: Created OrdenItem: {orden_item}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        print(f"Error type: {type(e)}")
        
        # If it's a database error, let's check the table structure
        if "NOT NULL constraint failed" in str(e):
            print("\n=== Checking Database Table Structure ===")
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA table_info(mesero_ordenitem)")
                columns = cursor.fetchall()
                
                print("Database table columns:")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]}) - NOT NULL: {bool(col[3])}")
                
                # Check if subtotal column exists and is NOT NULL
                subtotal_col = next((col for col in columns if col[1] == 'subtotal'), None)
                if subtotal_col:
                    print(f"\nSubtotal column found: {subtotal_col}")
                    print(f"NOT NULL constraint: {bool(subtotal_col[3])}")
                else:
                    print("\nNo subtotal column found in database")
            
            print("\n=== Checking Django Model Fields ===")
            print("OrdenItem model fields:")
            for field in OrdenItem._meta.fields:
                print(f"  - {field.name} ({field.__class__.__name__})")

if __name__ == "__main__":
    test_ordenitem_creation()
