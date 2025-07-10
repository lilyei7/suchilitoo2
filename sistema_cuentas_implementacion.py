#!/usr/bin/env python
"""
Sistema de Cuentas - Implementación Completa
=============================================

Este script implementa el sistema de cuentas que conecta meseros y cajeros:
1. Cajero puede crear pedidos como mesero
2. Mesero puede solicitar cuenta a cajero
3. Cajero recibe notificaciones y procesa pagos
4. Flujo completo de efectivo y tarjeta
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.db import transaction
from django.utils import timezone
from datetime import datetime
from decimal import Decimal

# Importar modelos
from mesero.models import Orden, OrdenItem, Mesa
from accounts.models import Usuario, Sucursal
from restaurant.models import ProductoVenta

print("🚀 INICIANDO IMPLEMENTACIÓN DEL SISTEMA DE CUENTAS")
print("=" * 60)

def agregar_campos_cuenta():
    """Agregar campos necesarios para el sistema de cuentas"""
    print("\n📋 PASO 1: Agregando campos para sistema de cuentas")
    
    # Verificar si ya existen los campos necesarios
    from django.db import connection
    with connection.cursor() as cursor:
        # Verificar campos en la tabla de órdenes
        cursor.execute("PRAGMA table_info(mesero_orden)")
        columns = [column[1] for column in cursor.fetchall()]
        
        campos_necesarios = [
            'cuenta_solicitada',
            'fecha_solicitud_cuenta',
            'usuario_solicita_cuenta',
            'cuenta_procesada',
            'fecha_procesamiento_cuenta',
            'cajero_procesa_cuenta',
            'metodo_pago_cuenta',
            'monto_recibido',
            'cambio_dado',
            'referencia_pago',
            'ticket_generado'
        ]
        
        campos_faltantes = []
        for campo in campos_necesarios:
            if campo not in columns:
                campos_faltantes.append(campo)
        
        if campos_faltantes:
            print(f"   ⚠️  Campos faltantes en mesero_orden: {campos_faltantes}")
            print("   ℹ️  Se necesitan agregar manualmente a través de migraciones")
            
            # Crear el archivo de migración
            migration_content = '''
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
'''
            
            # Crear el archivo de migración
            migration_file = "c:/Users/lilye/OneDrive/Desktop/suchilitoo2/mesero/migrations/0002_sistema_cuentas.py"
            with open(migration_file, 'w', encoding='utf-8') as f:
                f.write(migration_content)
            
            print(f"   📝 Archivo de migración creado: {migration_file}")
        else:
            print("   ✅ Todos los campos necesarios ya existen")

def crear_modelo_notificaciones():
    """Crear modelo para notificaciones de cuenta"""
    print("\n📋 PASO 2: Creando modelo de notificaciones")
    
    modelo_content = '''
class NotificacionCuenta(models.Model):
    """Modelo para notificaciones de cuenta solicitada"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='notificaciones_cuenta')
    mesero = models.ForeignKey('accounts.Usuario', on_delete=models.CASCADE, related_name='notificaciones_enviadas')
    cajero = models.ForeignKey('accounts.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='notificaciones_recibidas')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_procesamiento = models.DateTimeField(null=True, blank=True)
    notas = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Notificación de Cuenta"
        verbose_name_plural = "Notificaciones de Cuenta"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Cuenta solicitada - Orden {self.orden.numero_orden} - Mesa {self.orden.mesa.numero if self.orden.mesa else 'Sin mesa'}"
'''
    
    # Agregar al archivo de modelos del mesero
    models_file = "c:/Users/lilye/OneDrive/Desktop/suchilitoo2/mesero/models.py"
    
    try:
        with open(models_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'class NotificacionCuenta' not in content:
            # Agregar el modelo al final del archivo
            with open(models_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n{modelo_content}")
            print("   ✅ Modelo NotificacionCuenta agregado a mesero/models.py")
        else:
            print("   ℹ️  El modelo NotificacionCuenta ya existe")
    except Exception as e:
        print(f"   ❌ Error al crear modelo: {e}")

def main():
    """Función principal"""
    try:
        print("🎯 IMPLEMENTANDO SISTEMA DE CUENTAS COMPLETO")
        print("=" * 60)
        
        # Paso 1: Agregar campos necesarios
        agregar_campos_cuenta()
        
        # Paso 2: Crear modelo de notificaciones
        crear_modelo_notificaciones()
        
        print("\n" + "=" * 60)
        print("✅ IMPLEMENTACIÓN BÁSICA COMPLETADA")
        print("\n🔄 SIGUIENTES PASOS:")
        print("1. Ejecutar: python manage.py makemigrations")
        print("2. Ejecutar: python manage.py migrate")
        print("3. Implementar las vistas del cajero")
        print("4. Implementar las vistas del mesero")
        print("5. Crear las interfaces HTML")
        print("6. Implementar el sistema de notificaciones en tiempo real")
        
    except Exception as e:
        print(f"❌ Error durante la implementación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
