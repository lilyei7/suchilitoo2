import os
import sqlite3
import sys
from pathlib import Path

print("🔨 Forzando corrección del modelo IncidentComment...")

def fix_incident_comment_model():
    """
    Aplica todas las correcciones necesarias para el modelo IncidentComment
    independientemente de las migraciones
    """
    try:
        # 1. Verificar que el archivo models_checklist.py existe
        models_path = Path(os.path.dirname(os.path.abspath(__file__))) / 'dashboard' / 'models_checklist.py'
        if not models_path.exists():
            print(f"❌ Error: No se encontró el archivo {models_path}")
            return False
            
        # 2. Leer el contenido actual
        with open(models_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 3. Comprobar si ya existe el modelo IncidentComment
        if 'class IncidentComment(' in content:
            print("✅ El modelo IncidentComment ya existe en models_checklist.py")
        else:
            # Añadir el modelo IncidentComment al final del archivo
            incident_comment_model = '''

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
'''
            
            with open(models_path, 'a', encoding='utf-8') as f:
                f.write(incident_comment_model)
                
            print("✅ Modelo IncidentComment añadido a models_checklist.py")
            
        # 4. Actualizar la vista para usar el modelo
        views_path = Path(os.path.dirname(os.path.abspath(__file__))) / 'dashboard' / 'views' / 'checklist_views.py'
        if not views_path.exists():
            print(f"❌ Error: No se encontró el archivo {views_path}")
            return False
            
        # Leer el contenido actual
        with open(views_path, 'r', encoding='utf-8') as f:
            views_content = f.read()
            
        # Comprobar si ya está actualizada
        if 'from dashboard.models_checklist import IncidentComment' in views_content:
            print("✅ La vista ya está actualizada para usar IncidentComment")
        else:
            # Actualizar las importaciones
            old_import = 'from dashboard.models_checklist import IncidentReport, IncidentHistory'
            new_import = 'from dashboard.models_checklist import IncidentReport, IncidentHistory, IncidentComment'
            
            views_content = views_content.replace(old_import, new_import)
            
            # Actualizar la función add_incident_comment
            old_function = """def add_incident_comment(request, incident_id):
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
            
            new_function = """def add_incident_comment(request, incident_id):
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
        )"""
            
            views_content = views_content.replace(old_function, new_function)
            
            with open(views_path, 'w', encoding='utf-8') as f:
                f.write(views_content)
                
            print("✅ Vista add_incident_comment actualizada")
        
        # 5. Crear la tabla en la base de datos si no existe
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
        
        if not os.path.exists(db_path):
            print(f"❌ Error: Base de datos no encontrada en {db_path}")
            return False
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si existe la tabla
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dashboard_incidentcomment'")
        if cursor.fetchone():
            print("✅ La tabla dashboard_incidentcomment ya existe")
        else:
            # Crear la tabla
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
            cursor.execute('CREATE INDEX IF NOT EXISTS "dashboard_incidentcomment_incident_id_idx" ON "dashboard_incidentcomment" ("incident_id")')
            cursor.execute('CREATE INDEX IF NOT EXISTS "dashboard_incidentcomment_user_id_idx" ON "dashboard_incidentcomment" ("user_id")')
            
            conn.commit()
            print("✅ Tabla dashboard_incidentcomment creada")
            
        # 6. Asegurarse de que la migración está registrada
        cursor.execute("SELECT id FROM django_migrations WHERE app = 'dashboard' AND name = '0008_incidentcomment'")
        if cursor.fetchone():
            print("✅ Migración dashboard.0008_incidentcomment ya registrada")
        else:
            # Registrar la migración
            cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES ('dashboard', '0008_incidentcomment', datetime('now'))
            """)
            conn.commit()
            print("✅ Migración dashboard.0008_incidentcomment registrada")
            
        conn.close()
        
        print("\n🚀 Implementación del modelo IncidentComment completada")
        print("Ahora puedes ejecutar el servidor Django normalmente:")
        print("python manage.py runserver")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_incident_comment_model()
