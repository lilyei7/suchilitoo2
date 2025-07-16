# Guía para Mejorar el Sistema de Incidentes

Este documento describe las mejoras realizadas al sistema de reporte de incidentes en la plataforma Suchilito, específicamente relacionadas con el manejo de comentarios y el historial de incidentes.

## Resumen de Mejoras

1. **Modelo de Comentarios Dedicado**: Se ha creado un modelo dedicado `IncidentComment` para almacenar comentarios de incidentes.
2. **Visualización de Comentarios**: Se ha mejorado la interfaz para mostrar comentarios en la página de detalles de incidentes.
3. **Integración con Historial**: Los comentarios ahora aparecen correctamente en la línea de tiempo del historial del incidente.
4. **Notificaciones**: Se han implementado notificaciones automáticas cuando se añaden comentarios a incidentes asignados.

## Pasos para Implementar las Mejoras

### 1. Ejecutar los Scripts de Mejora

He creado dos scripts que implementan estas mejoras automáticamente:

```bash
# Primero, activa el entorno virtual si lo estás usando
# En Windows:
.\venv\Scripts\activate

# Ejecuta el primer script para crear el modelo de comentarios
python enhance_incident_comments.py

# Ejecuta el segundo script para mejorar la visualización de comentarios
python enhance_incident_comments_display.py
```

### 2. Reiniciar el Servidor Django

```bash
# Detén el servidor actual (Ctrl+C) y luego reinícialo
python manage.py runserver
```

### 3. Verificar la Funcionalidad

1. Navega a un incidente existente en: `/dashboard/checklist/incidente/[ID]/`
2. Verifica que puedes ver los comentarios anteriores (si existen)
3. Añade un nuevo comentario utilizando el formulario
4. Comprueba que el comentario aparece tanto en la sección de comentarios como en el historial

## Detalles Técnicos

### Modelo de Comentarios (`IncidentComment`)

```python
class IncidentComment(models.Model):
    incident = models.ForeignKey(IncidentReport, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    text = models.TextField('Comentario')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Automáticamente crea entradas en el historial y notificaciones cuando se añade un comentario
```

### Sección de Comentarios en la Plantilla

La página de detalles de incidentes ahora muestra:
- Lista de comentarios existentes (ordenados por fecha, más recientes primero)
- Formulario para añadir nuevos comentarios
- Etiquetas visuales que identifican si el comentario es del reportante o del usuario asignado

### Integración con el Historial

Cada vez que se añade un comentario:
1. Se almacena en la tabla `dashboard_incidentcomment`
2. Se crea automáticamente una entrada en `IncidentHistory` con tipo 'comentario'
3. Se envía una notificación al usuario asignado (si es diferente al que comenta)

## Solución de Problemas

Si encuentras algún problema al implementar estas mejoras:

1. **Error en las Migraciones**: Ejecuta manualmente:
   ```bash
   python manage.py makemigrations dashboard
   python manage.py migrate dashboard
   ```

2. **No se muestran los comentarios**:
   - Verifica la consola del navegador para errores JavaScript
   - Comprueba los logs del servidor para errores en las vistas
   - Asegúrate de que la base de datos tiene la tabla `dashboard_incidentcomment`

3. **Error al añadir comentarios**:
   - Verifica que la vista `add_incident_comment` está correctamente implementada
   - Comprueba que el formulario está enviando los datos correctamente

## Próximas Mejoras Recomendadas

1. Añadir la capacidad de editar y eliminar comentarios
2. Implementar un sistema de menciones (@usuario) en los comentarios
3. Mejorar las notificaciones para incluir resúmenes diarios de actividad en incidentes

---

Si necesitas ayuda adicional o tienes preguntas sobre estas mejoras, no dudes en contactarme.
