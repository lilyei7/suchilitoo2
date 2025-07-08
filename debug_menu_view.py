import os
import django
from django.template.loader import render_to_string
from django.template import Context, Template

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def test_menu_view():
    """Test the menu view and template rendering"""
    from restaurant.models import ProductoVenta
    
    print("\n=== Testing Menu View ===")
    
    # Check if ProductoVenta model exists
    print("\nChecking ProductoVenta model...")
    try:
        productos = ProductoVenta.objects.all()
        print(f"- Found {productos.count()} products")
        if productos.exists():
            print("- Sample product:", productos.first())
    except Exception as e:
        print(f"Error accessing ProductoVenta: {str(e)}")
    
    # Test template rendering
    print("\nTesting template rendering...")
    try:
        # Test context
        context = {
            'total_productos': 5,
            'productos_por_categoria': {'Test': ['product1', 'product2']}
        }
        
        # Try to render the base template
        try:
            base_template = render_to_string('mesero/base.html', context)
            print("✓ Base template rendered successfully")
            print("Base template preview:")
            print(base_template[:200] + "...")
        except Exception as e:
            print(f"✗ Error rendering base template: {str(e)}")
        
        # Try to render the menu template
        try:
            menu_template = render_to_string('mesero/menu.html', context)
            print("\nMenu template rendered successfully")
            print("Menu template preview:")
            print(menu_template[:200] + "...")
        except Exception as e:
            print(f"✗ Error rendering menu template: {str(e)}")
            
    except Exception as e:
        print(f"Error during template testing: {str(e)}")

if __name__ == '__main__':
    test_menu_view()
