"""
Este script abre una página web en el navegador 
para probar visualmente el botón de eliminar
"""
import webbrowser
import os
import time
import subprocess
import sys

def probar_eliminar_producto():
    """
    Abre la página de productos para probar la funcionalidad de eliminación
    """
    print("=== ABRIENDO NAVEGADOR PARA PROBAR ELIMINACIÓN DE PRODUCTOS ===")
    
    # URLs para probar
    urls = [
        "http://127.0.0.1:8000/dashboard/productos-venta/",
        "http://127.0.0.1:8000/dashboard/productos-venta/diagnostico/"
    ]
    
    # Verificar que el servidor esté en ejecución
    print("Verificando que el servidor Django esté en ejecución...")
    try:
        import requests
        response = requests.get(urls[0])
        if response.status_code != 200:
            print(f"❌ El servidor Django no está respondiendo (código {response.status_code})")
            return
        print("✅ Servidor Django en ejecución")
    except:
        print("❌ No se pudo conectar al servidor Django")
        print("   Asegúrate de que el servidor esté en ejecución con 'python manage.py runserver'")
        return
    
    # Instrucciones
    print("\nPasos para probar la eliminación de productos:")
    print("1. Se abrirán dos pestañas en tu navegador:")
    print("   - La página de productos")
    print("   - La página de diagnóstico")
    print("2. En la página de productos:")
    print("   - Busca un producto de prueba (preferiblemente uno creado para tests)")
    print("   - Haz clic en el botón rojo de eliminación (ícono de papelera)")
    print("   - Verifica que el modal se abre y muestra el nombre del producto")
    print("   - Haz clic en 'Eliminar' para confirmar")
    print("   - Verifica que el producto se elimina y la página se recarga")
    print("3. En la página de diagnóstico:")
    print("   - Verifica que aparece el indicador azul en la esquina inferior derecha")
    print("   - Haz clic en el botón 'Probar JavaScript' para verificar que funciona")
    print("4. En ambas páginas:")
    print("   - Abre la consola del navegador (F12 -> Console)")
    print("   - Verifica que no hay errores de JavaScript")
    print("   - Verifica que aparecen los logs de depuración")
    
    # Preguntar si quiere continuar
    respuesta = input("\n¿Deseas abrir las páginas en el navegador? (s/n): ")
    if respuesta.lower() != 's':
        print("Operación cancelada.")
        return
    
    # Abrir navegador
    print("\nAbriendo páginas en el navegador...")
    for url in urls:
        webbrowser.open_new_tab(url)
        time.sleep(1)  # Esperar un segundo entre cada apertura
    
    print("\n✅ Páginas abiertas en el navegador")
    print("Sigue los pasos anteriores para probar la eliminación de productos")
    print("Recuerda revisar la consola del navegador (F12 -> Console) para verificar logs y errores")

if __name__ == "__main__":
    probar_eliminar_producto()
