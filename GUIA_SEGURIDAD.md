# 🛡️ Guía de Seguridad - AutoNew

## 📋 Índice

1. [Configuración de Seguridad](#configuración-de-seguridad)
2. [Autenticación y Autorización](#autenticación-y-autorización)
3. [Protección de Datos](#protección-de-datos)
4. [Validación de Entrada](#validación-de-entrada)
5. [Configuración HTTPS](#configuración-https)
6. [Backup y Recuperación](#backup-y-recuperación)
7. [Monitoreo y Logs](#monitoreo-y-logs)
8. [Checklist de Seguridad](#checklist-de-seguridad)

---

# ⚙️ Configuración de Seguridad

## Settings de Producción

```python
# autonew/settings_production.py

# ¡CRÍTICO! - Nunca en producción con DEBUG=True
DEBUG = False

# Hosts permitidos - SOLO los dominios reales
ALLOWED_HOSTS = [
    'tu-dominio.com',
    'www.tu-dominio.com',
    # NO incluir localhost o 127.0.0.1 en producción
]

# Clave secreta - DEBE ser única y segura
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
# Generar nueva clave: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Configuración HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies seguras
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 hora
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# Headers de seguridad
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

## Variables de Entorno

```bash
# .env (NUNCA subir a Git)
DJANGO_SECRET_KEY=tu-clave-super-secreta-aqui
DB_PASSWORD=password-base-datos-seguro
EMAIL_PASSWORD=password-email-aplicacion
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
```

---

# 🔐 Autenticación y Autorización

## Modelo de Usuario Seguro

```python
# lavado_auto/models.py
class Usuario(AbstractBaseUser, PermissionsMixin):
    # Campos únicos para evitar duplicados
    nombre_usuario = models.CharField(max_length=20, unique=True)
    correo = models.EmailField(unique=True)
    
    # Validaciones de seguridad
    def clean(self):
        super().clean()
        if len(self.nombre_usuario) < 3:
            raise ValidationError('El nombre de usuario debe tener al menos 3 caracteres')
        if not re.match(r'^[a-zA-Z0-9_]+$', self.nombre_usuario):
            raise ValidationError('El nombre de usuario solo puede contener letras, números y guiones bajos')
```

## Validadores de Contraseña

```python
# autonew/settings.py
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ('nombre_usuario', 'correo', 'nombre_completo'),
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    # Validador personalizado
    {
        'NAME': 'lavado_auto.validators.ComplexPasswordValidator',
    },
]
```

## Decorador de Seguridad Mejorado

```python
# lavado_auto/decorators.py
from functools import wraps
from django.core.cache import cache
from django.http import HttpResponseForbidden
import time

def admin_required_with_rate_limit(max_attempts=5, lockout_duration=300):
    """
    Decorador con protección contra ataques de fuerza bruta
    """
    def decorator(function):
        @wraps(function)
        def wrap(request, *args, **kwargs):
            # Obtener IP del usuario
            ip = get_client_ip(request)
            cache_key = f'admin_attempts_{ip}'
            
            # Verificar intentos fallidos
            attempts = cache.get(cache_key, 0)
            if attempts >= max_attempts:
                return HttpResponseForbidden("Demasiados intentos fallidos. Intente más tarde.")
            
            # Verificar autenticación y rol
            if not request.user.is_authenticated:
                # Incrementar contador de intentos
                cache.set(cache_key, attempts + 1, lockout_duration)
                return redirect('logincrud')
            
            if not hasattr(request.user, 'rol') or request.user.rol != 'admin':
                cache.set(cache_key, attempts + 1, lockout_duration)
                return redirect('logincrud')
            
            # Limpiar contador si el acceso es exitoso
            cache.delete(cache_key)
            return function(request, *args, **kwargs)
        return wrap
    return decorator

def get_client_ip(request):
    """Obtener IP real del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

---

# 🛡️ Protección de Datos

## Validación de Archivos

```python
# lavado_auto/validators.py
import magic
from django.core.exceptions import ValidationError
from django.conf import settings

def validate_image_file(value):
    """Validar que el archivo sea realmente una imagen"""
    # Verificar tamaño
    if value.size > 5 * 1024 * 1024:  # 5MB máximo
        raise ValidationError('El archivo no puede ser mayor a 5MB')
    
    # Verificar tipo MIME real (no solo extensión)
    mime = magic.from_buffer(value.read(1024), mime=True)
    if mime not in ['image/jpeg', 'image/png', 'image/gif']:
        raise ValidationError('Solo se permiten archivos JPG, PNG o GIF')
    
    # Resetear puntero del archivo
    value.seek(0)

def validate_phone_number(value):
    """Validar número de teléfono colombiano"""
    import re
    pattern = r'^57[0-9]{10}$'
    if not re.match(pattern, value):
        raise ValidationError('Número de teléfono inválido. Debe ser formato: 573001234567')
```

## Sanitización de Datos

```python
# lavado_auto/utils.py
import bleach
from django.utils.html import escape

def sanitize_input(text):
    """Limpiar y sanitizar entrada de usuario"""
    # Limpiar HTML malicioso
    cleaned = bleach.clean(text, tags=[], attributes={}, strip=True)
    
    # Escapar caracteres especiales
    escaped = escape(cleaned)
    
    return escaped

def validate_business_hours(hora):
    """Validar que la hora esté en horario comercial"""
    from datetime import time
    
    hora_obj = time.fromisoformat(hora)
    inicio = time(8, 0)  # 8:00 AM
    fin = time(18, 0)    # 6:00 PM
    
    if not (inicio <= hora_obj <= fin):
        raise ValidationError('Las reservas solo se pueden hacer entre 8:00 AM y 6:00 PM')
```

---

# ✅ Validación de Entrada

## Formularios Seguros

```python
# lavado_auto/forms.py
from django import forms
from django.core.exceptions import ValidationError
import re

class SecureReservaForm(forms.ModelForm):
    """Formulario de reserva con validaciones de seguridad"""
    
    class Meta:
        model = Reserva
        fields = ['fecha', 'hora', 'empresa']
    
    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']
        from datetime import date
        
        if fecha < date.today():
            raise ValidationError('No se pueden hacer reservas en fechas pasadas')
        
        # Máximo 30 días en el futuro
        from datetime import timedelta
        if fecha > date.today() + timedelta(days=30):
            raise ValidationError('No se pueden hacer reservas con más de 30 días de anticipación')
        
        return fecha
    
    def clean_comentario(self):
        comentario = self.cleaned_data.get('comentario', '')
        
        # Longitud máxima
        if len(comentario) > 500:
            raise ValidationError('El comentario no puede tener más de 500 caracteres')
        
        # Filtro de spam básico
        spam_words = ['spam', 'viagra', 'casino', 'lottery']
        comentario_lower = comentario.lower()
        
        for word in spam_words:
            if word in comentario_lower:
                raise ValidationError('El comentario contiene contenido no permitido')
        
        return sanitize_input(comentario)

class SecureUsuarioForm(forms.ModelForm):
    """Formulario de usuario con validaciones extras"""
    
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Mínimo 8 caracteres, debe incluir letras y números"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Repetir contraseña"
    )
    
    def clean_nombre_usuario(self):
        nombre_usuario = self.cleaned_data['nombre_usuario']
        
        # Caracteres permitidos
        if not re.match(r'^[a-zA-Z0-9_]+$', nombre_usuario):
            raise ValidationError('Solo letras, números y guiones bajos permitidos')
        
        # Longitud
        if len(nombre_usuario) < 3 or len(nombre_usuario) > 20:
            raise ValidationError('El nombre de usuario debe tener entre 3 y 20 caracteres')
        
        # Palabras reservadas
        reserved_words = ['admin', 'root', 'administrator', 'null', 'undefined']
        if nombre_usuario.lower() in reserved_words:
            raise ValidationError('Este nombre de usuario no está disponible')
        
        return nombre_usuario
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Las contraseñas no coinciden')
        
        return password2
```

## Validación en Vistas

```python
# lavado_auto/views.py
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
import logging

logger = logging.getLogger(__name__)

@csrf_protect
@never_cache
def secure_login(request):
    """Vista de login con protecciones extra"""
    
    if request.method == 'POST':
        # Obtener datos del form
        nombre_usuario = request.POST.get('nombre_usuario', '').strip()
        password = request.POST.get('password', '')
        
        # Validaciones básicas
        if not nombre_usuario or not password:
            messages.error(request, 'Todos los campos son obligatorios')
            return render(request, 'login.html')
        
        # Protección contra inyección
        if len(nombre_usuario) > 50 or len(password) > 128:
            messages.error(request, 'Datos inválidos')
            logger.warning(f'Intento de login con datos sospechosos desde IP: {get_client_ip(request)}')
            return render(request, 'login.html')
        
        # Autenticación
        user = authenticate(request, username=nombre_usuario, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                logger.info(f'Login exitoso para usuario: {nombre_usuario} desde IP: {get_client_ip(request)}')
                return redirect('home')
            else:
                messages.error(request, 'Cuenta desactivada')
                logger.warning(f'Intento de login con cuenta desactivada: {nombre_usuario}')
        else:
            messages.error(request, 'Credenciales incorrectas')
            logger.warning(f'Intento de login fallido para: {nombre_usuario} desde IP: {get_client_ip(request)}')
    
    return render(request, 'login.html')
```

---

# 🔒 Configuración HTTPS

## Certificado SSL

### Let's Encrypt (Gratuito)
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Renovación automática
sudo crontab -e
# Agregar: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Nginx con SSL
```nginx
# /etc/nginx/sites-available/autonew
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com www.tu-dominio.com;
    
    # Certificados SSL
    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;
    
    # Configuración SSL segura
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    
    # Headers de seguridad
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header Referrer-Policy no-referrer-when-downgrade always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /var/www/autonew/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/autonew/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
}
```

---

# 💾 Backup y Recuperación

## Script de Backup Automatizado

```bash
#!/bin/bash
# backup.sh

# Configuración
DB_NAME="autonew_db"
DB_USER="autonew_user"
BACKUP_DIR="/var/backups/autonew"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Crear directorio de backup
mkdir -p $BACKUP_DIR

# Backup de base de datos
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Backup de archivos media
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /var/www/autonew/media/

# Backup de configuración
cp -r /var/www/autonew/autonew/settings* $BACKUP_DIR/settings_backup_$DATE/

# Limpiar backups antiguos
find $BACKUP_DIR -name "*.sql" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Log del backup
echo "$(date): Backup completado - $DATE" >> /var/log/autonew_backup.log
```

## Programar Backup con Cron

```bash
# Editar crontab
sudo crontab -e

# Backup diario a las 2:00 AM
0 2 * * * /usr/local/bin/backup_autonew.sh

# Backup de la configuración semanalmente
0 3 * * 0 tar -czf /var/backups/autonew/config_$(date +\%Y\%m\%d).tar.gz /var/www/autonew/
```

---

# 📊 Monitoreo y Logs

## Configuración de Logging

```python
# autonew/settings_production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/autonew/django.log',
            'maxBytes': 15728640,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/autonew/security.log',
            'maxBytes': 15728640,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'lavado_auto': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
    },
}
```

## Middleware de Auditoría

```python
# lavado_auto/middleware.py
import logging
from django.utils.deprecation import MiddlewareMixin

security_logger = logging.getLogger('django.security')

class SecurityAuditMiddleware(MiddlewareMixin):
    """Middleware para auditoría de seguridad"""
    
    def process_request(self, request):
        # Detectar patrones sospechosos
        suspicious_patterns = [
            'admin/admin',
            'phpmyadmin',
            'wp-admin',
            'xmlrpc.php',
            '../../../',
            '<script>',
            'union select',
            'drop table'
        ]
        
        path = request.get_full_path().lower()
        
        for pattern in suspicious_patterns:
            if pattern in path:
                security_logger.warning(
                    f'Patrón sospechoso detectado: {pattern} desde IP: {self.get_client_ip(request)}'
                )
                break
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
```

---

# ✅ Checklist de Seguridad

## Pre-Despliegue

### ⚙️ Configuración
- [ ] `DEBUG = False` en producción
- [ ] `SECRET_KEY` única y segura
- [ ] `ALLOWED_HOSTS` configurado correctamente
- [ ] Variables de entorno configuradas
- [ ] Base de datos con credenciales seguras

### 🔐 HTTPS y SSL
- [ ] Certificado SSL instalado
- [ ] Redirección HTTP → HTTPS
- [ ] Headers de seguridad configurados
- [ ] HSTS habilitado
- [ ] Cookies seguras

### 🛡️ Autenticación
- [ ] Validadores de contraseña configurados
- [ ] Rate limiting implementado
- [ ] Logs de seguridad activos
- [ ] Sesiones seguras configuradas

### 📁 Archivos y Permisos
- [ ] Archivos de configuración protegidos
- [ ] Directorio media con permisos correctos
- [ ] Validación de archivos subidos
- [ ] Backup automatizado configurado

## Post-Despliegue

### 🔍 Monitoreo
- [ ] Logs de aplicación funcionando
- [ ] Logs de seguridad activos
- [ ] Monitoreo de errores 500/404
- [ ] Alertas configuradas

### 🧪 Pruebas de Seguridad
- [ ] Pruebas de penetración básicas
- [ ] Verificación de headers de seguridad
- [ ] Test de vulnerabilidades comunes
- [ ] Verificación de backup y restauración

### 📊 Mantenimiento
- [ ] Actualizaciones de seguridad programadas
- [ ] Revisión de logs semanal
- [ ] Pruebas de backup mensuales
- [ ] Auditoría de usuarios activos

---

# 🚨 Respuesta a Incidentes

## Plan de Respuesta

### 1. Detección
- Monitoreo de logs automático
- Alertas de comportamiento anómalo
- Reportes de usuarios

### 2. Contención
```bash
# Bloquear IP sospechosa
sudo ufw insert 1 deny from DIRECCION_IP_SOSPECHOSA

# Desactivar usuario comprometido
python manage.py shell -c "
from lavado_auto.models import Usuario
usuario = Usuario.objects.get(nombre_usuario='usuario_comprometido')
usuario.is_active = False
usuario.save()
"
```

### 3. Erradicación
- Cambiar contraseñas comprometidas
- Actualizar dependencias vulnerables
- Aplicar parches de seguridad

### 4. Recuperación
- Restaurar desde backup si es necesario
- Verificar integridad de datos
- Monitoreo intensivo

### 5. Lecciones Aprendidas
- Documentar el incidente
- Actualizar procedimientos
- Mejorar medidas preventivas

---

# 📞 Contactos de Emergencia

## Equipo de Seguridad
- **Security Lead**: security@autonew.com
- **Dev Team**: dev@autonew.com
- **Infrastructure**: infra@autonew.com

## Servicios Externos
- **Hosting Provider**: soporte@hosting.com
- **SSL Certificate**: certificados@letsencrypt.org
- **DNS Provider**: dns@proveedor.com

---

**⚠️ IMPORTANTE**: Esta guía debe actualizarse regularmente y todo el equipo debe estar familiarizado con los procedimientos de seguridad.

*Última actualización: 30 de junio de 2025*
