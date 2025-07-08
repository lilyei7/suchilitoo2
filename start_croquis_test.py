#!/usr/bin/env python3
"""
Script to start the Django server and provide a direct test URL for the croquis editor
"""

import os
import subprocess
import sys
import django
from django.db import connection

def start_server_and_test():
    print("🔍 Verificando estado del proyecto...")
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
    django.setup()
    
    try:
        # Verificar conexión a la base de datos
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Conexión a la base de datos OK")
        
        # Verificar que existe al menos una sucursal
        from dashboard.models import Sucursal
        sucursales = Sucursal.objects.all()
        if sucursales.exists():
            sucursal = sucursales.first()
            print(f"✅ Sucursal encontrada: {sucursal.nombre} (ID: {sucursal.id})")
            
            print(f"\n🔗 URLs para probar:")
            print(f"Editor de croquis: http://localhost:8000/dashboard/sucursales/{sucursal.id}/croquis/")
            print(f"Preview de croquis: http://localhost:8000/dashboard/sucursales/{sucursal.id}/croquis/preview/")
            print(f"Dashboard principal: http://localhost:8000/dashboard/")
            
        else:
            print("⚠️  No hay sucursales registradas")
            
        print(f"\n🚀 Para probar el editor de croquis:")
        print(f"1. Abre una terminal en: c:\\Users\\olcha\\Desktop\\sushi_restaurant - Copy (2)\\suchilitoo2")
        print(f"2. Ejecuta: python manage.py runserver")
        print(f"3. Ve a: http://localhost:8000/dashboard/")
        print(f"4. Inicia sesión con las credenciales del sistema")
        print(f"5. Ve a Sucursales > [Nombre Sucursal] > Diseñar Croquis")
        print(f"6. Abre las herramientas de desarrollador del navegador (F12)")
        print(f"7. Ve a la pestaña Console para ver errores JavaScript")
        
        print(f"\n🔧 Para depurar los errores JavaScript:")
        print(f"- Abre F12 en el navegador")
        print(f"- Ve a Console")
        print(f"- Recarga la página del editor de croquis")
        print(f"- Reporta cualquier error ReferenceError que veas")
        
    except Exception as e:
        print(f"❌ Error verificando el proyecto: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_server_and_test()
