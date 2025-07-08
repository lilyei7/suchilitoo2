import os
import time
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
    print("2. Haz click en el botón 'Eliminar' de un producto")
    print("3. Confirma la eliminación en el modal")
    print("4. Observa la consola del navegador (F12) para verificar que no hay errores")
    print("5. Verifica que el producto se eliminó correctamente")
    print("\nEl script ha sido ejecutado con éxito si no aparecen errores ReferenceError en la consola")
    
    # Open the browser
    webbrowser.open(list_url)

if __name__ == "__main__":
    main()
