import os
import sys
import django
from pathlib import Path

# Add the project path to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.db import connections, transaction
from django.db.utils import OperationalError, ProgrammingError
from django.contrib.auth import get_user_model

print("Enhancing the Incident Reporting System...")

def create_incident_comment_model():
    """
    Adds IncidentComment model to models_checklist.py if it doesn't exist
    """
    models_path = Path(__file__).parent / 'dashboard' / 'models_checklist.py'
    
    # Check if the file exists
    if not models_path.exists():
        print(f"Error: {models_path} not found.")
        return False
    
    # Read the file content
    with open(models_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if the model already exists in the file
    if 'class IncidentComment(' in content:
        print("IncidentComment model already exists in models_checklist.py")
        return False
    
    # Add the model to the end of the file
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
    
    print("Added IncidentComment model to models_checklist.py")
    return True

def update_add_incident_comment_view():
    """
    Updates the add_incident_comment view to use the IncidentComment model
    """
    views_path = Path(__file__).parent / 'dashboard' / 'views' / 'checklist_views.py'
    
    if not views_path.exists():
        print(f"Error: {views_path} not found.")
        return False
    
    with open(views_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if we need to update
    if 'from dashboard.models_checklist import IncidentComment' not in content:
        # Add import
        import_statement = 'from dashboard.models_checklist import IncidentReport, IncidentHistory'
        updated_import = 'from dashboard.models_checklist import IncidentReport, IncidentHistory, IncidentComment'
        content = content.replace(import_statement, updated_import)
    
    # Update the add_incident_comment function
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
    
    print("Updated add_incident_comment view in checklist_views.py")
    return True

def create_table_manually():
    """
    Creates the IncidentComment table in the database manually
    """
    try:
        with connections['default'].cursor() as cursor:
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dashboard_incidentcomment'")
            if cursor.fetchone():
                print("Table dashboard_incidentcomment already exists")
                return True
            
            # Create table
            cursor.execute("""
            CREATE TABLE "dashboard_incidentcomment" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "text" text NOT NULL,
                "created_at" datetime NOT NULL,
                "incident_id" integer NOT NULL REFERENCES "dashboard_incidentreport" ("id") DEFERRABLE INITIALLY DEFERRED,
                "user_id" integer NULL REFERENCES "dashboard_usuario" ("id") DEFERRABLE INITIALLY DEFERRED
            )
            """)
            
            # Create indexes
            cursor.execute('CREATE INDEX "dashboard_incidentcomment_incident_id_idx" ON "dashboard_incidentcomment" ("incident_id")')
            cursor.execute('CREATE INDEX "dashboard_incidentcomment_user_id_idx" ON "dashboard_incidentcomment" ("user_id")')
            
            print("Successfully created dashboard_incidentcomment table manually")
            return True
            
    except Exception as e:
        print(f"Error creating table: {e}")
        return False

def migrate_comments_from_history():
    """
    Migrates existing comments from IncidentHistory to IncidentComment
    """
    try:
        from dashboard.models_checklist import IncidentHistory, IncidentComment
        
        # Find all comment entries in history
        comment_entries = IncidentHistory.objects.filter(action_type='comentario')
        
        if not comment_entries.exists():
            print("No comment entries found in history to migrate")
            return True
        
        # Check if any comments already exist in the IncidentComment table
        if IncidentComment.objects.exists():
            print("Comments already exist in IncidentComment table. Skipping migration.")
            return True
        
        counter = 0
        # Migrate each entry
        with transaction.atomic():
            for entry in comment_entries:
                # Create a comment from the history entry
                comment_text = entry.description
                if comment_text.startswith('Comentó: '):
                    comment_text = comment_text[9:]  # Remove "Comentó: " prefix
                
                IncidentComment.objects.create(
                    incident=entry.incident,
                    user=entry.action_by,
                    text=comment_text,
                    created_at=entry.timestamp
                )
                counter += 1
        
        print(f"Successfully migrated {counter} comments from history to IncidentComment table")
        return True
        
    except Exception as e:
        print(f"Error migrating comments: {e}")
        return False

def main():
    model_created = create_incident_comment_model()
    view_updated = update_add_incident_comment_view()
    
    if model_created or view_updated:
        try:
            # Try to create tables using migrations
            import subprocess
            subprocess.run([sys.executable, 'manage.py', 'makemigrations', 'dashboard'], 
                           cwd=os.path.dirname(os.path.abspath(__file__)))
            subprocess.run([sys.executable, 'manage.py', 'migrate', 'dashboard'], 
                           cwd=os.path.dirname(os.path.abspath(__file__)))
            print("Successfully created tables using migrations")
        except Exception as e:
            print(f"Error creating tables via migrations: {e}")
            print("Trying to create table manually...")
            create_table_manually()
    
    # Migrate existing comments
    migrate_comments_from_history()
    
    print("\nIncident Reporting System enhancement completed!")
    print("\nNext steps:")
    print("1. Restart your Django server if it's running")
    print("2. Test adding comments to incidents")
    print("3. Verify that comments appear in the incident history timeline")

if __name__ == "__main__":
    main()
