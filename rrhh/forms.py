from django import forms
from django.utils import timezone
from .models import (
    Empleado, DocumentoEmpleado, Turno, AsignacionTurno,
    Asistencia, Capacitacion, EmpleadoCapacitacion,
    Evaluacion, Vacacion, Nomina, Rol
)

class RolForm(forms.ModelForm):
    """Formulario para crear y editar roles"""
    class Meta:
        model = Rol
        fields = ['nombre', 'descripcion', 'permisos']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'permisos': forms.HiddenInput(),  # Se maneja con interfaz especial
        }

class EmpleadoForm(forms.ModelForm):
    """Formulario para crear y editar empleados"""
    class Meta:
        model = Empleado
        exclude = ['usuario', 'roles', 'sucursales', 'creado', 'actualizado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'fecha_ingreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_termino': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-select'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'salario_base': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'jefe_directo': forms.Select(attrs={'class': 'form-select'}),
        }

class DocumentoEmpleadoForm(forms.ModelForm):
    """Formulario para subir documentos de empleados"""
    class Meta:
        model = DocumentoEmpleado
        exclude = ['empleado', 'fecha_subida']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class TurnoForm(forms.ModelForm):
    """Formulario para crear y editar turnos"""
    class Meta:
        model = Turno
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'lunes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'martes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'miercoles': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'jueves': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'viernes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sabado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'domingo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AsignacionTurnoForm(forms.ModelForm):
    """Formulario para asignar turnos a empleados"""
    class Meta:
        model = AsignacionTurno
        fields = '__all__'
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'turno': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'sucursal': forms.Select(attrs={'class': 'form-select'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class AsistenciaForm(forms.ModelForm):
    """Formulario para registrar asistencia"""
    class Meta:
        model = Asistencia
        fields = '__all__'
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_entrada': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'hora_salida': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'turno': forms.Select(attrs={'class': 'form-select'}),
            'sucursal': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CapacitacionForm(forms.ModelForm):
    """Formulario para crear y editar capacitaciones"""
    class Meta:
        model = Capacitacion
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'duracion_horas': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'instructor': forms.TextInput(attrs={'class': 'form-control'}),
            'material': forms.FileInput(attrs={'class': 'form-control'}),
        }

class EmpleadoCapacitacionForm(forms.ModelForm):
    """Formulario para asignar capacitaciones a empleados"""
    class Meta:
        model = EmpleadoCapacitacion
        exclude = ['fecha_asignacion']
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'capacitacion': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'calificacion': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '1', 'max': '10'}),
            'comentarios': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class EvaluacionForm(forms.ModelForm):
    """Formulario para evaluaciones de desempeño"""
    class Meta:
        model = Evaluacion
        fields = '__all__'
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'evaluador': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'periodo_evaluado': forms.TextInput(attrs={'class': 'form-control'}),
            'puntuacion_general': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '1', 'max': '10'}),
            'fortalezas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'areas_mejora': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'comentarios': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class VacacionForm(forms.ModelForm):
    """Formulario para solicitar vacaciones y permisos"""
    class Meta:
        model = Vacacion
        exclude = ['aprobada_por', 'fecha_solicitud', 'fecha_aprobacion']
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'dias_habiles': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise forms.ValidationError('La fecha de inicio no puede ser posterior a la fecha de fin.')
        
        return cleaned_data

class NominaForm(forms.ModelForm):
    """Formulario para generar nóminas de pago"""
    class Meta:
        model = Nomina
        exclude = ['aprobada_por', 'recibo_pdf']
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'periodo': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_calculo': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_pago': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salario_base': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'horas_extra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bonificaciones': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'comisiones': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'deducciones': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_bruto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_neto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Calcular total bruto
        salario_base = cleaned_data.get('salario_base') or 0
        horas_extra = cleaned_data.get('horas_extra') or 0
        bonificaciones = cleaned_data.get('bonificaciones') or 0
        comisiones = cleaned_data.get('comisiones') or 0
        
        total_bruto = salario_base + horas_extra + bonificaciones + comisiones
        cleaned_data['total_bruto'] = total_bruto
        
        # Calcular total neto
        deducciones = cleaned_data.get('deducciones') or 0
        total_neto = total_bruto - deducciones
        cleaned_data['total_neto'] = total_neto
        
        return cleaned_data
