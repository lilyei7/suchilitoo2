from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.conf import settings
import os
from accounts.models import Sucursal

class Rol(models.Model):
    """Modelo para los roles de empleados en el sistema"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    permisos = models.JSONField(default=dict)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['nombre']

def empleado_foto_path(instance, filename):
    """Define la ruta para guardar las fotos de los empleados"""
    ext = filename.split('.')[-1]
    # Formato: fotos_empleados/ID-NOMBRE-APELLIDO.ext
    filename = f"{instance.id}-{instance.nombre}-{instance.apellido}.{ext}"
    return os.path.join('fotos_empleados', filename)

def empleado_documento_path(instance, filename):
    """Define la ruta para guardar los documentos de los empleados"""
    # Formato: documentos_empleados/ID/TIPO-FECHA.ext
    ext = filename.split('.')[-1]
    date_str = timezone.now().strftime("%Y%m%d")
    filename = f"{instance.tipo}-{date_str}.{ext}"
    return os.path.join('documentos_empleados', str(instance.empleado.id), filename)

class Empleado(models.Model):
    """Modelo principal para empleados"""
    ESTADO_CHOICES = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('vacaciones', 'De Vacaciones'),
        ('permiso', 'De Permiso'),
    )
    
    TIPO_CONTRATO_CHOICES = (
        ('indefinido', 'Indefinido'),
        ('plazo_fijo', 'Plazo Fijo'),
        ('por_obra', 'Por Obra o Faena'),
        ('part_time', 'Part Time'),
    )
    
    # Datos personales
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rut = models.CharField(max_length=15, unique=True)
    fecha_nacimiento = models.DateField()
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    foto = models.ImageField(
        upload_to=empleado_foto_path, 
        null=True, 
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    
    # Datos laborales
    fecha_ingreso = models.DateField()
    fecha_termino = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    tipo_contrato = models.CharField(max_length=20, choices=TIPO_CONTRATO_CHOICES)
    cargo = models.CharField(max_length=100)
    salario_base = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Relaciones
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    roles = models.ManyToManyField(Rol, blank=True)
    sucursales = models.ManyToManyField(Sucursal, blank=True)
    jefe_directo = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinados')
    
    # Metadatos
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    
    def esta_activo(self):
        return self.estado == 'activo'
    
    def dias_en_empresa(self):
        if self.fecha_termino and self.fecha_termino < timezone.now().date():
            return (self.fecha_termino - self.fecha_ingreso).days
        return (timezone.now().date() - self.fecha_ingreso).days
    
    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ['apellido', 'nombre']

class DocumentoEmpleado(models.Model):
    """Modelo para documentos relacionados con empleados"""
    TIPO_CHOICES = (
        ('contrato', 'Contrato'),
        ('identificacion', 'Identificación'),
        ('cv', 'Curriculum Vitae'),
        ('certificado', 'Certificado'),
        ('evaluacion', 'Evaluación'),
        ('otro', 'Otro'),
    )
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    nombre = models.CharField(max_length=100)
    archivo = models.FileField(
        upload_to=empleado_documento_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])]
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.empleado}"
    
    class Meta:
        verbose_name = "Documento de Empleado"
        verbose_name_plural = "Documentos de Empleados"
        ordering = ['-fecha_subida']

class Turno(models.Model):
    """Modelo para definir turnos de trabajo"""
    nombre = models.CharField(max_length=100)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    # Días de la semana como booleanos
    lunes = models.BooleanField(default=False)
    martes = models.BooleanField(default=False)
    miercoles = models.BooleanField(default=False)
    jueves = models.BooleanField(default=False)
    viernes = models.BooleanField(default=False)
    sabado = models.BooleanField(default=False)
    domingo = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.nombre} ({self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')})"
    
    def dias_semana_texto(self):
        dias = []
        if self.lunes: dias.append("Lun")
        if self.martes: dias.append("Mar")
        if self.miercoles: dias.append("Mié")
        if self.jueves: dias.append("Jue")
        if self.viernes: dias.append("Vie")
        if self.sabado: dias.append("Sáb")
        if self.domingo: dias.append("Dom")
        return ", ".join(dias)
    
    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        ordering = ['hora_inicio']

class AsignacionTurno(models.Model):
    """Modelo para asignar turnos a empleados"""
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='asignaciones_turno')
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    notas = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.empleado} - {self.turno} - {self.sucursal}"
    
    class Meta:
        verbose_name = "Asignación de Turno"
        verbose_name_plural = "Asignaciones de Turnos"
        ordering = ['-fecha_inicio']

class Asistencia(models.Model):
    """Modelo para registrar la asistencia de los empleados"""
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    hora_entrada = models.DateTimeField()
    hora_salida = models.DateTimeField(null=True, blank=True)
    turno = models.ForeignKey(Turno, on_delete=models.SET_NULL, null=True, blank=True)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.empleado} - {self.fecha.strftime('%Y-%m-%d')}"
    
    def horas_trabajadas(self):
        if not self.hora_salida:
            return None
        diferencia = self.hora_salida - self.hora_entrada
        return diferencia.total_seconds() / 3600  # Convertir a horas
    
    class Meta:
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        ordering = ['-fecha', '-hora_entrada']
        unique_together = [['empleado', 'fecha']]

class Capacitacion(models.Model):
    """Modelo para cursos y capacitaciones"""
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    duracion_horas = models.PositiveIntegerField()
    instructor = models.CharField(max_length=100, blank=True, null=True)
    material = models.FileField(upload_to='capacitaciones/', null=True, blank=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Capacitación"
        verbose_name_plural = "Capacitaciones"
        ordering = ['nombre']

class EmpleadoCapacitacion(models.Model):
    """Modelo para asignar capacitaciones a empleados"""
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En Curso'),
        ('completada', 'Completada'),
        ('reprobada', 'Reprobada'),
        ('cancelada', 'Cancelada'),
    )
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='capacitaciones')
    capacitacion = models.ForeignKey(Capacitacion, on_delete=models.CASCADE)
    fecha_asignacion = models.DateField(auto_now_add=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    calificacion = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    comentarios = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.empleado} - {self.capacitacion}"
    
    class Meta:
        verbose_name = "Empleado-Capacitación"
        verbose_name_plural = "Empleados-Capacitaciones"
        ordering = ['-fecha_asignacion']

class Evaluacion(models.Model):
    """Modelo para evaluaciones de desempeño"""
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='evaluaciones')
    evaluador = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, related_name='evaluaciones_realizadas')
    fecha = models.DateField()
    periodo_evaluado = models.CharField(max_length=100)  # Ej: "Primer Semestre 2025"
    puntuacion_general = models.DecimalField(max_digits=5, decimal_places=2)
    fortalezas = models.TextField(blank=True, null=True)
    areas_mejora = models.TextField(blank=True, null=True)
    comentarios = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.empleado} - {self.periodo_evaluado}"
    
    class Meta:
        verbose_name = "Evaluación"
        verbose_name_plural = "Evaluaciones"
        ordering = ['-fecha']

class Vacacion(models.Model):
    """Modelo para gestionar vacaciones y permisos"""
    TIPO_CHOICES = (
        ('vacaciones', 'Vacaciones'),
        ('permiso_sin_goce', 'Permiso sin Goce de Sueldo'),
        ('permiso_con_goce', 'Permiso con Goce de Sueldo'),
        ('licencia_medica', 'Licencia Médica'),
        ('otro', 'Otro'),
    )
    
    ESTADO_CHOICES = (
        ('solicitada', 'Solicitada'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('cancelada', 'Cancelada'),
    )
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='vacaciones')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_habiles = models.PositiveIntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='solicitada')
    aprobada_por = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True, related_name='vacaciones_aprobadas')
    fecha_solicitud = models.DateField(auto_now_add=True)
    fecha_aprobacion = models.DateField(null=True, blank=True)
    motivo = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.empleado} - {self.get_tipo_display()} ({self.fecha_inicio} a {self.fecha_fin})"
    
    def dias_totales(self):
        return (self.fecha_fin - self.fecha_inicio).days + 1
    
    class Meta:
        verbose_name = "Vacación o Permiso"
        verbose_name_plural = "Vacaciones y Permisos"
        ordering = ['-fecha_inicio']

class Nomina(models.Model):
    """Modelo para nóminas de pago"""
    ESTADO_CHOICES = (
        ('borrador', 'Borrador'),
        ('pendiente', 'Pendiente de Aprobación'),
        ('aprobada', 'Aprobada'),
        ('pagada', 'Pagada'),
        ('cancelada', 'Cancelada'),
    )
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='nominas')
    periodo = models.CharField(max_length=50)  # Ej: "Julio 2025"
    fecha_calculo = models.DateField(auto_now_add=True)
    fecha_pago = models.DateField(null=True, blank=True)
    
    # Montos
    salario_base = models.DecimalField(max_digits=10, decimal_places=2)
    horas_extra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonificaciones = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comisiones = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deducciones = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_bruto = models.DecimalField(max_digits=10, decimal_places=2)
    total_neto = models.DecimalField(max_digits=10, decimal_places=2)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    aprobada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='nominas_aprobadas')
    observaciones = models.TextField(blank=True, null=True)
    recibo_pdf = models.FileField(upload_to='recibos_nomina/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.empleado} - {self.periodo}"
    
    class Meta:
        verbose_name = "Nómina"
        verbose_name_plural = "Nóminas"
        ordering = ['-fecha_calculo']
        unique_together = [['empleado', 'periodo']]

class Notificacion(models.Model):
    """Modelo para gestionar notificaciones del sistema RRHH"""
    TIPO_CHOICES = (
        ('contrato', 'Vencimiento de Contrato'),
        ('evaluacion', 'Evaluación Pendiente'),
        ('capacitacion', 'Capacitación Programada'),
        ('vacaciones', 'Solicitud de Vacaciones'),
        ('asistencia', 'Problema de Asistencia'),
        ('otro', 'Otro'),
    )
    
    PRIORIDAD_CHOICES = (
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    )
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='notificaciones', null=True, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones_rrhh')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    leida = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.titulo} - {self.get_tipo_display()}"
    
    def marcar_como_leida(self):
        self.leida = True
        self.fecha_lectura = timezone.now()
        self.save()
    
    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha_creacion']
