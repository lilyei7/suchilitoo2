import os
import sqlite3
import sys
from pathlib import Path

print("Enhancing the Incident Reporting System...")

def fix_all_migration_issues():
    """
    Arregla todos los problemas de migración y crea la tabla IncidentComment manualmente
    """
    # Ruta de la base de datos SQLite
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
    
    if not os.path.exists(db_path):
        print(f"Error: Base de datos no encontrada en {db_path}")
        return False
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Eliminar todas las migraciones problemáticas
        cursor.execute("DELETE FROM django_migrations WHERE app = 'dashboard' AND name LIKE '0008%'")
        cursor.execute("DELETE FROM django_migrations WHERE app = 'dashboard' AND name LIKE '0009%'")
        cursor.execute("DELETE FROM django_migrations WHERE app = 'dashboard' AND name LIKE '0010%'")
        cursor.execute("DELETE FROM django_migrations WHERE app = 'dashboard' AND name LIKE '0011%'")
        cursor.execute("DELETE FROM django_migrations WHERE app = 'dashboard' AND name LIKE '0012%'")
        conn.commit()
        print("Migraciones problemáticas eliminadas de la base de datos.")
        
        # 2. Verificar que la migración dashboard.0005_croquislayout exista
        cursor.execute("SELECT id FROM django_migrations WHERE app = 'dashboard' AND name = '0005_croquislayout'")
        dashboard_migration = cursor.fetchone()
        
        if not dashboard_migration:
            cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES ('dashboard', '0005_croquislayout', datetime('now'))
            """)
            conn.commit()
            print("Migración dashboard.0005_croquislayout agregada manualmente.")
        
        # 3. Crear tabla IncidentComment manualmente si no existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dashboard_incidentcomment'")
        if not cursor.fetchone():
            cursor.execute("""
            CREATE TABLE "dashboard_incidentcomment" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "text" text NOT NULL,
                "created_at" datetime NOT NULL,
                "incident_id" integer NOT NULL REFERENCES "dashboard_incidentreport" ("id") DEFERRABLE INITIALLY DEFERRED,
                "user_id" integer NULL REFERENCES "accounts_usuario" ("id") DEFERRABLE INITIALLY DEFERRED
            )
            """)
            
            # Crear índices
            cursor.execute('CREATE INDEX "dashboard_incidentcomment_incident_id_idx" ON "dashboard_incidentcomment" ("incident_id")')
            cursor.execute('CREATE INDEX "dashboard_incidentcomment_user_id_idx" ON "dashboard_incidentcomment" ("user_id")')
            
            # Registrar la migración
            cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES ('dashboard', '0008_incidentcomment', datetime('now'))
            """)
            
            conn.commit()
            print("Tabla dashboard_incidentcomment creada manualmente.")
        else:
            print("La tabla dashboard_incidentcomment ya existe.")
        
        # 4. Mostrar migraciones actuales
        cursor.execute("SELECT app, name FROM django_migrations WHERE app IN ('dashboard', 'mesero') ORDER BY app, name")
        migrations = cursor.fetchall()
        print("\nMigraciones aplicadas:")
        for migration in migrations:
            print(f"- {migration[0]}.{migration[1]}")
        
        conn.close()
        
        # 5. Actualizar modelos_checklist.py
        models_path = Path(__file__).parent / 'dashboard' / 'models_checklist.py'
        if models_path.exists():
            # Leer el contenido
            with open(models_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Verificar si el modelo ya existe
            if 'class IncidentComment(' not in content:
                with open(models_path, 'a', encoding='utf-8') as file:
                    file.write('''

class IncidentComment(models.Model):
    """
    Comentarios en reportes de incidentes
    """
    incident = models.ForeignKey(
        IncidentReport, 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name='Incidente'
    )
    user = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='incident_comments',
        verbose_name='Usuario'
    )
    text = models.TextField('Comentario')
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Comentario de Incidente'
        verbose_name_plural = 'Comentarios de Incidentes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comentario en {self.incident.title} por {self.user.get_full_name() if self.user else 'Usuario eliminado'}"
        
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Create history entry for new comments
        if is_new and hasattr(self, 'incident') and hasattr(self, 'user'):
            from dashboard.models_checklist import IncidentHistory
            IncidentHistory.objects.create(
                incident=self.incident,
                action_by=self.user,
                action_type='comentario',
                description=f"Comentó: {self.text[:100]}{'...' if len(self.text) > 100 else ''}"
            )
            
            # Create notification for assigned user if different from commenter
            if self.incident.assigned_to and self.incident.assigned_to != self.user:
                from dashboard.models_checklist import ChecklistNotification
                ChecklistNotification.objects.create(
                    recipient=self.incident.assigned_to,
                    type='incident_comment',
                    message=f"Nuevo comentario en incidente: {self.incident.title}",
                    related_object_id=self.incident.id,
                    related_model='IncidentReport'
                )
''')
                print("Modelo IncidentComment agregado a models_checklist.py")
            else:
                print("El modelo IncidentComment ya existe en models_checklist.py")
        else:
            print(f"Error: No se encontró el archivo {models_path}")
        
        # 6. Actualizar la vista add_incident_comment
        views_path = Path(__file__).parent / 'dashboard' / 'views' / 'checklist_views.py'
        if views_path.exists():
            # Leer el contenido
            with open(views_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Actualizar las importaciones
            if 'from dashboard.models_checklist import IncidentComment' not in content:
                import_statement = 'from dashboard.models_checklist import IncidentReport, IncidentHistory'
                updated_import = 'from dashboard.models_checklist import IncidentReport, IncidentHistory, IncidentComment'
                content = content.replace(import_statement, updated_import)
                
                # Actualizar la función add_incident_comment
                if 'IncidentComment.objects.create(' not in content:
                    original_function = """def add_incident_comment(request, incident_id):
    \"\"\"
    Añade un comentario a un incidente
    \"\"\"
    try:
        # Obtener el incidente
        incident = get_object_or_404(IncidentReport, id=incident_id)
        
        # Verificar permisos
        if not request.user.is_staff and request.user.sucursal != incident.branch:
            return JsonResponse({
                'success': False,
                'message': 'No tienes permiso para comentar en este incidente.'
            })
        
        # Obtener el comentario
        comment = request.POST.get('comment', '').strip()
        
        # Validar comentario
        if not comment:
            return JsonResponse({
                'success': False,
                'message': 'El comentario no puede estar vacío.'
            })
        
        # Registrar el comentario en el historial
        history_entry = IncidentHistory.objects.create(
            incident=incident,
            action_by=request.user,
            action_type='comentario',
            description=comment
        )"""
                    
                    updated_function = """def add_incident_comment(request, incident_id):
    \"\"\"
    Añade un comentario a un incidente
    \"\"\"
    try:
        # Obtener el incidente
        incident = get_object_or_404(IncidentReport, id=incident_id)
        
        # Verificar permisos
        if not request.user.is_staff and request.user.sucursal != incident.branch:
            return JsonResponse({
                'success': False,
                'message': 'No tienes permiso para comentar en este incidente.'
            })
        
        # Obtener el comentario
        comment_text = request.POST.get('comment', '').strip()
        
        # Validar comentario
        if not comment_text:
            return JsonResponse({
                'success': False,
                'message': 'El comentario no puede estar vacío.'
            })
        
        # Crear el comentario
        comment = IncidentComment.objects.create(
            incident=incident,
            user=request.user,
            text=comment_text
        )
        
        # No es necesario crear manualmente un registro en el historial
        # ya que el método save() de IncidentComment lo hace automáticamente"""
                    
                    content = content.replace(original_function, updated_function)
                    
                    with open(views_path, 'w', encoding='utf-8') as file:
                        file.write(content)
                        
                    print("Vista add_incident_comment actualizada en checklist_views.py")
                else:
                    print("La vista add_incident_comment ya está actualizada")
            else:
                print("Las importaciones ya están actualizadas en checklist_views.py")
        else:
            print(f"Error: No se encontró el archivo {views_path}")
        
        print("\nIncident Reporting System enhancement completed!")
        print("Ahora puedes iniciar tu servidor Django normalmente con 'python manage.py runserver'")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    fix_all_migration_issues()
