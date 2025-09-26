"""
Context processors para cookies en AutoNew
"""
import json
from django.conf import settings

def cookie_context(request):
    """
    Context processor que proporciona información de cookies a todos los templates
    """
    # Obtener estado de consentimiento
    consent = request.COOKIES.get('cookie_consent', '')
    
    # Obtener preferencias de cookies
    preferences = request.COOKIES.get('cookie_preferences', '{}')
    try:
        cookie_preferences = json.loads(preferences)
    except:
        cookie_preferences = {
            'necessary': True,
            'functional': False,
            'analytics': False,
            'marketing': False
        }
    
    # Verificar si se debe mostrar el banner
    show_cookie_banner = not consent
    
    # Información sobre categorías de cookies disponibles
    cookie_categories = getattr(settings, 'COOKIE_CATEGORIES', {})
    
    return {
        'cookie_consent': consent,
        'cookie_preferences': cookie_preferences,
        'show_cookie_banner': show_cookie_banner,
        'cookie_categories': cookie_categories,
        'has_analytics_consent': cookie_preferences.get('analytics', False),
        'has_marketing_consent': cookie_preferences.get('marketing', False),
        'has_functional_consent': cookie_preferences.get('functional', False),
    }
