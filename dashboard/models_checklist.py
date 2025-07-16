from django.db import models
from accounts.models import Usuario, Sucursal, Rol

class ChecklistCategory(models.Model):
    """
    Categoría de tareas para el checklist (ej. 'Apertura', 'Cierre', 'Limpieza', etc.)
    """
    name = models.CharField('Nombre', max_length=100)
    order = models.IntegerField('Orden', default=0)
    active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Categoría de Checklist'
        verbose_name_plural = 'Categorías de Checklist'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class ChecklistTask(models.Model):
    """
    Tarea que debe ser completada como parte de un checklist
    """
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descripción', blank=True)
    category = models.ForeignKey(
        ChecklistCategory, 
        on_delete=models.CASCADE, 
        related_name='tasks',
        verbose_name='Categoría'
    )
    requires_evidence = models.BooleanField('Requiere evidencia', default=False)
    default_role = models.ForeignKey(
        Rol, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Rol predeterminado'
    )
    active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Tarea de Checklist'
        verbose_name_plural = 'Tareas de Checklist'
        ordering = ['category__order', 'title']

    def __str__(self):
        return f"{self.title} ({self.category.name})"


class TaskInstance(models.Model):
    """
    Instancia diaria de una tarea de checklist asignada a una sucursal y turno específico
    """
    SHIFT_CHOICES = [
        ('mañana', 'Mañana'),
        ('tarde', 'Tarde'),
        ('noche', 'Noche'),
    ]
    
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
    ]
    
    task = models.ForeignKey(
        ChecklistTask, 
        on_delete=models.CASCADE, 
        related_name='instances',
        verbose_name='Tarea'
    )
    branch = models.ForeignKey(
        Sucursal, 
        on_delete=models.CASCADE, 
        related_name='task_instances',
        verbose_name='Sucursal'
    )
    date = models.DateField('Fecha')
    shift = models.CharField('Turno', max_length=10, choices=SHIFT_CHOICES)
    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES, default='pendiente')
    performed_by = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='completed_tasks',
        verbose_name='Realizado por'
    )
    performed_at = models.DateTimeField('Fecha de realización', null=True, blank=True)
    verified = models.BooleanField('Verificado', default=False)
    verified_by = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_tasks',
        verbose_name='Verificado por'
    )
    verified_at = models.DateTimeField('Fecha de verificación', null=True, blank=True)
    verification_notes = models.TextField('Notas de verificación', blank=True)
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Instancia de Tarea'
        verbose_name_plural = 'Instancias de Tareas'
        ordering = ['-date', 'shift', 'task__category__order', 'task__title']
        unique_together = ['task', 'branch', 'date', 'shift']

    def __str__(self):
        return f"{self.task.title} - {self.branch.nombre} - {self.date} ({self.shift})"
    
    def is_complete(self):
        return self.status == 'completado'
    
    def can_complete(self):
        """Determina si la tarea puede ser marcada como completada"""
        if not self.task.requires_evidence:
            return True
        # Si requiere evidencia, verificar que exista al menos una
        return self.evidence_files.exists()


class Evidence(models.Model):
    """
    Evidencia adjunta a una instancia de tarea
    """
    instance = models.ForeignKey(
        TaskInstance, 
        on_delete=models.CASCADE, 
        related_name='evidence_files',
        verbose_name='Instancia de tarea'
    )
    uploaded_by = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='uploaded_evidence',
        verbose_name='Subido por'
    )
    file = models.FileField('Archivo', upload_to='checklist/evidence/%Y/%m/%d/')
    comment = models.TextField('Comentario', blank=True)
    uploaded_at = models.DateTimeField('Fecha de subida', auto_now_add=True)

    class Meta:
        verbose_name = 'Evidencia'
        verbose_name_plural = 'Evidencias'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Evidencia para {self.instance.task.title} ({self.uploaded_at})"


class IncidentReport(models.Model):
    """
    Reporte de incidente en una sucursal
    """
    CATEGORY_CHOICES = [
        ('mobiliario', 'Mobiliario'),
        ('equipo', 'Equipo'),
        ('instalaciones', 'Instalaciones'),
        ('seguridad', 'Seguridad'),
        ('servicio', 'Servicio'),
        ('personal', 'Personal'),
        ('otro', 'Otro'),
    ]
    
    STATUS_CHOICES = [
        ('abierto', 'Abierto'),
        ('en_proceso', 'En proceso'),
        ('cerrado', 'Cerrado'),
    ]
    
    URGENCY_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    branch = models.ForeignKey(
        Sucursal, 
        on_delete=models.CASCADE, 
        related_name='incidents',
        verbose_name='Sucursal'
    )
    category = models.CharField('Categoría', max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descripción')
    urgency = models.CharField('Nivel de Urgencia', max_length=10, choices=URGENCY_CHOICES, default='media')
    reported_by = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='reported_incidents',
        verbose_name='Reportado por'
    )
    status = models.CharField('Estado', max_length=15, choices=STATUS_CHOICES, default='abierto')
    assigned_to = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_incidents',
        verbose_name='Asignado a'
    )
    resolution_note = models.TextField('Nota de resolución', blank=True)
    reported_at = models.DateTimeField('Fecha de reporte', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)
    resolved_at = models.DateTimeField('Fecha de resolución', null=True, blank=True)

    class Meta:
        verbose_name = 'Reporte de Incidente'
        verbose_name_plural = 'Reportes de Incidentes'
        ordering = ['-reported_at']

    def __str__(self):
        return f"{self.title} - {self.branch.nombre} ({self.get_status_display()})"
        
    @property
    def has_evidence(self):
        """
        Verifica si el incidente tiene evidencias adjuntas
        """
        return self.evidence_files.exists()


class Notification(models.Model):
    """
    Notificación para usuarios del sistema de checklist
    """
    TYPE_CHOICES = [
        ('task_created', 'Tarea creada'),
        ('task_completed', 'Tarea completada'),
        ('evidence_uploaded', 'Evidencia subida'),
        ('incident_reported', 'Incidente reportado'),
        ('incident_updated', 'Incidente actualizado'),
        ('incident_resolved', 'Incidente resuelto'),
    ]
    
    ALERT_TYPES = [
        ('primary', 'Informativa'),
        ('success', 'Éxito'),
        ('warning', 'Advertencia'),
        ('danger', 'Error'),
        ('info', 'Información'),
        ('secondary', 'Secundaria'),
    ]
    
    ICON_CHOICES = [
        ('info-circle', 'Información'),
        ('check-circle', 'Completado'),
        ('exclamation-triangle', 'Advertencia'),
        ('exclamation-circle', 'Error'),
        ('bell', 'Notificación'),
        ('tools', 'Mantenimiento'),
        ('clipboard-check', 'Checklist'),
        ('tasks', 'Tareas'),
        ('camera', 'Evidencia'),
        ('bug', 'Incidente'),
    ]
    
    # Campos que coinciden con la estructura actual de la base de datos
    type = models.CharField('Tipo', max_length=20, choices=TYPE_CHOICES)
    recipient = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        verbose_name='Destinatario'
    )
    title = models.CharField('Título', max_length=200)
    message = models.TextField('Mensaje')
    read = models.BooleanField('Leído', default=False)
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    
    # Campos adicionales para mostrar en la interfaz de usuario
    alert_type = models.CharField('Tipo de alerta', max_length=20, choices=ALERT_TYPES, default='info', null=True, blank=True)
    icon = models.CharField('Ícono', max_length=30, choices=ICON_CHOICES, default='info-circle', null=True, blank=True)
    link = models.CharField('Enlace', max_length=255, null=True, blank=True)
    
    related_task = models.ForeignKey(
        TaskInstance, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='notifications',
        verbose_name='Tarea relacionada'
    )
    related_incident = models.ForeignKey(
        IncidentReport, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='notifications',
        verbose_name='Incidente relacionado'
    )

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()} para {self.recipient.username} ({self.created_at})"
        
    def marcar_como_leida(self):
        """
        Marca la notificación como leída y guarda el cambio
        """
        if not self.read:
            self.read = True
            self.save(update_fields=['read'])
            
    def mark_as_read(self):
        """
        Mark the notification as read and save the change
        """
        return self.marcar_como_leida()


class IncidentEvidence(models.Model):
    """
    Evidencia adjunta a un reporte de incidente
    """
    incident = models.ForeignKey(
        IncidentReport, 
        on_delete=models.CASCADE, 
        related_name='evidence_files',
        verbose_name='Reporte de incidente'
    )
    uploaded_by = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='uploaded_incident_evidence',
        verbose_name='Subido por'
    )
    file = models.FileField('Archivo', upload_to='checklist/incidents/%Y/%m/%d/')
    comment = models.TextField('Comentario', blank=True)
    uploaded_at = models.DateTimeField('Fecha de subida', auto_now_add=True)

    class Meta:
        verbose_name = 'Evidencia de Incidente'
        verbose_name_plural = 'Evidencias de Incidentes'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Evidencia para incidente {self.incident.title} ({self.uploaded_at})"


class IncidentHistory(models.Model):
    """
    Historial de acciones en un incidente (creación, asignación, cambio de estado, etc.)
    """
    ACTION_TYPES = [
        ('creado', 'Creado'),
        ('cambio_estado', 'Cambio de Estado'),
        ('reasignado', 'Reasignado'),
        ('cerrado', 'Cerrado'),
        ('evidencia_agregada', 'Evidencia Agregada'),
        ('comentario', 'Comentario'),
    ]
    
    incident = models.ForeignKey(
        IncidentReport, 
        on_delete=models.CASCADE, 
        related_name='history',
        verbose_name='Incidente'
    )
    action_by = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='incident_actions',
        verbose_name='Realizado por'
    )
    action_type = models.CharField('Tipo de acción', max_length=20, choices=ACTION_TYPES)
    description = models.TextField('Descripción')
    timestamp = models.DateTimeField('Fecha y hora', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Historial de Incidente'
        verbose_name_plural = 'Historial de Incidentes'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.incident.title} ({self.timestamp})"


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
