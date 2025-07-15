#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar el acceso al sistema de checklist
"""

import os
import sys
import django
import requests
from bs4 import BeautifulSoup
import webbrowser
import time

# Configurar entorno Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management.utils import get_random_secret_key

# URL base del servidor
BASE_URL = "http://127.0.0.1:8000"

def verificar_acceso_checklist():
    print("🔍 Verificando acceso al sistema de checklist...")
    
    # Verificar que el servidor esté ejecutándose
    try:
        response = requests.get(f"{BASE_URL}/login/")
        if response.status_code != 200:
            print(f"❌ Error: El servidor no está respondiendo. Código: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Error: No se puede conectar al servidor. Asegúrate de que esté ejecutándose.")
        return False
    
    # Iniciar sesión
    print("🔑 Intentando iniciar sesión...")
    session = requests.Session()
    
    # Obtener token CSRF
    login_page = session.get(f"{BASE_URL}/login/")
    soup = BeautifulSoup(login_page.text, 'html.parser')
    
    try:
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
    except:
        print("❌ Error: No se pudo obtener el token CSRF de la página de login.")
        return False
    
    # Verificar si existe un usuario administrador
    Usuario = get_user_model()
    try:
        admin_user = Usuario.objects.filter(is_staff=True).first()
        if not admin_user:
            print("⚠ No se encontró ningún usuario administrador. Creando uno para pruebas...")
            # Crear un usuario administrador para pruebas
            admin_user = Usuario.objects.create_superuser(
                username="admin_test",
                email="admin@example.com",
                password="admin12345",
                is_staff=True,
                is_active=True
            )
            print(f"✅ Usuario administrador creado: {admin_user.username}")
        
        # Intentar iniciar sesión
        login_data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': admin_user.username,
            'password': 'admin12345'  # Asumimos esta contraseña para pruebas
        }
        
        login_response = session.post(f"{BASE_URL}/login/", data=login_data, headers={
            'Referer': f"{BASE_URL}/login/"
        })
        
        if "error" in login_response.text.lower():
            print("⚠ No se pudo iniciar sesión con las credenciales proporcionadas.")
            print("⚠ Intentando crear y usar un nuevo usuario de prueba...")
            
            # Crear un nuevo usuario de prueba
            test_username = f"test_user_{get_random_secret_key()[:8]}"
            test_password = "password123"
            
            test_user = Usuario.objects.create_user(
                username=test_username,
                password=test_password,
                is_staff=True,
                is_active=True
            )
            
            # Intentar iniciar sesión con el nuevo usuario
            login_data = {
                'csrfmiddlewaretoken': csrf_token,
                'username': test_username,
                'password': test_password
            }
            
            login_response = session.post(f"{BASE_URL}/login/", data=login_data, headers={
                'Referer': f"{BASE_URL}/login/"
            })
            
            if "error" in login_response.text.lower():
                print("❌ Error: No se pudo iniciar sesión con el usuario de prueba.")
                return False
        
        # Verificar redirección después del login
        print("🔍 Verificando redirección después del login...")
        if not login_response.url.endswith('/dashboard/'):
            print(f"⚠ Advertencia: La redirección después del login fue a {login_response.url} en lugar de /dashboard/")
        
        # Acceder al checklist
        print("🔍 Intentando acceder al sistema de checklist...")
        checklist_response = session.get(f"{BASE_URL}/dashboard/checklist/")
        
        # Verificar si la página del checklist cargó correctamente
        if checklist_response.status_code == 200:
            print("✅ Acceso exitoso al sistema de checklist.")
            
            # Guardar HTML para inspección
            with open("checklist_page.html", "w", encoding="utf-8") as f:
                f.write(checklist_response.text)
            
            print("📄 Se ha guardado el HTML de la página del checklist en 'checklist_page.html'")
            
            # Abrir en el navegador para verificación visual
            print("🌐 Abriendo página en el navegador para verificación visual...")
            checklist_url = f"{BASE_URL}/dashboard/checklist/"
            webbrowser.open(checklist_url)
            
            return True
        else:
            print(f"❌ Error: No se pudo acceder al checklist. Código: {checklist_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la verificación: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando verificación del sistema de checklist...")
    verificar_acceso_checklist()
    print("✅ Verificación completada.")
