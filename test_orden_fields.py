#!/usr/bin/env python3
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import Orden, Mesa
from accounts.models import Usuario
from django.utils import timezone

def test_orden_creation():
    """Test Orden creation with correct field names"""
    print("🧪 TESTING ORDEN CREATION...")
    print("=" * 50)
    
    try:
        # Test 1: Check Orden model fields
        print("1. Checking Orden model fields")
        orden_fields = [f.name for f in Orden._meta.fields]
        print(f"   Available fields: {orden_fields}")
        
        if 'observaciones' in orden_fields:
            print("   ✅ Field 'observaciones' exists")
        else:
            print("   ❌ Field 'observaciones' not found")
            
        if 'notas_cocina' in orden_fields:
            print("   ✅ Field 'notas_cocina' exists")
        else:
            print("   ❌ Field 'notas_cocina' not found")
            
        if 'notas' in orden_fields:
            print("   ❌ Field 'notas' exists (should not)")
        else:
            print("   ✅ Field 'notas' does not exist (correct)")
        
        # Test 2: Try creating an Orden with observaciones
        print("\n2. Testing Orden creation with observaciones")
        mesa = Mesa.objects.filter(activa=True).first()
        usuario = Usuario.objects.first()
        
        if mesa and usuario:
            # Test the creation that should work now
            orden_test = Orden(
                mesa=mesa,
                mesero=usuario,
                estado='pendiente',
                observaciones='Test notes'  # This should work
            )
            print("   ✅ Orden object created successfully with observaciones")
            
            # Test the old way that was causing the error
            try:
                orden_test_bad = Orden(
                    mesa=mesa,
                    mesero=usuario,
                    estado='pendiente',
                    notas='Test notes'  # This should fail
                )
                print("   ❌ ERROR: Orden created with 'notas' field (should have failed)")
            except TypeError as e:
                print(f"   ✅ Expected error with 'notas' field: {e}")
        else:
            print("   ⚠️  No mesa or usuario found for testing")
        
        print("\n" + "=" * 50)
        print("🎉 ORDEN FIELD VALIDATION COMPLETED!")
        
    except Exception as e:
        print(f"❌ Error testing orden creation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_orden_creation()
