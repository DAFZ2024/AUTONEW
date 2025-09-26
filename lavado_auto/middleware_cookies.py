"""
Middleware para gestión de cookies en AutoNew
"""
import json
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import JsonResponse

class CookieConsentMiddleware(MiddlewareMixin):
    """
    Middleware para gestionar el consentimiento de cookies
    """
    
    def process_request(self, request):
        # Verificar si el usuario ha dado consentimiento
        consent = request.COOKIES.get('cookie_consent')
        request.cookie_consent = consent == 'accepted'
        
        # Obtener preferencias de cookies
        preferences = request.COOKIES.get('cookie_preferences', '{}')
        try:
            request.cookie_preferences = json.loads(preferences)
        except:
            request.cookie_preferences = {
                'necessary': True,
                'functional': False,
                'analytics': False,
                'marketing': False
            }
    
    def process_response(self, request, response):
        # Agregar headers de seguridad para cookies
        if hasattr(settings, 'COOKIE_SETTINGS'):
            response['Set-Cookie-SameSite'] = settings.COOKIE_SETTINGS.get('SAMESITE', 'Lax')
        
        return response

class CookiePolicyMiddleware(MiddlewareMixin):
    """
    Middleware para aplicar políticas de cookies automáticamente
    """
    
    def process_response(self, request, response):
        # Solo aplicar en producción
        if settings.DEBUG:
            return response
            
        # Configurar cookies de sesión
        if response.cookies:
            for cookie in response.cookies.values():
                if hasattr(settings, 'COOKIE_SETTINGS'):
                    cookie['secure'] = settings.COOKIE_SETTINGS.get('SECURE', False)
                    cookie['samesite'] = settings.COOKIE_SETTINGS.get('SAMESITE', 'Lax')
                
        return response
