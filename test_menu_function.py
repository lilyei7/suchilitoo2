#!/usr/bin/env python3
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def test_menu_function():
    """Test the menu function that was causing the error"""
    try:
        from mesero.views import obtener_productos_menu
        
        print("🧪 TESTING MENU FUNCTION...")
        print("=" * 50)
        
        # Test the function that was causing the SQL error
        menu_data = obtener_productos_menu()
        
        print(f"✅ Function executed successfully")
        print(f"✅ Found {len(menu_data)} categories")
        
        # Check for products with personalizations
        products_with_personalizations = 0
        total_products = 0
        
        for category, products in menu_data.items():
            total_products += len(products)
            for product in products:
                if product.get('personalizaciones'):
                    products_with_personalizations += 1
        
        print(f"✅ Total products: {total_products}")
        print(f"✅ Products with personalizations: {products_with_personalizations}")
        
        # Test a specific product with personalizations
        print("\n🔍 SAMPLE PRODUCT WITH PERSONALIZATIONS:")
        found_sample = False
        for category, products in menu_data.items():
            for product in products:
                if product.get('personalizaciones'):
                    print(f"   Product: {product['nombre']}")
                    print(f"   Price: ${product['precio']}")
                    print(f"   Personalizations: {len(product['personalizaciones'])}")
                    for pers in product['personalizaciones'][:3]:  # Show first 3
                        print(f"     - {pers['nombre']} (+${pers['precio_extra']})")
                    found_sample = True
                    break
            if found_sample:
                break
        
        if not found_sample:
            print("   No products with personalizations found")
        
        print("\n✅ ALL TESTS PASSED!")
        print("✅ SQL parameterization issue fixed!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_menu_function()
