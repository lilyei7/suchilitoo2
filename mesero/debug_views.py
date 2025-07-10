from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def debug_endpoint(request):
    """Endpoint de debug para probar respuestas JSON"""
    
    logger.info(f"=== DEBUG ENDPOINT ===")
    logger.info(f"Método: {request.method}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Usuario autenticado: {request.user.is_authenticated}")
    logger.info(f"Usuario: {request.user}")
    logger.info(f"Content-Type: {request.content_type}")
    
    response_data = {
        'success': True,
        'message': 'Endpoint de debug funcionando',
        'method': request.method,
        'user_authenticated': request.user.is_authenticated,
        'user': str(request.user),
        'headers': dict(request.headers),
        'content_type': request.content_type,
        'is_ajax': request.headers.get('X-Requested-With') == 'XMLHttpRequest',
        'csrf_token': request.META.get('CSRF_COOKIE'),
    }
    
    logger.info(f"Enviando respuesta: {response_data}")
    
    return JsonResponse(response_data)

@login_required
@require_http_methods(["POST"])
def debug_auth_endpoint(request):
    """Endpoint de debug que requiere autenticación"""
    
    logger.info(f"=== DEBUG AUTH ENDPOINT ===")
    logger.info(f"Usuario: {request.user}")
    logger.info(f"Es AJAX: {request.headers.get('X-Requested-With') == 'XMLHttpRequest'}")
    
    response_data = {
        'success': True,
        'message': 'Endpoint con autenticación funcionando',
        'user': str(request.user),
        'user_id': request.user.id if request.user.is_authenticated else None,
        'is_superuser': request.user.is_superuser if request.user.is_authenticated else False,
    }
    
    return JsonResponse(response_data)
