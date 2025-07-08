#!/usr/bin/env python3
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import OrdenItem, Orden, Mesa
from restaurant.models import ProductoVenta
from accounts.models import Usuario
from decimal import Decimal

def test_ordenitem_creation():
    """Test OrdenItem creation with correct field names"""
    print("🧪 TESTING ORDENITEM CREATION...")
    print("=" * 50)
    
    try:
        # Test 1: Check OrdenItem model fields
        print("1. Checking OrdenItem model fields")
        ordenitem_fields = [f.name for f in OrdenItem._meta.fields]
        print(f"   Available fields: {ordenitem_fields}")
        
        required_fields = ['orden', 'producto', 'cantidad', 'precio_unitario', 'descuento_item', 'estado', 'observaciones']
        for field in required_fields:
            if field in ordenitem_fields:
                print(f"   ✅ Field '{field}' exists")
            else:
                print(f"   ❌ Field '{field}' not found")
        
        if 'subtotal' in ordenitem_fields:
            print("   ❌ Field 'subtotal' exists (should not)")
        else:
            print("   ✅ Field 'subtotal' does not exist (correct)")
        
        # Test 2: Check calcular_subtotal method
        print("\n2. Checking calcular_subtotal method")
        if hasattr(OrdenItem, 'calcular_subtotal'):
            print("   ✅ Method 'calcular_subtotal' exists")
        else:
            print("   ❌ Method 'calcular_subtotal' not found")
        
        # Test 3: Try creating an OrdenItem with correct fields
        print("\n3. Testing OrdenItem creation")
        producto = ProductoVenta.objects.filter(disponible=True).first()
        mesa = Mesa.objects.filter(activa=True).first()
        usuario = Usuario.objects.first()
        
        if producto and mesa and usuario:
            # Create a test orden first
            orden = Orden(
                mesa=mesa,
                mesero=usuario,
                estado='pendiente',
                observaciones='Test order'
            )
            print("   ✅ Orden object created successfully")
            
            # Test OrdenItem creation with correct fields
            ordenitem_test = OrdenItem(
                orden=orden,
                producto=producto,
                cantidad=2,
                precio_unitario=Decimal('25.50')  # This should work
            )
            print("   ✅ OrdenItem object created successfully with correct fields")
            
            # Test calcular_subtotal method
            subtotal = ordenitem_test.calcular_subtotal()
            expected_subtotal = Decimal('25.50') * 2
            if subtotal == expected_subtotal:
                print(f"   ✅ calcular_subtotal() works correctly: {subtotal}")
            else:
                print(f"   ❌ calcular_subtotal() returned unexpected value: {subtotal} (expected: {expected_subtotal})")
            
            # Test the old way that was causing the error
            try:
                ordenitem_test_bad = OrdenItem(
                    orden=orden,
                    producto=producto,
                    cantidad=2,
                    precio_unitario=Decimal('25.50'),
                    subtotal=Decimal('51.00')  # This should fail
                )
                print("   ❌ ERROR: OrdenItem created with 'subtotal' field (should have failed)")
            except TypeError as e:
                print(f"   ✅ Expected error with 'subtotal' field: {e}")
        else:
            print("   ⚠️  No producto, mesa, or usuario found for testing")
        
        print("\n" + "=" * 50)
        print("🎉 ORDENITEM FIELD VALIDATION COMPLETED!")
        
    except Exception as e:
        print(f"❌ Error testing ordenitem creation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_ordenitem_creation()
