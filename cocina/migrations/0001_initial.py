# Generated by Django 5.2.3 on 2025-07-05 15:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mesero', '0006_ordenitem_subtotal'),
        ('restaurant', '0003_merge_20250701_1556'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EstadoCocina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(choices=[('recibida', 'Recibida'), ('en_preparacion', 'En Preparación'), ('lista', 'Lista'), ('entregada', 'Entregada'), ('cancelada', 'Cancelada')], max_length=50, unique=True)),
                ('descripcion', models.TextField(blank=True)),
                ('color', models.CharField(default='#6c757d', help_text='Color hexadecimal para la interfaz', max_length=7)),
                ('orden', models.IntegerField(default=0, help_text='Orden de visualización')),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Estado de cocina',
                'verbose_name_plural': 'Estados de cocina',
                'ordering': ['orden', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='ItemCocina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado_cocina', models.CharField(choices=[('recibida', 'Recibida'), ('en_preparacion', 'En Preparación'), ('lista', 'Lista'), ('entregada', 'Entregada'), ('cancelada', 'Cancelada')], default='recibida', max_length=20)),
                ('tiempo_inicio', models.DateTimeField(blank=True, null=True)),
                ('tiempo_finalizacion', models.DateTimeField(blank=True, null=True)),
                ('notas_preparacion', models.TextField(blank=True)),
                ('cocinero_responsable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items_cocina_responsables', to=settings.AUTH_USER_MODEL)),
                ('orden_item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cocina_info', to='mesero.ordenitem')),
            ],
            options={
                'verbose_name': 'Item de cocina',
                'verbose_name_plural': 'Items de cocina',
            },
        ),
        migrations.CreateModel(
            name='LogCocina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accion', models.CharField(choices=[('orden_recibida', 'Orden Recibida'), ('preparacion_iniciada', 'Preparación Iniciada'), ('item_completado', 'Item Completado'), ('orden_completada', 'Orden Completada'), ('orden_cancelada', 'Orden Cancelada'), ('cambio_estado', 'Cambio de Estado'), ('asignacion_cocinero', 'Asignación de Cocinero')], max_length=30)),
                ('descripcion', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mesero.ordenitem')),
                ('orden', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs_cocina', to='mesero.orden')),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Log de cocina',
                'verbose_name_plural': 'Logs de cocina',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='OrdenCocina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prioridad', models.IntegerField(default=0, help_text='0=Normal, 1=Alta, 2=Urgente')),
                ('tiempo_estimado_total', models.IntegerField(default=0, help_text='Tiempo estimado total en minutos')),
                ('fecha_inicio_preparacion', models.DateTimeField(blank=True, null=True)),
                ('fecha_finalizacion', models.DateTimeField(blank=True, null=True)),
                ('notas_cocina', models.TextField(blank=True, help_text='Notas específicas para cocina')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('cocinero_asignado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordenes_cocina_asignadas', to=settings.AUTH_USER_MODEL)),
                ('orden', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cocina_info', to='mesero.orden')),
            ],
            options={
                'verbose_name': 'Orden de cocina',
                'verbose_name_plural': 'Órdenes de cocina',
                'ordering': ['-prioridad', 'fecha_creacion'],
            },
        ),
        migrations.CreateModel(
            name='TiempoPreparacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tiempo_estimado', models.IntegerField(help_text='Tiempo estimado en minutos')),
                ('tiempo_promedio', models.FloatField(default=0, help_text='Tiempo promedio real en minutos')),
                ('cantidad_preparaciones', models.IntegerField(default=0)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant.productoventa')),
            ],
            options={
                'verbose_name': 'Tiempo de preparación',
                'verbose_name_plural': 'Tiempos de preparación',
            },
        ),
    ]
