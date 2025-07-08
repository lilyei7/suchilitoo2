import django
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from mesero.models import Mesa, Orden
from accounts.models import Sucursal
from django.contrib.auth.models import Group
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()

def verificar_estado_completo():
    print("=== VERIFICACIÓN COMPLETA DEL ESTADO ===")
    
    # 1. Verificar sucursales
    print("\n1. SUCURSALES:")
    sucursales = Sucursal.objects.all()
    for sucursal in sucursales:
        print(f"   - {sucursal.nombre} (ID: {sucursal.id})")
    
    # 2. Verificar usuarios meseros
    print("\n2. USUARIOS MESEROS:")
    try:
        meseros_group = Group.objects.get(name='Meseros')
        meseros = User.objects.filter(groups=meseros_group)
        for mesero in meseros:
            print(f"   - {mesero.username} ({mesero.email}) - Sucursal: {getattr(mesero, 'sucursal', 'SIN SUCURSAL')}")
    except Group.DoesNotExist:
        print("   No existe el grupo 'Meseros'")
    
    # 3. Verificar mesas por sucursal
    print("\n3. MESAS POR SUCURSAL:")
    for sucursal in sucursales:
        mesas = Mesa.objects.filter(sucursal=sucursal)
        mesas_activas = mesas.filter(activa=True)
        print(f"   {sucursal.nombre}:")
        print(f"     - Total mesas: {mesas.count()}")
        print(f"     - Mesas activas: {mesas_activas.count()}")
        for mesa in mesas_activas[:5]:  # Mostrar solo las primeras 5
            print(f"       * Mesa {mesa.numero} (ID: {mesa.id}) - Estado: {mesa.get_estado_display()}")
    
    # 4. Verificar sesiones activas
    print("\n4. SESIONES ACTIVAS:")
    active_sessions = Session.objects.filter(expire_date__gt=timezone.now())
    print(f"   Total sesiones activas: {active_sessions.count()}")
    
    # 5. Probar la consulta de la vista
    print("\n5. SIMULACIÓN DE LA VISTA SELECCIONAR_MESA:")
    
    # Intentar con diferentes usuarios
    usuarios_test = ['mesero_test', 'mesero1', 'mesero2', 'mesero3']
    
    for username in usuarios_test:
        try:
            user = User.objects.get(username=username)
            print(f"\n   Usuario: {username}")
            print(f"   - Sucursal asignada: {getattr(user, 'sucursal', 'SIN SUCURSAL')}")
            
            if hasattr(user, 'sucursal') and user.sucursal:
                # Simular la consulta de la vista
                mesas = Mesa.objects.filter(sucursal=user.sucursal, activa=True)
                print(f"   - Mesas encontradas: {mesas.count()}")
                
                # Actualizar estado de cada mesa
                for mesa in mesas:
                    orden_activa = Orden.objects.filter(mesa=mesa, estado='activa').exists()
                    if orden_activa:
                        mesa.estado = 'ocupada'
                    else:
                        mesa.estado = 'disponible'
                    mesa.save()
                
                # Mostrar algunas mesas
                for mesa in mesas[:3]:
                    print(f"     * Mesa {mesa.numero} - Estado: {mesa.get_estado_display()}")
            else:
                print("   - ERROR: Usuario sin sucursal asignada")
                
        except User.DoesNotExist:
            print(f"   Usuario '{username}' no existe")
    
    # 6. Verificar template y archivos
    print("\n6. VERIFICACIÓN DE ARCHIVOS:")
    
    # Verificar vista
    vista_path = "mesero/views.py"
    if os.path.exists(vista_path):
        print(f"   ✓ Vista existe: {vista_path}")
    else:
        print(f"   ✗ Vista NO existe: {vista_path}")
    
    # Verificar template
    template_path = "mesero/templates/mesero/seleccionar_mesa.html"
    if os.path.exists(template_path):
        print(f"   ✓ Template existe: {template_path}")
    else:
        print(f"   ✗ Template NO existe: {template_path}")
    
    print("\n=== RECOMENDACIONES ===")
    print("1. Asegúrate de estar logueado con un usuario que tenga sucursal asignada")
    print("2. Verifica que el usuario pertenezca al grupo 'Meseros'")
    print("3. Confirma que la sucursal tenga mesas activas")
    print("4. Revisa la consola del servidor para ver los logs de depuración")
    print("5. Prueba acceder a: http://127.0.0.1:8000/mesero/seleccionar-mesa/")

if __name__ == "__main__":
    verificar_estado_completo()
