import json
from restaurant.models import ConfiguracionSistema

def configuracion_global(request):
    """
    Context processor para agregar la configuración global a todas las plantillas
    """
    # Por defecto, logo original
    logo_actual = 'dashboard/img/logo.png'
    
    try:
        # Intentar obtener la configuración del logo
        logo_config = ConfiguracionSistema.objects.filter(nombre="logo_sistema").first()
        if logo_config:
            config_data = json.loads(logo_config.valor)
            logo_path = config_data.get('logo_path')
            if logo_path:
                logo_actual = logo_path
    except Exception:
        # En caso de error, usar el logo por defecto
        pass
    
    return {
        'logo_actual': logo_actual
    }
