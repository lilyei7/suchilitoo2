import os
import webbrowser
from urllib.parse import urljoin

def main():
    # Open the browser to test the delete functionality
    server_url = "http://localhost:8000"
    list_url = urljoin(server_url, "/dashboard/productos-venta/")
    
    print("===== VERIFICACIÓN FINAL DE SOLUCIÓN =====")
    print("Abriendo navegador para probar la funcionalidad de eliminación...")
    print(f"URL: {list_url}")
    print("\nCorrecciones realizadas:")
    print("1. Se solucionó la redeclaración de la variable productoIdGlobal")
    print("2. Se corrigió el manejo de errores para usar variables seguras")
    print("3. Se aseguró que todos los procesos de verificación usen las variables correctas")
    print("4. Se agregó manejo de casos donde el ID del producto no esté disponible")
    
    print("\nPasos para probar:")
    print("1. Espera a que la página cargue completamente")
    print("2. Abre la consola del navegador (F12)")
    print("3. Haz click en el botón 'Eliminar' de un producto")
    print("4. Confirma la eliminación en el modal")
    print("5. Verifica que no hay errores en la consola después de la eliminación")
    print("6. Verifica que el producto se eliminó correctamente")
    
    # Open the browser
    webbrowser.open(list_url)

if __name__ == "__main__":
    main()
