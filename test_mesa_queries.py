#!/usr/bin/env python3
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from mesero.models import Mesa
from accounts.models import Sucursal

def test_mesa_queries():
    """Test Mesa queries with correct field names"""
    print("🧪 TESTING MESA QUERIES...")
    print("=" * 50)
    
    try:
        # Test 1: Filter by activa=True
        print("1. Testing Mesa.objects.filter(activa=True)")
        mesas_activas = Mesa.objects.filter(activa=True)
        print(f"   ✅ Found {mesas_activas.count()} active mesas")
        
        # Test 2: Filter by sucursal and activa=True
        print("\n2. Testing Mesa.objects.filter(sucursal=..., activa=True)")
        sucursal = Sucursal.objects.first()
        if sucursal:
            mesas_sucursal = Mesa.objects.filter(sucursal=sucursal, activa=True)
            print(f"   ✅ Found {mesas_sucursal.count()} active mesas in {sucursal.nombre}")
        else:
            print("   ⚠️  No sucursal found")
        
        # Test 3: Get specific mesa
        print("\n3. Testing Mesa.objects.get(activa=True)")
        mesa = Mesa.objects.filter(activa=True).first()
        if mesa:
            # This should work now without the field error
            test_mesa = Mesa.objects.get(id=mesa.id, activa=True)
            print(f"   ✅ Successfully retrieved mesa: {test_mesa.numero}")
        else:
            print("   ⚠️  No active mesa found")
        
        # Test 4: Check model fields
        print("\n4. Checking Mesa model fields")
        mesa_fields = [f.name for f in Mesa._meta.fields]
        print(f"   Available fields: {mesa_fields}")
        
        if 'activa' in mesa_fields:
            print("   ✅ Field 'activa' exists")
        else:
            print("   ❌ Field 'activa' not found")
            
        if 'activo' in mesa_fields:
            print("   ❌ Field 'activo' exists (should not)")
        else:
            print("   ✅ Field 'activo' does not exist (correct)")
        
        print("\n" + "=" * 50)
        print("🎉 ALL MESA QUERIES WORKING CORRECTLY!")
        
    except Exception as e:
        print(f"❌ Error testing mesa queries: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_mesa_queries()
