from django.core.management.base import BaseCommand
from restaurant.models import Receta
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Actualizar nombres de recetas con valores predeterminados'

    def handle(self, *args, **options):
        # Actualizar nombres de recetas antiguas si tienen el valor por defecto
        recetas_actualizadas = 0
        for receta in Receta.objects.filter(nombre="Receta").all():
            # Asignar nombres personalizados basados en el ID
            nombre_original = receta.nombre
            if receta.id == 1:
                receta.nombre = "Te 1LT Envasado"
            elif receta.id == 2:
                receta.nombre = "Favorito Especial"
            else:
                receta.nombre = f"Receta Personalizada {receta.id}"
                
            # Guardar los cambios en la base de datos
            receta.save()
            recetas_actualizadas += 1
            self.stdout.write(self.style.SUCCESS(f'Actualizado nombre de receta ID {receta.id} de "{nombre_original}" a "{receta.nombre}"'))
            
        if recetas_actualizadas == 0:
            self.stdout.write(self.style.WARNING('No se encontraron recetas con el nombre predeterminado "Receta"'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Se actualizaron {recetas_actualizadas} recetas correctamente'))
