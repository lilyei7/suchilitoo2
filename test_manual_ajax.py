#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para probar el formulario AJAX de proveedores
"""

import webbrowser
import time

def test_proveedor_form():
    """Test manual del formulario de proveedores"""
    print("🧪 Iniciando test manual del formulario AJAX...")
    print("="*50)
    
    # URL del sistema
    url = "http://127.0.0.1:8000/dashboard/proveedores/"
    
    print(f"📍 Abriendo navegador en: {url}")
    print()
    print("🔍 INSTRUCCIONES DE PRUEBA:")
    print("1. Hacer login con admin/admin123 si es necesario")
    print("2. Hacer clic en 'Nuevo Proveedor'")
    print("3. Llenar el formulario con:")
    print("   - Nombre comercial: Test AJAX Provider")
    print("   - Email: test@ajax.com")
    print("   - Teléfono: 5551234567")
    print("4. Hacer clic en 'Guardar Proveedor'")
    print("5. Verificar que:")
    print("   ✅ NO se redirecciona a una página JSON")
    print("   ✅ El modal se cierra automáticamente")
    print("   ✅ Aparece un toast de éxito")
    print("   ✅ La página se recarga mostrando el nuevo proveedor")
    print()
    print("🚨 SI APARECE UNA PÁGINA JSON, EL AJAX NO FUNCIONA")
    print("="*50)
    
    # Abrir navegador
    webbrowser.open(url)
    
    print("🎯 Navegador abierto. Realiza las pruebas manualmente...")
    print("💡 Presiona F12 para ver la consola del navegador")
    print("🔍 Busca el mensaje: '🚀 Enviando formulario via AJAX...'")

if __name__ == "__main__":
    test_proveedor_form()
