# Generated by Django 5.2.4 on 2025-07-16 16:36

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('dashboard', '0008_fix_migration_chain'),
        ('restaurant', '0005_configuracionsistema'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChecklistCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre')),
                ('order', models.IntegerField(default=0, verbose_name='Orden')),
                ('active', models.BooleanField(default=True, verbose_name='Activo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')),
            ],
            options={
                'verbose_name': 'Categoría de Checklist',
                'verbose_name_plural': 'Categorías de Checklist',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('telefono', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('direccion', models.TextField(blank=True, null=True)),
                ('notas', models.TextField(blank=True, null=True)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('ultima_visita', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='CajaApertura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora', models.DateTimeField(auto_now_add=True)),
                ('monto_inicial', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('notas', models.TextField(blank=True, null=True)),
                ('cerrada', models.BooleanField(default=False)),
                ('cajero', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='aperturas_caja', to=settings.AUTH_USER_MODEL)),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aperturas_caja', to='accounts.sucursal')),
            ],
            options={
                'verbose_name': 'Apertura de caja',
                'verbose_name_plural': 'Aperturas de caja',
                'ordering': ['-fecha_hora'],
            },
        ),
        migrations.CreateModel(
            name='CajaCierre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora', models.DateTimeField(auto_now_add=True)),
                ('monto_sistema', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('monto_fisico', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('diferencia', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('ventas_efectivo', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('ventas_tarjeta', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('ventas_otros', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_ventas', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('notas', models.TextField(blank=True, null=True)),
                ('apertura', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='cierre', to='dashboard.cajaapertura')),
            ],
            options={
                'verbose_name': 'Cierre de caja',
                'verbose_name_plural': 'Cierres de caja',
                'ordering': ['-fecha_hora'],
            },
        ),
        migrations.CreateModel(
            name='ChecklistTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
                ('requires_evidence', models.BooleanField(default=False, verbose_name='Requiere evidencia')),
                ('active', models.BooleanField(default=True, verbose_name='Activo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='dashboard.checklistcategory', verbose_name='Categoría')),
                ('default_role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.rol', verbose_name='Rol predeterminado')),
            ],
            options={
                'verbose_name': 'Tarea de Checklist',
                'verbose_name_plural': 'Tareas de Checklist',
                'ordering': ['category__order', 'title'],
            },
        ),
        migrations.CreateModel(
            name='CroquisLayout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('layout_data', models.JSONField(help_text='Datos del layout en formato JSON')),
                ('version', models.CharField(default='1.0', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sucursal', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='croquis_layout', to='accounts.sucursal')),
            ],
            options={
                'verbose_name': 'Layout de Croquis',
                'verbose_name_plural': 'Layouts de Croquis',
                'db_table': 'dashboard_croquis_layout',
            },
        ),
        migrations.CreateModel(
            name='HistorialPrecios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_compra', models.DateTimeField(default=django.utils.timezone.now)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cantidad_comprada', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cantidad_restante', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('creado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='historial_precios_creados', to=settings.AUTH_USER_MODEL)),
                ('insumo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial_precios', to='restaurant.insumo')),
                ('movimiento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='historial_precios', to='restaurant.movimientoinventario')),
                ('sucursal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.sucursal')),
            ],
            options={
                'verbose_name': 'Historial de Precios',
                'verbose_name_plural': 'Historial de Precios',
                'ordering': ['insumo', 'fecha_compra'],
            },
        ),
        migrations.CreateModel(
            name='IncidentReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('mobiliario', 'Mobiliario'), ('equipo', 'Equipo'), ('instalaciones', 'Instalaciones'), ('seguridad', 'Seguridad'), ('servicio', 'Servicio'), ('personal', 'Personal'), ('otro', 'Otro')], max_length=20, verbose_name='Categoría')),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('description', models.TextField(verbose_name='Descripción')),
                ('urgency', models.CharField(choices=[('baja', 'Baja'), ('media', 'Media'), ('alta', 'Alta'), ('critica', 'Crítica')], default='media', max_length=10, verbose_name='Nivel de Urgencia')),
                ('status', models.CharField(choices=[('abierto', 'Abierto'), ('en_proceso', 'En proceso'), ('cerrado', 'Cerrado')], default='abierto', max_length=15, verbose_name='Estado')),
                ('resolution_note', models.TextField(blank=True, verbose_name='Nota de resolución')),
                ('reported_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de reporte')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')),
                ('resolved_at', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de resolución')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_incidents', to=settings.AUTH_USER_MODEL, verbose_name='Asignado a')),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incidents', to='accounts.sucursal', verbose_name='Sucursal')),
                ('reported_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reported_incidents', to=settings.AUTH_USER_MODEL, verbose_name='Reportado por')),
            ],
            options={
                'verbose_name': 'Reporte de Incidente',
                'verbose_name_plural': 'Reportes de Incidentes',
                'ordering': ['-reported_at'],
            },
        ),
        migrations.CreateModel(
            name='IncidentHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('creado', 'Creado'), ('cambio_estado', 'Cambio de Estado'), ('reasignado', 'Reasignado'), ('cerrado', 'Cerrado'), ('evidencia_agregada', 'Evidencia Agregada'), ('comentario', 'Comentario')], max_length=20, verbose_name='Tipo de acción')),
                ('description', models.TextField(verbose_name='Descripción')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora')),
                ('action_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incident_actions', to=settings.AUTH_USER_MODEL, verbose_name='Realizado por')),
                ('incident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='dashboard.incidentreport', verbose_name='Incidente')),
            ],
            options={
                'verbose_name': 'Historial de Incidente',
                'verbose_name_plural': 'Historial de Incidentes',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='IncidentEvidence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='checklist/incidents/%Y/%m/%d/', verbose_name='Archivo')),
                ('comment', models.TextField(blank=True, verbose_name='Comentario')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de subida')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_incident_evidence', to=settings.AUTH_USER_MODEL, verbose_name='Subido por')),
                ('incident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evidence_files', to='dashboard.incidentreport', verbose_name='Reporte de incidente')),
            ],
            options={
                'verbose_name': 'Evidencia de Incidente',
                'verbose_name_plural': 'Evidencias de Incidentes',
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='IncidentComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Comentario')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incident_comments', to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
                ('incident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='dashboard.incidentreport', verbose_name='Incidente')),
            ],
            options={
                'verbose_name': 'Comentario de Incidente',
                'verbose_name_plural': 'Comentarios de Incidentes',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Mesa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=10)),
                ('nombre', models.CharField(blank=True, max_length=50, null=True)),
                ('capacidad', models.IntegerField(default=4)),
                ('estado', models.CharField(choices=[('disponible', 'Disponible'), ('ocupada', 'Ocupada'), ('reservada', 'Reservada'), ('mantenimiento', 'En Mantenimiento')], default='disponible', max_length=20)),
                ('codigo_qr', models.CharField(blank=True, max_length=100, null=True)),
                ('activa', models.BooleanField(default=True)),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mesas', to='accounts.sucursal')),
            ],
            options={
                'verbose_name': 'Mesa',
                'verbose_name_plural': 'Mesas',
                'ordering': ['sucursal', 'numero'],
                'unique_together': {('numero', 'sucursal')},
            },
        ),
        migrations.CreateModel(
            name='Orden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=20, unique=True)),
                ('fecha_hora', models.DateTimeField(auto_now_add=True)),
                ('tipo', models.CharField(choices=[('mesa', 'Para Mesa'), ('llevar', 'Para Llevar'), ('delivery', 'Delivery')], default='mesa', max_length=20)),
                ('estado', models.CharField(choices=[('abierta', 'Abierta'), ('en_proceso', 'En Proceso'), ('lista', 'Lista para Entrega'), ('entregada', 'Entregada'), ('cancelada', 'Cancelada'), ('cerrada', 'Cerrada')], default='abierta', max_length=20)),
                ('notas', models.TextField(blank=True, null=True)),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('descuento', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('impuestos', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('pagada', models.BooleanField(default=False)),
                ('cajero', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordenes_creadas', to=settings.AUTH_USER_MODEL)),
                ('cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordenes', to='dashboard.cliente')),
                ('mesa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordenes', to='dashboard.mesa')),
                ('mesero', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordenes_atendidas', to=settings.AUTH_USER_MODEL)),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordenes', to='accounts.sucursal')),
            ],
            options={
                'verbose_name': 'Orden',
                'verbose_name_plural': 'Órdenes',
                'ordering': ['-fecha_hora'],
            },
        ),
        migrations.CreateModel(
            name='OrdenItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precio_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('costo_unitario', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('costo_total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('notas', models.TextField(blank=True, null=True)),
                ('estado', models.CharField(default='pendiente', max_length=20)),
                ('orden', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='dashboard.orden')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items_orden', to='restaurant.productoventa')),
            ],
            options={
                'verbose_name': 'Item de orden',
                'verbose_name_plural': 'Items de orden',
            },
        ),
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_comercial', models.CharField(default='Sin nombre', max_length=200, verbose_name='Nombre comercial')),
                ('razon_social', models.CharField(blank=True, max_length=200, verbose_name='Razón social')),
                ('rfc', models.CharField(blank=True, max_length=13, verbose_name='RFC')),
                ('persona_contacto', models.CharField(blank=True, max_length=200, verbose_name='Persona de contacto')),
                ('telefono', models.CharField(blank=True, max_length=20, verbose_name='Teléfono')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('forma_pago_preferida', models.CharField(choices=[('efectivo', 'Efectivo'), ('transferencia', 'Transferencia'), ('cheque', 'Cheque'), ('credito', 'Crédito'), ('tarjeta', 'Tarjeta')], default='transferencia', max_length=20, verbose_name='Forma de pago preferida')),
                ('dias_credito', models.IntegerField(default=0, verbose_name='Días de crédito')),
                ('direccion', models.TextField(blank=True, verbose_name='Dirección')),
                ('ciudad_estado', models.CharField(blank=True, max_length=200, verbose_name='Ciudad/Estado')),
                ('categoria_productos', models.CharField(choices=[('ingredientes', 'Ingredientes'), ('bebidas', 'Bebidas'), ('utensilios', 'Utensilios'), ('empaque', 'Empaque'), ('limpieza', 'Limpieza'), ('equipos', 'Equipos')], default='ingredientes', max_length=20, verbose_name='Categoría de productos')),
                ('notas_adicionales', models.TextField(blank=True, verbose_name='Notas adicionales')),
                ('estado', models.CharField(choices=[('activo', 'Activo'), ('inactivo', 'Inactivo'), ('pendiente', 'Pendiente')], default='activo', max_length=10)),
                ('fecha_registro', models.DateTimeField(default=django.utils.timezone.now)),
                ('nombre', models.CharField(editable=False, max_length=200)),
                ('contacto', models.CharField(blank=True, editable=False, max_length=200)),
                ('categoria', models.CharField(choices=[('ingredientes', 'Ingredientes'), ('bebidas', 'Bebidas'), ('utensilios', 'Utensilios'), ('empaque', 'Empaque'), ('limpieza', 'Limpieza'), ('equipos', 'Equipos')], default='ingredientes', editable=False, max_length=20)),
                ('notas', models.TextField(blank=True, editable=False)),
                ('creado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='proveedores_creados', to=settings.AUTH_USER_MODEL, verbose_name='Creado por')),
                ('sucursal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='proveedores', to='accounts.sucursal', verbose_name='Sucursal')),
            ],
            options={
                'verbose_name': 'Proveedor',
                'verbose_name_plural': 'Proveedores',
            },
        ),
        migrations.CreateModel(
            name='TaskInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Fecha')),
                ('shift', models.CharField(choices=[('mañana', 'Mañana'), ('tarde', 'Tarde'), ('noche', 'Noche')], max_length=10, verbose_name='Turno')),
                ('status', models.CharField(choices=[('pendiente', 'Pendiente'), ('completado', 'Completado')], default='pendiente', max_length=10, verbose_name='Estado')),
                ('performed_at', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de realización')),
                ('verified', models.BooleanField(default=False, verbose_name='Verificado')),
                ('verified_at', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de verificación')),
                ('verification_notes', models.TextField(blank=True, verbose_name='Notas de verificación')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_instances', to='accounts.sucursal', verbose_name='Sucursal')),
                ('performed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='completed_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Realizado por')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instances', to='dashboard.checklisttask', verbose_name='Tarea')),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_tasks', to=settings.AUTH_USER_MODEL, verbose_name='Verificado por')),
            ],
            options={
                'verbose_name': 'Instancia de Tarea',
                'verbose_name_plural': 'Instancias de Tareas',
                'ordering': ['-date', 'shift', 'task__category__order', 'task__title'],
                'unique_together': {('task', 'branch', 'date', 'shift')},
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('task_created', 'Tarea creada'), ('task_completed', 'Tarea completada'), ('evidence_uploaded', 'Evidencia subida'), ('incident_reported', 'Incidente reportado'), ('incident_updated', 'Incidente actualizado'), ('incident_resolved', 'Incidente resuelto')], max_length=20, verbose_name='Tipo')),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('message', models.TextField(verbose_name='Mensaje')),
                ('read', models.BooleanField(default=False, verbose_name='Leído')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('alert_type', models.CharField(blank=True, choices=[('primary', 'Informativa'), ('success', 'Éxito'), ('warning', 'Advertencia'), ('danger', 'Error'), ('info', 'Información'), ('secondary', 'Secundaria')], default='info', max_length=20, null=True, verbose_name='Tipo de alerta')),
                ('icon', models.CharField(blank=True, choices=[('info-circle', 'Información'), ('check-circle', 'Completado'), ('exclamation-triangle', 'Advertencia'), ('exclamation-circle', 'Error'), ('bell', 'Notificación'), ('tools', 'Mantenimiento'), ('clipboard-check', 'Checklist'), ('tasks', 'Tareas'), ('camera', 'Evidencia'), ('bug', 'Incidente')], default='info-circle', max_length=30, null=True, verbose_name='Ícono')),
                ('link', models.CharField(blank=True, max_length=255, null=True, verbose_name='Enlace')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='Destinatario')),
                ('related_incident', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='dashboard.incidentreport', verbose_name='Incidente relacionado')),
                ('related_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='dashboard.taskinstance', verbose_name='Tarea relacionada')),
            ],
            options={
                'verbose_name': 'Notificación',
                'verbose_name_plural': 'Notificaciones',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Evidence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='checklist/evidence/%Y/%m/%d/', verbose_name='Archivo')),
                ('comment', models.TextField(blank=True, verbose_name='Comentario')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de subida')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_evidence', to=settings.AUTH_USER_MODEL, verbose_name='Subido por')),
                ('instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evidence_files', to='dashboard.taskinstance', verbose_name='Instancia de tarea')),
            ],
            options={
                'verbose_name': 'Evidencia',
                'verbose_name_plural': 'Evidencias',
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_factura', models.CharField(blank=True, max_length=50, null=True)),
                ('fecha_hora', models.DateTimeField(auto_now_add=True)),
                ('metodo_pago', models.CharField(choices=[('efectivo', 'Efectivo'), ('tarjeta', 'Tarjeta'), ('transferencia', 'Transferencia'), ('credito', 'Crédito'), ('mixto', 'Pago Mixto')], default='efectivo', max_length=20)),
                ('monto_recibido', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cambio', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('descuento', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('impuestos', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('anulada', models.BooleanField(default=False)),
                ('motivo_anulacion', models.TextField(blank=True, null=True)),
                ('cajero', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ventas_realizadas', to=settings.AUTH_USER_MODEL)),
                ('cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='compras', to='dashboard.cliente')),
                ('orden', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='venta', to='dashboard.orden')),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ventas', to='accounts.sucursal')),
            ],
            options={
                'verbose_name': 'Venta',
                'verbose_name_plural': 'Ventas',
                'ordering': ['-fecha_hora'],
            },
        ),
        migrations.CreateModel(
            name='DetalleVenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precio_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('costo_unitario', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('costo_total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('descuento', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ventas', to='restaurant.productoventa')),
                ('venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='dashboard.venta')),
            ],
            options={
                'verbose_name': 'Detalle de venta',
                'verbose_name_plural': 'Detalles de venta',
            },
        ),
        migrations.CreateModel(
            name='ProveedorInsumo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio por unidad')),
                ('precio_descuento', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Precio con descuento')),
                ('cantidad_minima', models.DecimalField(decimal_places=2, default=1, max_digits=10, verbose_name='Cantidad mínima de compra')),
                ('tiempo_entrega_dias', models.IntegerField(default=1, verbose_name='Tiempo de entrega (días)')),
                ('activo', models.BooleanField(default=True, verbose_name='Disponible')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('notas', models.TextField(blank=True, verbose_name='Notas específicas')),
                ('insumo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proveedores_insumo', to='restaurant.insumo')),
                ('proveedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='insumos_proveedor', to='dashboard.proveedor')),
            ],
            options={
                'verbose_name': 'Insumo por Proveedor',
                'verbose_name_plural': 'Insumos por Proveedor',
                'ordering': ['proveedor', 'insumo__categoria', 'insumo__nombre'],
                'unique_together': {('proveedor', 'insumo')},
            },
        ),
    ]
