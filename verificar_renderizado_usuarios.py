#!/usr/bin/env python
"""
Script para verificar el renderizado de la página de usuarios
"""
import os
import sys
import django
import json
from bs4 import BeautifulSoup

# Configurar el entorno de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth import get_user_model
from accounts.models import Rol, Sucursal

User = get_user_model()

def verificar_renderizado_usuarios():
    """Verificar el renderizado de la página de usuarios"""
    # Crear un cliente para las pruebas
    client = Client()
    
    # Verificar que haya un usuario admin
    if not User.objects.filter(is_superuser=True).exists():
        print("❌ No hay usuarios administradores. Creando uno...")
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123456'
        )
        print("✅ Usuario admin creado")
    
    # Iniciar sesión con un usuario admin
    admin = User.objects.filter(is_superuser=True).first()
    client.force_login(admin)
    
    # Obtener la página de usuarios
    response = client.get('/dashboard/usuarios/')
    
    # Verificar respuesta
    if response.status_code == 200:
        print("✅ Página de usuarios cargada correctamente")
        
        # Analizar el HTML con BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Verificar si el modal de crear usuario existe
        modal_crear = soup.find(id='modalCrearUsuario')
        if modal_crear:
            print("✅ Modal de crear usuario encontrado")
            
            # Verificar si el selector de roles existe
            select_rol = modal_crear.find(id='rol')
            if select_rol:
                print("✅ Selector de roles encontrado")
                
                # Contar opciones en el selector
                opciones = select_rol.find_all('option')
                print(f"Opciones encontradas: {len(opciones)}")
                
                for opcion in opciones:
                    print(f"  - Opción: value='{opcion.get('value')}', texto='{opcion.text}'")
                
                if len(opciones) <= 1:
                    print("❌ El selector de roles no tiene opciones o solo tiene la opción por defecto")
            else:
                print("❌ No se encontró el selector de roles en el modal")
        else:
            print("❌ No se encontró el modal de crear usuario")
        
        # Verificar si hay scripts personalizados
        scripts = soup.find_all('script')
        scripts_sin_src = [script for script in scripts if not script.get('src')]
        
        print(f"\nScripts encontrados: {len(scripts)}")
        print(f"Scripts sin src (código inline): {len(scripts_sin_src)}")
        
        # Buscar la función cargarSucursalesRoles
        cargar_roles_encontrado = False
        for script in scripts_sin_src:
            if 'cargarSucursalesRoles' in script.text:
                cargar_roles_encontrado = True
                print("✅ Función cargarSucursalesRoles encontrada")
                break
        
        if not cargar_roles_encontrado:
            print("❌ No se encontró la función cargarSucursalesRoles")
    else:
        print(f"❌ Error al cargar la página de usuarios: {response.status_code}")

if __name__ == "__main__":
    print("Verificando renderizado de la página de usuarios...")
    verificar_renderizado_usuarios()
    
    # Mostrar información adicional
    print("\nInformación adicional:")
    print(f"- Roles activos en la base de datos: {Rol.objects.filter(activo=True).count()}")
    print(f"- Sucursales activas en la base de datos: {Sucursal.objects.filter(activa=True).count()}")
