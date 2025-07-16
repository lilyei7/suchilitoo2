import os
import django
import sys

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "suchilitoo.settings")
django.setup()

# Now you can import Django models
from django.db import connections

with connections['default'].cursor() as cursor:
    cursor.execute("SELECT app, name FROM django_migrations WHERE app='dashboard' ORDER BY id")
    migrations = cursor.fetchall()
    
    print("Dashboard migrations in database:")
    for migration in migrations:
        print(f"  - {migration[0]}.{migration[1]}")
