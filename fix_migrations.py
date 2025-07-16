"""
This script helps fix migration issues by cleaning up the migration history.
It recreates a single initial migration that includes all models.
"""

import os
import shutil
import sys
from django.core.management import execute_from_command_line

# Change to the project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def main():
    # Step 1: Delete all existing migration files except __init__.py
    migration_dir = os.path.join('dashboard', 'migrations')
    for filename in os.listdir(migration_dir):
        if filename != '__init__.py' and filename.endswith('.py'):
            file_path = os.path.join(migration_dir, filename)
            print(f"Removing {file_path}")
            os.remove(file_path)
    
    # Step 2: Clear the django_migrations table
    print("Clearing django_migrations table...")
    execute_from_command_line(['manage.py', 'dbshell', '-c', 
                              "DELETE FROM django_migrations WHERE app = 'dashboard';"])
    
    # Step 3: Create new initial migration
    print("Creating new initial migration...")
    execute_from_command_line(['manage.py', 'makemigrations', 'dashboard'])
    
    # Step 4: Apply the migration
    print("Applying migration...")
    execute_from_command_line(['manage.py', 'migrate', 'dashboard'])
    
    print("Migration cleanup complete.")

if __name__ == "__main__":
    main()
