# Generated by Django 5.2.4 on 2025-07-17 17:08

import django.core.validators
import django.db.models.deletion
import rrhh.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Capacitacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField()),
                ('duracion_horas', models.PositiveIntegerField()),
                ('instructor', models.CharField(blank=True, max_length=100, null=True)),
                ('material', models.FileField(blank=True, null=True, upload_to='capacitaciones/')),
            ],
            options={
                'verbose_name': 'Capacitación',
                'verbose_name_plural': 'Capacitaciones',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Rol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('permisos', models.JSONField(default=dict)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('actualizado', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Rol',
                'verbose_name_plural': 'Roles',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('hora_inicio', models.TimeField()),
                ('hora_fin', models.TimeField()),
                ('lunes', models.BooleanField(default=False)),
                ('martes', models.BooleanField(default=False)),
                ('miercoles', models.BooleanField(default=False)),
                ('jueves', models.BooleanField(default=False)),
                ('viernes', models.BooleanField(default=False)),
                ('sabado', models.BooleanField(default=False)),
                ('domingo', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Turno',
                'verbose_name_plural': 'Turnos',
                'ordering': ['hora_inicio'],
            },
        ),
        migrations.CreateModel(
            name='Empleado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('apellido', models.CharField(max_length=100)),
                ('rut', models.CharField(max_length=15, unique=True)),
                ('fecha_nacimiento', models.DateField()),
                ('direccion', models.CharField(max_length=200)),
                ('telefono', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('foto', models.ImageField(blank=True, null=True, upload_to=rrhh.models.empleado_foto_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])),
                ('fecha_ingreso', models.DateField()),
                ('fecha_termino', models.DateField(blank=True, null=True)),
                ('estado', models.CharField(choices=[('activo', 'Activo'), ('inactivo', 'Inactivo'), ('vacaciones', 'De Vacaciones'), ('permiso', 'De Permiso')], default='activo', max_length=20)),
                ('tipo_contrato', models.CharField(choices=[('indefinido', 'Indefinido'), ('plazo_fijo', 'Plazo Fijo'), ('por_obra', 'Por Obra o Faena'), ('part_time', 'Part Time')], max_length=20)),
                ('cargo', models.CharField(max_length=100)),
                ('salario_base', models.DecimalField(decimal_places=2, max_digits=10)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('actualizado', models.DateTimeField(auto_now=True)),
                ('jefe_directo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subordinados', to='rrhh.empleado')),
                ('sucursales', models.ManyToManyField(blank=True, to='accounts.sucursal')),
                ('usuario', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('roles', models.ManyToManyField(blank=True, to='rrhh.rol')),
            ],
            options={
                'verbose_name': 'Empleado',
                'verbose_name_plural': 'Empleados',
                'ordering': ['apellido', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='DocumentoEmpleado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('contrato', 'Contrato'), ('identificacion', 'Identificación'), ('cv', 'Curriculum Vitae'), ('certificado', 'Certificado'), ('evaluacion', 'Evaluación'), ('otro', 'Otro')], max_length=20)),
                ('nombre', models.CharField(max_length=100)),
                ('archivo', models.FileField(upload_to=rrhh.models.empleado_documento_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])])),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos', to='rrhh.empleado')),
            ],
            options={
                'verbose_name': 'Documento de Empleado',
                'verbose_name_plural': 'Documentos de Empleados',
                'ordering': ['-fecha_subida'],
            },
        ),
        migrations.CreateModel(
            name='EmpleadoCapacitacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_asignacion', models.DateField(auto_now_add=True)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField(blank=True, null=True)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('en_curso', 'En Curso'), ('completada', 'Completada'), ('reprobada', 'Reprobada'), ('cancelada', 'Cancelada')], default='pendiente', max_length=20)),
                ('calificacion', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('comentarios', models.TextField(blank=True, null=True)),
                ('capacitacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rrhh.capacitacion')),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='capacitaciones', to='rrhh.empleado')),
            ],
            options={
                'verbose_name': 'Empleado-Capacitación',
                'verbose_name_plural': 'Empleados-Capacitaciones',
                'ordering': ['-fecha_asignacion'],
            },
        ),
        migrations.CreateModel(
            name='Evaluacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('periodo_evaluado', models.CharField(max_length=100)),
                ('puntuacion_general', models.DecimalField(decimal_places=2, max_digits=5)),
                ('fortalezas', models.TextField(blank=True, null=True)),
                ('areas_mejora', models.TextField(blank=True, null=True)),
                ('comentarios', models.TextField(blank=True, null=True)),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluaciones', to='rrhh.empleado')),
                ('evaluador', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='evaluaciones_realizadas', to='rrhh.empleado')),
            ],
            options={
                'verbose_name': 'Evaluación',
                'verbose_name_plural': 'Evaluaciones',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('contrato', 'Vencimiento de Contrato'), ('evaluacion', 'Evaluación Pendiente'), ('capacitacion', 'Capacitación Programada'), ('vacaciones', 'Solicitud de Vacaciones'), ('asistencia', 'Problema de Asistencia'), ('otro', 'Otro')], max_length=20)),
                ('titulo', models.CharField(max_length=200)),
                ('mensaje', models.TextField()),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_lectura', models.DateTimeField(blank=True, null=True)),
                ('prioridad', models.CharField(choices=[('baja', 'Baja'), ('media', 'Media'), ('alta', 'Alta'), ('urgente', 'Urgente')], default='media', max_length=10)),
                ('leida', models.BooleanField(default=False)),
                ('empleado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notificaciones', to='rrhh.empleado')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificaciones_rrhh', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notificación',
                'verbose_name_plural': 'Notificaciones',
                'ordering': ['-fecha_creacion'],
            },
        ),
        migrations.CreateModel(
            name='AsignacionTurno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField(blank=True, null=True)),
                ('notas', models.TextField(blank=True, null=True)),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.sucursal')),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asignaciones_turno', to='rrhh.empleado')),
                ('turno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rrhh.turno')),
            ],
            options={
                'verbose_name': 'Asignación de Turno',
                'verbose_name_plural': 'Asignaciones de Turnos',
                'ordering': ['-fecha_inicio'],
            },
        ),
        migrations.CreateModel(
            name='Vacacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('vacaciones', 'Vacaciones'), ('permiso_sin_goce', 'Permiso sin Goce de Sueldo'), ('permiso_con_goce', 'Permiso con Goce de Sueldo'), ('licencia_medica', 'Licencia Médica'), ('otro', 'Otro')], max_length=20)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('dias_habiles', models.PositiveIntegerField()),
                ('estado', models.CharField(choices=[('solicitada', 'Solicitada'), ('aprobada', 'Aprobada'), ('rechazada', 'Rechazada'), ('cancelada', 'Cancelada')], default='solicitada', max_length=20)),
                ('fecha_solicitud', models.DateField(auto_now_add=True)),
                ('fecha_aprobacion', models.DateField(blank=True, null=True)),
                ('motivo', models.TextField(blank=True, null=True)),
                ('aprobada_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vacaciones_aprobadas', to='rrhh.empleado')),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vacaciones', to='rrhh.empleado')),
            ],
            options={
                'verbose_name': 'Vacación o Permiso',
                'verbose_name_plural': 'Vacaciones y Permisos',
                'ordering': ['-fecha_inicio'],
            },
        ),
        migrations.CreateModel(
            name='Nomina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('periodo', models.CharField(max_length=50)),
                ('fecha_calculo', models.DateField(auto_now_add=True)),
                ('fecha_pago', models.DateField(blank=True, null=True)),
                ('salario_base', models.DecimalField(decimal_places=2, max_digits=10)),
                ('horas_extra', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('bonificaciones', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('comisiones', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('deducciones', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_bruto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_neto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('estado', models.CharField(choices=[('borrador', 'Borrador'), ('pendiente', 'Pendiente de Aprobación'), ('aprobada', 'Aprobada'), ('pagada', 'Pagada'), ('cancelada', 'Cancelada')], default='borrador', max_length=20)),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('recibo_pdf', models.FileField(blank=True, null=True, upload_to='recibos_nomina/')),
                ('aprobada_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nominas_aprobadas', to=settings.AUTH_USER_MODEL)),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nominas', to='rrhh.empleado')),
            ],
            options={
                'verbose_name': 'Nómina',
                'verbose_name_plural': 'Nóminas',
                'ordering': ['-fecha_calculo'],
                'unique_together': {('empleado', 'periodo')},
            },
        ),
        migrations.CreateModel(
            name='Asistencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('hora_entrada', models.DateTimeField()),
                ('hora_salida', models.DateTimeField(blank=True, null=True)),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.sucursal')),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asistencias', to='rrhh.empleado')),
                ('turno', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rrhh.turno')),
            ],
            options={
                'verbose_name': 'Asistencia',
                'verbose_name_plural': 'Asistencias',
                'ordering': ['-fecha', '-hora_entrada'],
                'unique_together': {('empleado', 'fecha')},
            },
        ),
    ]
