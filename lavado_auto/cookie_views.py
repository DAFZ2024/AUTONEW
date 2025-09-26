"""
Vistas para gestión de cookies en AutoNew
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.conf import settings
import json
from datetime import datetime, timedelta

class CookieConsentView(View):
    """
    Vista para manejar el consentimiento de cookies
    """
    
    def get(self, request):
        """Mostrar política de cookies"""
        context = {
            'cookie_consent': request.COOKIES.get('cookie_consent'),
            'cookie_preferences': getattr(request, 'cookie_preferences', {})
        }
        return render(request, 'cookies/cookie_policy.html', context)
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        """Guardar preferencias de cookies"""
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            response = JsonResponse({'status': 'success'})
            
            if action == 'accept_all':
                # Aceptar todas las cookies
                preferences = {
                    'necessary': True,
                    'functional': True,
                    'analytics': True,
                    'marketing': True
                }
                self._set_cookie_consent(response, 'accepted', preferences)
                
            elif action == 'reject_all':
                # Solo cookies necesarias
                preferences = {
                    'necessary': True,
                    'functional': False,
                    'analytics': False,
                    'marketing': False
                }
                self._set_cookie_consent(response, 'rejected', preferences)
                
            elif action == 'customize':
                # Preferencias personalizadas
                preferences = data.get('preferences', {})
                preferences['necessary'] = True  # Siempre necesarias
                self._set_cookie_consent(response, 'customized', preferences)
                
            return response
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    def _set_cookie_consent(self, response, consent_type, preferences):
        """Establecer cookies de consentimiento"""
        # Cookie de consentimiento
        response.set_cookie(
            'cookie_consent',
            consent_type,
            max_age=365 * 24 * 60 * 60,  # 1 año
            secure=not settings.DEBUG,
            httponly=False,
            samesite='Lax'
        )
        
        # Cookie de preferencias
        response.set_cookie(
            'cookie_preferences',
            json.dumps(preferences),
            max_age=365 * 24 * 60 * 60,
            secure=not settings.DEBUG,
            httponly=False,
            samesite='Lax'
        )
        
        # Cookie de timestamp
        response.set_cookie(
            'cookie_consent_date',
            datetime.now().isoformat(),
            max_age=365 * 24 * 60 * 60,
            secure=not settings.DEBUG,
            httponly=True,
            samesite='Lax'
        )

@require_http_methods(["GET"])
def cookie_status(request):
    """API para verificar estado de cookies"""
    return JsonResponse({
        'consent': request.COOKIES.get('cookie_consent'),
        'preferences': getattr(request, 'cookie_preferences', {}),
        'consent_date': request.COOKIES.get('cookie_consent_date')
    })

class UserPreferencesView(View):
    """
    Vista para manejar preferencias del usuario usando cookies
    """
    
    def get(self, request):
        """Obtener preferencias del usuario"""
        preferences = {
            'theme': request.COOKIES.get('user_theme', 'light'),
            'language': request.COOKIES.get('user_language', 'es'),
            'notifications': request.COOKIES.get('user_notifications', 'enabled'),
            'auto_save': request.COOKIES.get('user_auto_save', 'true')
        }
        return JsonResponse(preferences)
    
    def post(self, request):
        """Guardar preferencias del usuario"""
        try:
            data = json.loads(request.body)
            response = JsonResponse({'status': 'success'})
            
            # Solo guardar si el usuario ha consentido cookies funcionales
            cookie_preferences = getattr(request, 'cookie_preferences', {})
            if not cookie_preferences.get('functional', False):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Cookies funcionales no permitidas'
                }, status=403)
            
            # Guardar cada preferencia
            for key, value in data.items():
                if key in ['theme', 'language', 'notifications', 'auto_save']:
                    response.set_cookie(
                        f'user_{key}',
                        str(value),
                        max_age=30 * 24 * 60 * 60,  # 30 días
                        secure=not settings.DEBUG,
                        httponly=False,
                        samesite='Lax'
                    )
            
            return response
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
