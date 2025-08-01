# Generated by Django 5.2.3 on 2025-07-02 22:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('restaurant', '0003_merge_20250701_1556'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Mesa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=10, unique=True)),
                ('capacidad', models.IntegerField(default=4)),
                ('estado', models.CharField(choices=[('disponible', 'Disponible'), ('ocupada', 'Ocupada'), ('reservada', 'Reservada'), ('limpieza', 'En Limpieza'), ('mantenimiento', 'Mantenimiento')], default='disponible', max_length=20)),
                ('ubicacion', models.CharField(blank=True, help_text='Ej: Terraza, Salón principal, VIP', max_length=100, null=True)),
                ('activa', models.BooleanField(default=True)),
                ('notas', models.TextField(blank=True, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mesas_mesero', to='accounts.sucursal')),
            ],
            options={
                'verbose_name': 'Mesa',
                'verbose_name_plural': 'Mesas',
                'ordering': ['numero'],
            },
        ),
        migrations.CreateModel(
            name='HistorialMesa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado_anterior', models.CharField(max_length=20)),
                ('estado_nuevo', models.CharField(max_length=20)),
                ('motivo', models.TextField(blank=True, null=True)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('mesa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial', to='mesero.mesa')),
            ],
            options={
                'verbose_name': 'Historial de mesa',
                'verbose_name_plural': 'Historiales de mesas',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='Orden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_orden', models.CharField(max_length=20, unique=True)),
                ('cliente_nombre', models.CharField(blank=True, max_length=200, null=True)),
                ('cliente_telefono', models.CharField(blank=True, max_length=20, null=True)),
                ('tipo_servicio', models.CharField(choices=[('mesa', 'En Mesa'), ('llevar', 'Para Llevar'), ('delivery', 'Delivery')], default='mesa', max_length=20)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('confirmada', 'Confirmada'), ('en_preparacion', 'En Preparación'), ('lista', 'Lista'), ('entregada', 'Entregada'), ('cancelada', 'Cancelada'), ('cerrada', 'Cerrada')], default='pendiente', max_length=20)),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('impuesto', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('descuento', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('notas_cocina', models.TextField(blank=True, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_confirmacion', models.DateTimeField(blank=True, null=True)),
                ('fecha_preparacion', models.DateTimeField(blank=True, null=True)),
                ('fecha_lista', models.DateTimeField(blank=True, null=True)),
                ('fecha_entrega', models.DateTimeField(blank=True, null=True)),
                ('fecha_cierre', models.DateTimeField(blank=True, null=True)),
                ('mesa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordenes_mesero', to='mesero.mesa')),
                ('mesero', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordenes_mesero_atendidas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Orden',
                'verbose_name_plural': 'Órdenes',
                'ordering': ['-fecha_creacion'],
            },
        ),
        migrations.CreateModel(
            name='HistorialOrden',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado_anterior', models.CharField(max_length=20)),
                ('estado_nuevo', models.CharField(max_length=20)),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('orden', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial', to='mesero.orden')),
            ],
            options={
                'verbose_name': 'Historial de orden',
                'verbose_name_plural': 'Historiales de órdenes',
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='OrdenItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField(default=1)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('descuento_item', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('en_preparacion', 'En Preparación'), ('listo', 'Listo'), ('entregado', 'Entregado'), ('cancelado', 'Cancelado')], default='pendiente', max_length=20)),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('orden', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='mesero.orden')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='restaurant.productoventa')),
            ],
            options={
                'verbose_name': 'Item de orden',
                'verbose_name_plural': 'Items de órdenes',
            },
        ),
    ]
