import os
import sys
import sqlite3

def reset_migrations():
    """Resets all migrations for the dashboard app in the database"""
    # Ruta de la base de datos SQLite
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
    
    if not os.path.exists(db_path):
        print(f"Error: Base de datos no encontrada en {db_path}")
        return False
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Eliminar todas las migraciones de dashboard de la tabla django_migrations
        cursor.execute("DELETE FROM django_migrations WHERE app = 'dashboard'")
        conn.commit()
        
        print("Todas las migraciones de dashboard han sido eliminadas de la base de datos.")
        conn.close()
        return True
    except Exception as e:
        print(f"Error al resetear migraciones: {e}")
        return False

if __name__ == "__main__":
    reset_migrations()
    print("Ahora puedes ejecutar 'python manage.py migrate dashboard' para aplicar las migraciones desde cero.")
