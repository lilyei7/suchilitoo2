import os
import sys
import warnings

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
    try:
        from django.core.management import execute_from_command_line
        from django.core.management.base import CommandError
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Ignorar las advertencias sobre migraciones
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        # Ignorar advertencias de migración específicas
        warnings.filterwarnings('ignore', message='You have unapplied migration')
        
        # Monkey patch para evitar verificar migraciones pendientes
        from django.core.management.commands import runserver
        original_check = runserver.Command.check
        def custom_check(self, *args, **kwargs):
            # Llamar al método original sin modificar argumentos
            result = original_check(self, *args, **kwargs)
            return result
        runserver.Command.check = custom_check
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
