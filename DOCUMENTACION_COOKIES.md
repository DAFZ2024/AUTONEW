# 🍪 Documentación de Cookies - AutoNew

## Resumen

Este documento describe la implementación completa del sistema de gestión de cookies en AutoNew, conforme a las regulaciones GDPR, CCPA y otras normativas de privacidad.

## Archivos Implementados

### 1. Middleware
- **`lavado_auto/middleware_cookies.py`**: Gestiona el consentimiento y aplica políticas de cookies

### 2. Vistas
- **`lavado_auto/cookie_views.py`**: Maneja el consentimiento y preferencias de cookies

### 3. Templates
- **`lavado_auto/templates/cookies/cookie_banner.html`**: Banner interactivo de cookies
- **`lavado_auto/templates/cookies/cookie_policy.html`**: Página de política de cookies

### 4. Context Processor
- **`lavado_auto/context_processors.py`**: Proporciona datos de cookies a todos los templates

### 5. Comando de Gestión
- **`lavado_auto/management/commands/manage_cookies.py`**: Herramienta de administración de cookies

## Configuración en Settings.py

```python
# Middleware agregados
MIDDLEWARE = [
    # ... otros middleware ...
    'lavado_auto.middleware_cookies.CookieConsentMiddleware',
    'lavado_auto.middleware_cookies.CookiePolicyMiddleware',
]

# Context processor agregado
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ... otros processors ...
                'lavado_auto.context_processors.cookie_context',
            ],
        },
    },
]

# Configuración de cookies
COOKIE_SETTINGS = {
    'SECURE': not DEBUG,
    'HTTPONLY': False,
    'SAMESITE': 'Lax',
    'MAX_AGE': 365 * 24 * 60 * 60,
}
```

## URLs Configuradas

```python
urlpatterns = [
    # ... otras URLs ...
    path('cookies/', include([
        path('consent/', CookieConsentView.as_view(), name='cookie_consent'),
        path('status/', cookie_status, name='cookie_status'),
        path('preferences/', UserPreferencesView.as_view(), name='user_preferences'),
        path('politica/', CookieConsentView.as_view(), name='cookie_policy'),
    ])),
]
```

## Categorías de Cookies

### 1. **Cookies Necesarias** 🔒
- **Siempre activas**
- Autenticación, sesión, seguridad
- No se pueden desactivar

### 2. **Cookies Funcionales** ⚙️
- **Opcionales**
- Preferencias del usuario, configuraciones
- Mejoran la experiencia de uso

### 3. **Cookies de Análisis** 📊
- **Opcionales**
- Google Analytics, métricas de uso
- Ayudan a mejorar el sitio

### 4. **Cookies de Marketing** 🎯
- **Opcionales**
- Publicidad personalizada, remarketing
- Seguimiento de conversiones

## Funcionalidades Implementadas

### Banner de Cookies
- 🎨 Diseño responsivo con Tailwind CSS
- 🔄 Animaciones suaves de entrada/salida
- ⚙️ Modal de configuración avanzada
- 📱 Optimizado para móviles

### Gestión de Consentimiento
- ✅ Aceptar todas las cookies
- ❌ Rechazar cookies opcionales
- ⚙️ Personalización granular por categoría
- 💾 Persistencia de preferencias

### APIs JavaScript
```javascript
// Verificar consentimiento
window.AutoNewCookies.hasConsent('analytics')

// Abrir configuración
window.AutoNewCookies.showSettings()

// Obtener cookie
window.AutoNewCookies.getCookie('nombre')
```

### Context Variables
Disponibles en todos los templates:
- `cookie_consent`: Estado del consentimiento
- `cookie_preferences`: Preferencias detalladas
- `show_cookie_banner`: Si mostrar el banner
- `has_analytics_consent`: Consentimiento para analytics
- `has_marketing_consent`: Consentimiento para marketing

## Integración con Terceros

### Google Analytics
```javascript
if (hasConsentFor('analytics')) {
    // Cargar Google Analytics
    gtag('config', 'GA_MEASUREMENT_ID');
}
```

### Facebook Pixel
```javascript
if (hasConsentFor('marketing')) {
    // Cargar Facebook Pixel
    fbq('init', 'PIXEL_ID');
}
```

## Comandos de Administración

```bash
# Generar reporte de cookies
python manage.py manage_cookies --report

# Limpiar datos antiguos
python manage.py manage_cookies --days 365
```

## Cumplimiento Legal

### GDPR (Europa)
✅ Consentimiento explícito requerido
✅ Granularidad por categorías
✅ Fácil revocación de consentimiento
✅ Información transparente

### CCPA (California)
✅ Derecho a rechazar cookies
✅ Información clara sobre el uso
✅ Opción de no venta de datos

### LGPD (Brasil)
✅ Consentimiento para datos personales
✅ Finalidades específicas
✅ Revocación sencilla

## Mejores Prácticas Implementadas

1. **Consentimiento antes de carga**: Scripts de terceros solo se cargan tras consentimiento
2. **Granularidad**: Control por categorías de cookies
3. **Persistencia**: Preferencias guardadas por 1 año
4. **Seguridad**: Flags Secure, HttpOnly, SameSite configurados
5. **UX**: Banner no intrusivo con opciones claras
6. **Accesibilidad**: Navegación por teclado, lectores de pantalla
7. **Performance**: Carga asíncrona, scripts optimizados

## Personalización

### Modificar Categorías
Edita `COOKIE_CATEGORIES` en `settings.py` para agregar o modificar categorías.

### Cambiar Diseño
Los templates usan Tailwind CSS y pueden personalizarse fácilmente.

### Integrar Nuevos Servicios
Agrega verificaciones de consentimiento antes de cargar nuevos scripts:

```javascript
if (window.AutoNewCookies.hasConsent('analytics')) {
    // Cargar tu servicio de analytics
}
```

## Mantenimiento

### Monitoreo
- Revisar logs de errores en cookies
- Verificar tasas de consentimiento
- Actualizar políticas según cambios legales

### Actualizaciones
- Revisar nuevas regulaciones trimestralmente
- Actualizar textos informativos
- Probar compatibilidad con navegadores

## Soporte

Para dudas sobre la implementación de cookies:
- 📧 Email: privacidad@autonew.com
- 📞 Teléfono: +57 XXX XXX XXXX
- 🌐 Documentación: /cookies/politica/

---

**Última actualización**: 2 de septiembre de 2025
**Versión**: 1.0.0
**Desarrollado por**: Andres Forero para AutoNew
