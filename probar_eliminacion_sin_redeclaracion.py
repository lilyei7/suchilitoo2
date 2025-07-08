import os
import webbrowser
from urllib.parse import urljoin

def main():
    # Open the browser to test the delete functionality
    server_url = "http://localhost:8000"
    list_url = urljoin(server_url, "/dashboard/productos-venta/")
    
    print("Abriendo navegador para probar la funcionalidad de eliminación...")
    print(f"URL: {list_url}")
    print("\nPasos para probar:")
    print("1. Espera a que la página cargue completamente")
    print("2. Abre la consola del navegador (F12)")
    print("3. Haz click en el botón 'Eliminar' de un producto")
    print("4. Confirma la eliminación en el modal")
    print("5. Verifica que no hay errores de redeclaración en la consola")
    print("6. Verifica que el producto se eliminó correctamente")
    print("\nEl script ha sido ejecutado con éxito si no aparecen errores de redeclaración en la consola")
    
    # Open the browser
    webbrowser.open(list_url)

if __name__ == "__main__":
    main()
