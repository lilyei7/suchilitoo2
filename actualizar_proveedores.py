import os
import django
import sys

# Configurar entorno Django
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushirestaurant.settings')
django.setup()

from django.db import connection
from django.db.utils import OperationalError
from dashboard.models import Proveedor
from accounts.models import Usuario, Sucursal

def crear_campos_proveedor():
    """
    Crea los campos necesarios en la tabla de proveedores.
    """
    cursor = connection.cursor()
    
    try:
        # Verificar si ya existen los campos
        cursor.execute("PRAGMA table_info(dashboard_proveedor)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        campos_a_crear = []
        if 'creado_por_id' not in columnas:
            campos_a_crear.append('creado_por_id INTEGER REFERENCES accounts_usuario(id)')
        
        if 'sucursal_id' not in columnas:
            campos_a_crear.append('sucursal_id INTEGER REFERENCES accounts_sucursal(id)')
        
        # Crear los campos si es necesario
        for campo in campos_a_crear:
            query = f"ALTER TABLE dashboard_proveedor ADD COLUMN {campo}"
            print(f"Ejecutando: {query}")
            cursor.execute(query)
        
        if campos_a_crear:
            print("Campos creados correctamente.")
        else:
            print("Los campos ya existen, no es necesario crearlos.")
            
    except OperationalError as e:
        print(f"Error al crear campos: {e}")
    finally:
        cursor.close()

def asignar_valores_iniciales():
    """
    Asigna valores iniciales a los campos creados.
    """
    try:
        # Obtener el primer usuario administrador
        admin = Usuario.objects.filter(rol__nombre='admin').first()
        
        if not admin:
            print("No se encontró un usuario administrador. No se pueden asignar valores iniciales.")
            return
        
        # Obtener la primera sucursal
        sucursal = Sucursal.objects.first()
        
        # Actualizar proveedores sin creador asignado
        count = Proveedor.objects.filter(creado_por__isnull=True).update(
            creado_por=admin,
            sucursal=sucursal
        )
        
        print(f"Se han actualizado {count} proveedores para asignarles el usuario administrador como creador y la sucursal principal.")
            
    except Exception as e:
        print(f"Error al asignar valores iniciales: {e}")

if __name__ == "__main__":
    print("Iniciando migración para agregar campos de creador y sucursal a proveedores...")
    crear_campos_proveedor()
    asignar_valores_iniciales()
    print("Migración completada.")
