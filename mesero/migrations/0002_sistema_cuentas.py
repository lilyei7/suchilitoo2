
# Migración para agregar campos de cuenta
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('mesero', '0001_initial'),  # Ajustar según la última migración
    ]

    operations = [
        migrations.AddField(
            model_name='orden',
            name='cuenta_solicitada',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orden',
            name='fecha_solicitud_cuenta',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orden',
            name='usuario_solicita_cuenta',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cuentas_solicitadas', to='accounts.usuario'),
        ),
        migrations.AddField(
            model_name='orden',
            name='cuenta_procesada',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orden',
            name='fecha_procesamiento_cuenta',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orden',
            name='cajero_procesa_cuenta',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cuentas_procesadas', to='accounts.usuario'),
        ),
        migrations.AddField(
            model_name='orden',
            name='metodo_pago_cuenta',
            field=models.CharField(blank=True, choices=[('efectivo', 'Efectivo'), ('tarjeta', 'Tarjeta'), ('transferencia', 'Transferencia')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='orden',
            name='monto_recibido',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='orden',
            name='cambio_dado',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='orden',
            name='referencia_pago',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='orden',
            name='ticket_generado',
            field=models.BooleanField(default=False),
        ),
    ]
