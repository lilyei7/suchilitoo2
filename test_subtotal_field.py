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

from mesero.models import OrdenItem, Orden, Mesa
from restaurant.models import ProductoVenta
from accounts.models import Sucursal
from django.contrib.auth import get_user_model

User = get_user_model()

def test_ordenitem_creation():
    """Test creating an OrdenItem to see if the subtotal field works"""
    print("=== Testing OrdenItem Creation ===")
    
    try:
        # Get required objects
        user = User.objects.first()
        if not user:
            print("ERROR: No user found")
            return
            
        sucursal = Sucursal.objects.first()
        if not sucursal:
            print("ERROR: No sucursal found")
            return
            
        mesa = Mesa.objects.first()
        if not mesa:
            print("ERROR: No mesa found")
            return
            
        producto = ProductoVenta.objects.first()
        if not producto:
            print("ERROR: No producto found")
            return
        
        print(f"Using user: {user}")
        print(f"Using sucursal: {sucursal}")
        print(f"Using mesa: {mesa}")
        print(f"Using producto: {producto}")
        
        # Create order
        orden = Orden.objects.create(
            mesa=mesa,
            mesero=user,
            observaciones="Test order for subtotal field"
        )
        print(f"Created order: {orden}")
        
        # Create OrdenItem
        orden_item = OrdenItem.objects.create(
            orden=orden,
            producto=producto,
            cantidad=2,
            precio_unitario=producto.precio
        )
        print(f"SUCCESS: Created OrdenItem: {orden_item}")
        print(f"OrdenItem subtotal: {orden_item.subtotal}")
        print(f"OrdenItem calcular_subtotal(): {orden_item.calcular_subtotal()}")
        
        # Clean up
        orden_item.delete()
        orden.delete()
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ordenitem_creation()
