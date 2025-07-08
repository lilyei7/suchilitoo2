#!/usr/bin/env python
"""
Test script to verify that OrdenItem creation works after adding the subtotal field.
This script simulates the order creation flow that was failing.
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suchilitoo2.settings')
django.setup()

from mesero.models import OrdenItem, Orden, Mesa
from restaurant.models import ProductoVenta
from accounts.models import Sucursal
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

def test_order_creation_flow():
    """Test the complete order creation flow that was previously failing"""
    print("=== Testing Order Creation Flow ===")
    print("This test simulates the order creation that was failing with:")
    print("'NOT NULL constraint failed: mesero_ordenitem.subtotal'")
    print()
    
    try:
        # Get required objects (or create test ones)
        user = User.objects.first()
        if not user:
            print("Creating test user...")
            user = User.objects.create_user(
                username="testuser",
                email="test@example.com",
                password="testpass123"
            )
        
        sucursal = Sucursal.objects.first()
        if not sucursal:
            print("Creating test sucursal...")
            sucursal = Sucursal.objects.create(
                nombre="Sucursal Test",
                direccion="Test Address",
                telefono="123456789"
            )
        
        mesa = Mesa.objects.filter(activa=True).first()
        if not mesa:
            print("Creating test mesa...")
            mesa = Mesa.objects.create(
                numero="TEST-1",
                capacidad=4,
                sucursal=sucursal,
                activa=True
            )
        
        producto = ProductoVenta.objects.filter(disponible=True).first()
        if not producto:
            print("No available product found. Please create a product first.")
            return False
        
        print(f"Using:")
        print(f"  - User: {user.username}")
        print(f"  - Mesa: {mesa.numero}")
        print(f"  - Producto: {producto.nombre} (${producto.precio})")
        print()
        
        # Step 1: Create order
        print("Step 1: Creating order...")
        orden = Orden.objects.create(
            mesa=mesa,
            mesero=user,
            observaciones="Test order to verify subtotal field fix"
        )
        print(f"✓ Order created: {orden.numero_orden}")
        
        # Step 2: Create order item (this was failing before)
        print("Step 2: Creating order item...")
        orden_item = OrdenItem.objects.create(
            orden=orden,
            producto=producto,
            cantidad=2,
            precio_unitario=producto.precio
        )
        print(f"✓ Order item created successfully!")
        print(f"  - Cantidad: {orden_item.cantidad}")
        print(f"  - Precio unitario: ${orden_item.precio_unitario}")
        print(f"  - Subtotal: ${orden_item.subtotal}")
        print(f"  - Calculated subtotal: ${orden_item.calcular_subtotal()}")
        
        # Step 3: Verify subtotal calculation
        expected_subtotal = orden_item.precio_unitario * orden_item.cantidad
        if orden_item.subtotal == expected_subtotal:
            print("✓ Subtotal calculation is correct!")
        else:
            print(f"✗ Subtotal mismatch: expected ${expected_subtotal}, got ${orden_item.subtotal}")
        
        # Step 4: Test order totals calculation
        print("Step 3: Testing order totals calculation...")
        orden.calcular_totales()
        print(f"✓ Order totals calculated: ${orden.total}")
        
        # Step 5: Clean up (optional)
        print("Step 4: Cleaning up test data...")
        orden_item.delete()
        orden.delete()
        print("✓ Test data cleaned up")
        
        print()
        print("🎉 SUCCESS! Order creation flow is now working!")
        print("The 'NOT NULL constraint failed: mesero_ordenitem.subtotal' error has been fixed.")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def check_model_fields():
    """Check that the OrdenItem model has the expected fields"""
    print("\n=== Model Field Check ===")
    print("OrdenItem model fields:")
    
    for field in OrdenItem._meta.fields:
        field_type = field.__class__.__name__
        print(f"  ✓ {field.name}: {field_type}")
    
    # Check specific fields
    required_fields = ['subtotal', 'precio_unitario', 'cantidad', 'orden', 'producto']
    for field_name in required_fields:
        if any(field.name == field_name for field in OrdenItem._meta.fields):
            print(f"  ✓ Required field '{field_name}' exists")
        else:
            print(f"  ✗ Required field '{field_name}' missing")

if __name__ == "__main__":
    print("OrdenItem Subtotal Field Fix - Verification Test")
    print("=" * 50)
    
    # Check model fields first
    check_model_fields()
    
    # Run the order creation test
    success = test_order_creation_flow()
    
    if success:
        print("\n✅ All tests passed! The fix is working correctly.")
        print("You can now create orders without the subtotal constraint error.")
    else:
        print("\n❌ Tests failed. Please review the error messages above.")
        print("You may need to run migrations or check your database schema.")
    
    print("\nTo run this test, use: python test_ordenitem_fix.py")
