import os
import sys
import django

# Add the project path to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suchilito.settings')
django.setup()

from django.db import migrations, models
from django.contrib.auth import get_user_model
from dashboard.models_checklist import IncidentReport, IncidentHistory

print("Adding IncidentComment model to enhance the incident reporting system...")

def create_incident_comment_model():
    """
    Creates the IncidentComment model and adds it to models_checklist.py
    """
    from django.db import connections
    from django.db.utils import OperationalError

    # Check if the table already exists
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dashboard_incidentcomment'")
            if cursor.fetchone():
                print("Table 'dashboard_incidentcomment' already exists. Skipping model creation.")
                return False
    except OperationalError:
        print("Could not check if table exists. Continuing with model creation...")

    # Add the model to models_checklist.py
    models_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              'dashboard', 'models_checklist.py')
    
    with open(models_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if the model already exists in the file
    if 'class IncidentComment(' in content:
        print("IncidentComment model already exists in models_checklist.py. Skipping model addition.")
        return False
    
    # Append the model to the end of the file
    incident_comment_model = """

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
        return f"Comentario en {self.incident.title} por {self.user.get_full_name()}"
        
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Create history entry for new comments
        if is_new:
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
"""
    
    # Add import if needed
    if "ChecklistNotification" not in content:
        # Find the last import line
        import_lines = [line for line in content.split('\n') if line.strip().startswith('from ') or line.strip().startswith('import ')]
        if import_lines:
            last_import = import_lines[-1]
            content = content.replace(last_import, last_import + "\nfrom dashboard.models_checklist import ChecklistNotification")
    
    with open(models_path, 'a', encoding='utf-8') as file:
        file.write(incident_comment_model)
    
    print("Successfully added IncidentComment model to models_checklist.py")
    return True

def update_add_comment_view():
    """
    Update the add_incident_comment view to create history entries
    """
    views_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             'dashboard', 'views', 'checklist_views.py')
    
    with open(views_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if the function already exists
    if 'def add_incident_comment(' not in content:
        print("Warning: add_incident_comment view not found. Cannot update.")
        return
    
    # Find the add_incident_comment function and check if it already creates history entries
    if 'IncidentHistory.objects.create' in content and 'action_type=\'comentario\'' in content:
        print("add_incident_comment view already creates history entries. Skipping update.")
        return
    
    # Update the function to create history entries
    updated_content = content.replace(
        "    comment = IncidentComment.objects.create(\n        incident=incident,\n        user=request.user,\n        text=comment_text\n    )",
        "    comment = IncidentComment.objects.create(\n        incident=incident,\n        user=request.user,\n        text=comment_text\n    )\n    \n    # Create history entry\n    IncidentHistory.objects.create(\n        incident=incident,\n        action_by=request.user,\n        action_type='comentario',\n        description=f\"Comentó: {comment_text[:100]}{'...' if len(comment_text) > 100 else ''}\"\n    )"
    )
    
    if updated_content != content:
        with open(views_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        print("Successfully updated add_incident_comment view to create history entries")
    else:
        print("Could not update add_incident_comment view. Manual inspection needed.")

def make_migrations():
    """
    Make migrations for the new model
    """
    try:
        import subprocess
        subprocess.run([sys.executable, 'manage.py', 'makemigrations', 'dashboard'], 
                       cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        print("Successfully created migrations")
        
        subprocess.run([sys.executable, 'manage.py', 'migrate', 'dashboard'], 
                       cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        print("Successfully applied migrations")
    except Exception as e:
        print(f"Error making migrations: {e}")
        print("You'll need to run 'python manage.py makemigrations dashboard' and 'python manage.py migrate dashboard' manually")

if __name__ == "__main__":
    model_created = create_incident_comment_model()
    update_add_comment_view()
    
    if model_created:
        make_migrations()
    
    print("\nDone! The incident comment system has been enhanced.")
    print("Next steps:")
    print("1. Run the Django server if it's not already running")
    print("2. Test adding comments to incidents")
    print("3. Check that comments appear in the incident history timeline")
