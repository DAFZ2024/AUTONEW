from django.db import models
from django.utils import timezone
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import uuid
import random


# Create your models here.

class UsuarioManager(BaseUserManager):
    def create_user(self, nombre_usuario, correo, password=None, **extra_fields):
        if not correo:
            raise ValueError('El usuario debe tener un correo electrónico')
        if not nombre_usuario:
            raise ValueError('El usuario debe tener un nombre de usuario')
        
        correo = self.normalize_email(correo)
        user = self.model(nombre_usuario=nombre_usuario, correo=correo, **extra_fields)
        user.set_password(password)  # Esto encripta la contraseña automáticamente
        user.save(using=self._db)
        return user
    
    def create_superuser(self, nombre_usuario, correo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(nombre_usuario, correo, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    @property
    def email(self):
        return self.correo
    id_usuario = models.AutoField(primary_key=True)
    nombre_completo = models.CharField(max_length=255) 
    nombre_usuario = models.CharField(max_length=20, unique=True)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    # Removemos el campo contrasena porque AbstractBaseUser ya maneja password
    token_reset = models.CharField(max_length=255, null=True, blank=True)
    rol = models.CharField(
        max_length=50, 
        choices=(('cliente', 'Cliente'), ('admin', 'Administrador')), 
        default='cliente'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(default=timezone.now)  # Fecha de registro del usuario
    
    # Campos para control de intentos fallidos de login
    failed_login_attempts = models.IntegerField(default=0)  # Contador de intentos fallidos
    last_failed_login = models.DateTimeField(null=True, blank=True)  # Última vez que falló el login
    lockout_time = models.DateTimeField(null=True, blank=True)  # Tiempo de bloqueo temporal (15 min)
    first_warning_sent = models.BooleanField(default=False)  # Si ya se envió el primer aviso de seguridad

    objects = UsuarioManager()

    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = ['correo']
    
    def __str__(self):
        return self.nombre_usuario
    
    @property
    def username(self):
        """Propiedad para compatibilidad con Django auth"""
        return self.nombre_usuario
    
    def increment_failed_attempts(self):
        """
        Incrementa el contador de intentos fallidos.
        Lógica:
        - 3 intentos fallidos: Bloqueo temporal de 15 minutos + correo de alerta
        - Después de 15 minutos, si falla 3 veces más: Desactivar cuenta + correo
        """
        from django.core.mail import send_mail, EmailMultiAlternatives
        from django.conf import settings
        
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        
        # Primera vez que llega a 3 intentos fallidos
        if self.failed_login_attempts == 3 and not self.first_warning_sent:
            self.lockout_time = timezone.now()  # Iniciar bloqueo temporal de 15 minutos
            self.first_warning_sent = True
            
            # Enviar correo de alerta (primer intento de acceso sospechoso)
            try:
                html_message = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7fa; }}
        .email-container {{ max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center; }}
        .header-icon {{ font-size: 64px; margin-bottom: 10px; }}
        .header h1 {{ color: #ffffff; margin: 0; font-size: 28px; font-weight: 600; }}
        .content {{ padding: 40px 30px; }}
        .greeting {{ font-size: 18px; color: #333333; margin-bottom: 20px; font-weight: 500; }}
        .alert-box {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin: 25px 0; border-radius: 6px; }}
        .alert-box strong {{ color: #856404; display: block; margin-bottom: 10px; font-size: 16px; }}
        .info-box {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 25px 0; }}
        .info-row {{ display: flex; align-items: center; margin: 12px 0; }}
        .info-icon {{ font-size: 20px; margin-right: 12px; width: 24px; }}
        .info-text {{ color: #495057; font-size: 15px; }}
        .info-text strong {{ color: #212529; }}
        .section {{ margin: 30px 0; }}
        .section-title {{ color: #667eea; font-size: 18px; font-weight: 600; margin-bottom: 15px; border-bottom: 2px solid #e9ecef; padding-bottom: 8px; }}
        .action-list {{ list-style: none; padding: 0; }}
        .action-list li {{ padding: 12px 0; padding-left: 30px; position: relative; color: #495057; line-height: 1.6; }}
        .action-list li:before {{ content: "✓"; position: absolute; left: 0; color: #28a745; font-weight: bold; font-size: 18px; }}
        .warning-box {{ background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 20px; margin: 25px 0; border-radius: 6px; }}
        .warning-box p {{ margin: 0; color: #721c24; font-weight: 500; }}
        .footer {{ background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e9ecef; }}
        .footer p {{ margin: 5px 0; color: #6c757d; font-size: 14px; }}
        .button {{ display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff !important; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0; box-shadow: 0 4px 12px rgba(102,126,234,0.3); transition: all 0.3s; }}
        .button:hover {{ transform: translateY(-2px); box-shadow: 0 6px 16px rgba(102,126,234,0.4); }}
        @media only screen and (max-width: 600px) {{
            .email-container {{ margin: 20px; }}
            .content {{ padding: 25px 20px; }}
            .header {{ padding: 30px 20px; }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="header-icon">⚠️</div>
            <h1>Alerta de Seguridad</h1>
        </div>
        
        <div class="content">
            <p class="greeting">Hola <strong>{self.nombre_completo}</strong>,</p>
            
            <div class="alert-box">
                <strong>⚡ Hemos detectado actividad inusual en tu cuenta</strong>
                <p style="margin: 8px 0 0 0; color: #856404;">Se registraron 3 intentos fallidos de inicio de sesión en tu cuenta de AUTONEW.</p>
            </div>
            
            <div class="info-box">
                <div class="info-row">
                    <span class="info-icon">👤</span>
                    <span class="info-text"><strong>Usuario:</strong> {self.nombre_usuario}</span>
                </div>
                <div class="info-row">
                    <span class="info-icon">📅</span>
                    <span class="info-text"><strong>Fecha y hora:</strong> {timezone.now().strftime('%d/%m/%Y a las %H:%M:%S')}</span>
                </div>
                <div class="info-row">
                    <span class="info-icon">🔒</span>
                    <span class="info-text"><strong>Estado:</strong> Cuenta bloqueada temporalmente</span>
                </div>
                <div class="info-row">
                    <span class="info-icon">⏱️</span>
                    <span class="info-text"><strong>Duración del bloqueo:</strong> 15 minutos</span>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">✅ Si fuiste tú quien intentó acceder:</h2>
                <ul class="action-list">
                    <li>Tu cuenta ha sido bloqueada temporalmente por 15 minutos como medida de seguridad preventiva.</li>
                    <li>Podrás volver a intentar iniciar sesión después de transcurrido este tiempo.</li>
                    <li>Asegúrate de recordar tu contraseña correcta para evitar nuevos bloqueos.</li>
                </ul>
            </div>
            
            <div class="section">
                <h2 class="section-title">🚨 Si NO fuiste tú:</h2>
                <ul class="action-list">
                    <li>Te recomendamos cambiar tu contraseña inmediatamente.</li>
                    <li>Revisa la actividad reciente de tu cuenta.</li>
                    <li>Verifica que tu correo electrónico no haya sido comprometido.</li>
                    <li>Contacta con nuestro equipo de soporte si necesitas ayuda.</li>
                </ul>
            </div>
            
            <div class="warning-box">
                <p>⚠️ <strong>IMPORTANTE:</strong> Si se registran 3 intentos fallidos adicionales después del desbloqueo automático, tu cuenta será desactivada y solo un administrador podrá reactivarla.</p>
            </div>
            
            <center>
                <a href="mailto:soporte@autonew.com" class="button">Contactar Soporte</a>
            </center>
        </div>
        
        <div class="footer">
            <p><strong>AUTONEW</strong> - Sistema de Gestión de Lavado Automotriz</p>
            <p>Este es un mensaje automático del sistema de seguridad.</p>
            <p style="font-size: 12px; color: #868e96; margin-top: 15px;">
                © 2025 AUTONEW. Todos los derechos reservados.<br>
                Si no solicitaste este correo, por favor ignóralo.
            </p>
        </div>
    </div>
</body>
</html>
                """
                
                text_message = f"""
Hola {self.nombre_completo},

ALERTA DE SEGURIDAD

Hemos detectado 3 intentos fallidos de inicio de sesión en tu cuenta de AUTONEW.

DETALLES:
• Usuario: {self.nombre_usuario}
• Fecha y hora: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}
• Estado: Cuenta bloqueada temporalmente por 15 minutos

Si fuiste tú quien intentó acceder:
- Tu cuenta ha sido bloqueada temporalmente por 15 minutos
- Podrás volver a intentar después de este tiempo

Si NO fuiste tú:
- Cambia tu contraseña inmediatamente
- Revisa la actividad reciente de tu cuenta
- Contacta a soporte si necesitas ayuda

IMPORTANTE: Si se registran 3 intentos fallidos adicionales, tu cuenta será desactivada.

Contacto: soporte@autonew.com

Equipo de Seguridad AUTONEW
                """
                
                msg = EmailMultiAlternatives(
                    subject='⚠️ Alerta de Seguridad - Intentos de Acceso a tu Cuenta',
                    body=text_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[self.correo]
                )
                msg.attach_alternative(html_message, "text/html")
                msg.send(fail_silently=True)
                
            except Exception as e:
                print(f"Error al enviar correo de alerta: {e}")
        
        # Segunda vez que llega a 3 intentos (después del bloqueo de 15 min)
        elif self.failed_login_attempts >= 6 and self.first_warning_sent:
            # DESACTIVAR LA CUENTA (solo admin puede activar)
            self.is_active = False
            self.lockout_time = None  # Ya no necesita bloqueo temporal
            
            # Enviar correo de cuenta desactivada
            try:
                html_message = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7fa; }}
        .email-container {{ max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); padding: 40px 30px; text-align: center; }}
        .header-icon {{ font-size: 64px; margin-bottom: 10px; }}
        .header h1 {{ color: #ffffff; margin: 0; font-size: 28px; font-weight: 600; }}
        .content {{ padding: 40px 30px; }}
        .greeting {{ font-size: 18px; color: #333333; margin-bottom: 20px; font-weight: 500; }}
        .critical-box {{ background: linear-gradient(135deg, #fee 0%, #fcc 100%); border: 2px solid #dc3545; padding: 25px; margin: 25px 0; border-radius: 8px; text-align: center; }}
        .critical-box .icon {{ font-size: 48px; margin-bottom: 15px; }}
        .critical-box h2 {{ color: #c0392b; margin: 0 0 10px 0; font-size: 22px; }}
        .critical-box p {{ color: #721c24; margin: 5px 0; font-size: 15px; }}
        .info-box {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 25px 0; }}
        .info-row {{ display: flex; align-items: center; margin: 12px 0; }}
        .info-icon {{ font-size: 20px; margin-right: 12px; width: 24px; }}
        .info-text {{ color: #495057; font-size: 15px; }}
        .info-text strong {{ color: #212529; }}
        .section {{ margin: 30px 0; }}
        .section-title {{ color: #dc3545; font-size: 18px; font-weight: 600; margin-bottom: 15px; border-bottom: 2px solid #e9ecef; padding-bottom: 8px; }}
        .step-box {{ background-color: #ffffff; border: 2px solid #e9ecef; padding: 20px; border-radius: 8px; margin: 15px 0; }}
        .step-box h3 {{ color: #495057; font-size: 16px; margin: 0 0 12px 0; }}
        .step-box ol {{ margin: 8px 0; padding-left: 20px; }}
        .step-box li {{ color: #495057; padding: 6px 0; line-height: 1.6; }}
        .support-box {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 8px; margin: 25px 0; text-align: center; }}
        .support-box h3 {{ margin: 0 0 15px 0; font-size: 20px; }}
        .support-box p {{ margin: 8px 0; font-size: 15px; }}
        .support-box a {{ color: #ffffff; font-weight: bold; text-decoration: none; font-size: 18px; }}
        .footer {{ background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e9ecef; }}
        .footer p {{ margin: 5px 0; color: #6c757d; font-size: 14px; }}
        .button {{ display: inline-block; padding: 14px 32px; background-color: #ffffff; color: #667eea !important; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 15px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        @media only screen and (max-width: 600px) {{
            .email-container {{ margin: 20px; }}
            .content {{ padding: 25px 20px; }}
            .header {{ padding: 30px 20px; }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="header-icon">🔒</div>
            <h1>Cuenta Desactivada</h1>
        </div>
        
        <div class="content">
            <p class="greeting">Hola <strong>{self.nombre_completo}</strong>,</p>
            
            <div class="critical-box">
                <div class="icon">🚨</div>
                <h2>Tu cuenta ha sido desactivada</h2>
                <p>Por razones de seguridad, tu cuenta en AUTONEW ha sido desactivada. Solo un administrador puede reactivarla.</p>
            </div>
            
            <div class="info-box">
                <div class="info-row">
                    <span class="info-icon">👤</span>
                    <span class="info-text"><strong>Usuario:</strong> {self.nombre_usuario}</span>
                </div>
                <div class="info-row">
                    <span class="info-icon">📅</span>
                    <span class="info-text"><strong>Fecha y hora:</strong> {timezone.now().strftime('%d/%m/%Y a las %H:%M:%S')}</span>
                </div>
                <div class="info-row">
                    <span class="info-icon">🔴</span>
                    <span class="info-text"><strong>Razón:</strong> Múltiples intentos fallidos de inicio de sesión</span>
                </div>
                <div class="info-row">
                    <span class="info-icon">🔢</span>
                    <span class="info-text"><strong>Intentos registrados:</strong> {self.failed_login_attempts} intentos fallidos</span>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">📋 Detalles del Incidente</h2>
                <p style="color: #495057; line-height: 1.6;">
                    Nuestro sistema de seguridad detectó múltiples intentos fallidos de acceso a tu cuenta, 
                    incluso después de un bloqueo temporal previo. Como medida de protección, tu cuenta ha 
                    sido desactivada automáticamente para prevenir accesos no autorizados. Solo un administrador 
                    puede reactivar tu cuenta.
                </p>
            </div>
            
            <div class="section">
                <h2 class="section-title">🔐 ¿Qué hacer ahora?</h2>
                
                <div class="step-box">
                    <h3>✅ Si reconoces estos intentos de acceso:</h3>
                    <ol>
                        <li>Contacta a nuestro equipo de soporte para reactivar tu cuenta</li>
                        <li>Te ayudaremos a restablecer tu contraseña de forma segura</li>
                        <li>Verifica que recuerdas correctamente tus credenciales</li>
                    </ol>
                </div>
                
                <div class="step-box">
                    <h3>⚠️ Si NO reconoces estos intentos:</h3>
                    <ol>
                        <li>Contacta <strong>INMEDIATAMENTE</strong> a nuestro equipo de soporte</li>
                        <li>Es posible que alguien esté intentando acceder a tu cuenta</li>
                        <li>Verifica que tu correo electrónico no haya sido comprometido</li>
                        <li>Cambia las contraseñas de tus otras cuentas por seguridad</li>
                    </ol>
                </div>
            </div>
            
            <div class="support-box">
                <h3>📞 Contacto de Soporte 24/7</h3>
                <p><strong>Email:</strong> <a href="mailto:soporte@autonew.com">soporte@autonew.com</a></p>
                <p>Responderemos a tu solicitud en menos de 24 horas</p>
                <a href="mailto:soporte@autonew.com" class="button">Contactar Ahora</a>
            </div>
            
            <p style="color: #6c757d; font-size: 14px; text-align: center; margin-top: 30px; line-height: 1.6;">
                <strong>Tu seguridad es nuestra prioridad.</strong><br>
                Lamentamos las molestias, pero estas medidas son necesarias para proteger tu información.
            </p>
        </div>
        
        <div class="footer">
            <p><strong>AUTONEW</strong> - Sistema de Gestión de Lavado Automotriz</p>
            <p>Este es un mensaje automático del sistema de seguridad.</p>
            <p style="font-size: 12px; color: #868e96; margin-top: 15px;">
                © 2025 AUTONEW. Todos los derechos reservados.<br>
                Si no solicitaste este correo, por favor contacta inmediatamente a soporte.
            </p>
        </div>
    </div>
</body>
</html>
                """
                
                text_message = f"""
Hola {self.nombre_completo},

CUENTA DESACTIVADA POR SEGURIDAD

Tu cuenta en AUTONEW ha sido DESACTIVADA por razones de seguridad.

DETALLES:
• Usuario: {self.nombre_usuario}
• Fecha y hora: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}
• Razón: Múltiples intentos fallidos de inicio de sesión
• Intentos registrados: {self.failed_login_attempts} intentos fallidos

¿QUÉ HACER AHORA?

Si reconoces estos intentos:
1. Contacta a soporte para reactivar tu cuenta
2. Te ayudaremos a restablecer tu contraseña

Si NO reconoces estos intentos:
1. Contacta INMEDIATAMENTE a soporte
2. Alguien puede estar intentando acceder a tu cuenta
3. Verifica tu correo electrónico

CONTACTO DE SOPORTE 24/7:
Email: soporte@autonew.com

Tu seguridad es nuestra prioridad.

Equipo de Seguridad AUTONEW
                """
                
                msg = EmailMultiAlternatives(
                    subject='🔒 Cuenta Desactivada por Seguridad - AUTONEW',
                    body=text_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[self.correo]
                )
                msg.attach_alternative(html_message, "text/html")
                msg.send(fail_silently=True)
                
            except Exception as e:
                print(f"Error al enviar correo de desactivación: {e}")
        
        self.save()
    
    def reset_failed_attempts(self):
        """Resetea el contador de intentos fallidos después de login exitoso"""
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.lockout_time = None
        self.first_warning_sent = False
        self.save()
    
    def can_attempt_login(self):
        """
        Verifica si el usuario puede intentar hacer login.
        Retorna True si puede, False si está bloqueado.
        """
        # Si la cuenta está desactivada, no puede intentar login
        if not self.is_active:
            return False
        
        # Si tiene lockout_time, verificar si han pasado 15 minutos
        if self.lockout_time:
            time_since_lockout = timezone.now() - self.lockout_time
            if time_since_lockout.total_seconds() > 900:  # 15 minutos = 900 segundos
                # Resetear solo el bloqueo temporal, pero mantener el contador y el flag de warning
                self.lockout_time = None
                # NO reseteamos failed_login_attempts ni first_warning_sent
                self.save()
                return True
            # Si no han pasado 15 minutos, está bloqueado temporalmente
            return False
        
        # Si no tiene lockout_time y está activo, puede intentar
        return True
    
    def get_remaining_attempts(self):
        """Obtiene el número de intentos restantes antes del bloqueo o desactivación"""
        if not self.first_warning_sent:
            # Primera fase: 3 intentos hasta bloqueo temporal
            return max(0, 3 - self.failed_login_attempts)
        else:
            # Segunda fase: 3 intentos más hasta desactivación (total 6)
            return max(0, 6 - self.failed_login_attempts)
    
    def get_lockout_remaining_time(self):
        """Obtiene el tiempo restante de bloqueo en minutos"""
        if not self.lockout_time:
            return 0
        
        time_since_lockout = timezone.now() - self.lockout_time
        remaining_seconds = 900 - time_since_lockout.total_seconds()  # 15 minutos = 900 segundos
        
        if remaining_seconds <= 0:
            return 0
        
        return int(remaining_seconds / 60) + 1  # Redondear hacia arriba
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'


class Servicio(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    nombre_servicio = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField()
    precio = models.FloatField()

class EmpresaServicio(models.Model):
    empresa = models.ForeignKey('Empresa', on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.empresa.nombre_empresa} - {self.servicio.nombre_servicio}"

class Empresa(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    nombre_empresa = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15)
    email = models.EmailField()
    contrasena = models.CharField(max_length=255, default='temp_password')  # Campo para la contraseña con default temporal
    token_reset = models.CharField(max_length=255, null=True, blank=True)  # Token para reset de contraseña
    fecha_registro = models.DateTimeField(default=timezone.now)  # Fecha de registro con default
    verificada = models.BooleanField(default=False)  # Campo para verificación de empresa
    
    # Coordenadas para el mapa
    latitud = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitud = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Campos para control de intentos fallidos de login (igual que Usuario)
    failed_login_attempts = models.IntegerField(default=0)  # Contador de intentos fallidos
    last_failed_login = models.DateTimeField(null=True, blank=True)  # Última vez que falló el login
    lockout_time = models.DateTimeField(null=True, blank=True)  # Tiempo de bloqueo temporal (15 min)
    first_warning_sent = models.BooleanField(default=False)  # Si ya se envió el primer aviso de seguridad
    is_active = models.BooleanField(default=True)  # Si la cuenta está activa
    
    # ==================== INFORMACIÓN BANCARIA PARA PAGOS ====================
    # Información del titular de la cuenta
    titular_cuenta = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Nombre completo del titular de la cuenta bancaria",
        verbose_name="Titular de la cuenta"
    )
    tipo_documento_titular = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ('CC', 'Cédula de Ciudadanía'),
            ('NIT', 'NIT'),
            ('CE', 'Cédula de Extranjería'),
            ('PAS', 'Pasaporte'),
        ],
        help_text="Tipo de documento del titular",
        verbose_name="Tipo de documento"
    )
    numero_documento_titular = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Número de documento del titular de la cuenta",
        verbose_name="Número de documento"
    )
    
    # Información de la cuenta bancaria
    banco = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Nombre del banco donde está la cuenta",
        verbose_name="Banco"
    )
    tipo_cuenta = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ('ahorros', 'Cuenta de Ahorros'),
            ('corriente', 'Cuenta Corriente'),
        ],
        help_text="Tipo de cuenta bancaria",
        verbose_name="Tipo de cuenta"
    )
    numero_cuenta = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Número de cuenta bancaria para recibir pagos",
        verbose_name="Número de cuenta"
    )
    
    # Información adicional para pagos internacionales o alternativas
    swift_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Código SWIFT del banco (para transferencias internacionales)",
        verbose_name="Código SWIFT"
    )
    iban = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Número IBAN (para pagos internacionales)",
        verbose_name="IBAN"
    )
    
    # Información fiscal
    nit_empresa = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="NIT de la empresa",
        verbose_name="NIT"
    )
    razon_social = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Razón social de la empresa (si es diferente al nombre comercial)",
        verbose_name="Razón social"
    )
    regimen_tributario = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('simplificado', 'Régimen Simplificado'),
            ('comun', 'Régimen Común'),
            ('especial', 'Régimen Especial'),
        ],
        help_text="Régimen tributario de la empresa",
        verbose_name="Régimen tributario"
    )
    
    # Información de contacto para temas de pagos
    email_facturacion = models.EmailField(
        blank=True,
        null=True,
        help_text="Email para enviar facturas y notificaciones de pagos",
        verbose_name="Email de facturación"
    )
    telefono_facturacion = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Teléfono de contacto para temas de facturación",
        verbose_name="Teléfono de facturación"
    )
    responsable_pagos = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Nombre de la persona responsable de gestionar los pagos",
        verbose_name="Responsable de pagos"
    )
    
    # Validación y verificación de datos bancarios
    datos_bancarios_verificados = models.BooleanField(
        default=False,
        help_text="Indica si los datos bancarios han sido verificados por el administrador",
        verbose_name="Datos bancarios verificados"
    )
    fecha_verificacion_bancaria = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se verificaron los datos bancarios",
        verbose_name="Fecha de verificación bancaria"
    )
    verificado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='empresas_verificadas',
        help_text="Administrador que verificó los datos bancarios",
        verbose_name="Verificado por"
    )
    
    # Notas adicionales
    notas_bancarias = models.TextField(
        blank=True,
        null=True,
        help_text="Notas adicionales sobre la información bancaria o instrucciones especiales para pagos",
        verbose_name="Notas bancarias"
    )
    
    servicios = models.ManyToManyField(Servicio, through=EmpresaServicio)

    def __str__(self):
        return self.nombre_empresa
    
    def datos_bancarios_completos(self):
        """
        Verifica si los datos bancarios mínimos están completos
        para poder realizar pagos a la empresa
        """
        campos_requeridos = [
            self.titular_cuenta,
            self.tipo_documento_titular,
            self.numero_documento_titular,
            self.banco,
            self.tipo_cuenta,
            self.numero_cuenta,
        ]
        return all(campos_requeridos)
    
    def puede_recibir_pagos(self):
        """
        Verifica si la empresa puede recibir pagos
        (datos bancarios completos y verificados)
        """
        return self.datos_bancarios_completos() and self.datos_bancarios_verificados
    
    def obtener_info_bancaria(self):
        """
        Retorna un diccionario con la información bancaria
        formateada para mostrar o usar en reportes
        """
        return {
            'titular': self.titular_cuenta,
            'documento': f"{self.get_tipo_documento_titular_display()} {self.numero_documento_titular}" if self.tipo_documento_titular else None,
            'banco': self.banco,
            'tipo_cuenta': self.get_tipo_cuenta_display() if self.tipo_cuenta else None,
            'numero_cuenta': self.numero_cuenta,
            'swift': self.swift_code,
            'iban': self.iban,
            'verificado': self.datos_bancarios_verificados,
            'fecha_verificacion': self.fecha_verificacion_bancaria,
        }
    
    def increment_failed_attempts(self):
        """
        Incrementa el contador de intentos fallidos de login para empresas.
        Lógica:
        - 3 intentos fallidos: Bloqueo temporal de 15 minutos + correo de alerta
        - Después de 15 minutos, si falla 3 veces más: Desactivar cuenta + correo
        """
        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings
        
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        
        # Primera vez que llega a 3 intentos fallidos
        if self.failed_login_attempts == 3 and not self.first_warning_sent:
            self.lockout_time = timezone.now()  # Iniciar bloqueo temporal de 15 minutos
            self.first_warning_sent = True
            
            # Enviar correo de alerta
            try:
                html_message = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7fa; }}
        .email-container {{ max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center; }}
        .header-icon {{ font-size: 64px; margin-bottom: 10px; }}
        .header h1 {{ color: #ffffff; margin: 0; font-size: 28px; font-weight: 600; }}
        .content {{ padding: 40px 30px; }}
        .greeting {{ font-size: 18px; color: #333333; margin-bottom: 20px; font-weight: 500; }}
        .alert-box {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin: 25px 0; border-radius: 6px; }}
        .alert-box strong {{ color: #856404; display: block; margin-bottom: 10px; font-size: 16px; }}
        .info-box {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 25px 0; }}
        .info-row {{ display: flex; align-items: center; margin: 12px 0; }}
        .info-icon {{ font-size: 20px; margin-right: 12px; width: 24px; }}
        .info-text {{ color: #495057; font-size: 15px; }}
        .info-text strong {{ color: #212529; }}
        .section {{ margin: 30px 0; }}
        .section-title {{ color: #667eea; font-size: 18px; font-weight: 600; margin-bottom: 15px; border-bottom: 2px solid #e9ecef; padding-bottom: 8px; }}
        .action-list {{ list-style: none; padding: 0; }}
        .action-list li {{ padding: 12px 0; padding-left: 30px; position: relative; color: #495057; line-height: 1.6; }}
        .action-list li:before {{ content: "✓"; position: absolute; left: 0; color: #28a745; font-weight: bold; font-size: 18px; }}
        .warning-box {{ background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 20px; margin: 25px 0; border-radius: 6px; }}
        .warning-box p {{ margin: 0; color: #721c24; font-weight: 500; }}
        .footer {{ background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e9ecef; }}
        .footer p {{ margin: 5px 0; color: #6c757d; font-size: 14px; }}
        .button {{ display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff !important; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0; box-shadow: 0 4px 12px rgba(102,126,234,0.3); }}
        @media only screen and (max-width: 600px) {{
            .email-container {{ margin: 20px; }}
            .content {{ padding: 25px 20px; }}
            .header {{ padding: 30px 20px; }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="header-icon">⚠️</div>
            <h1>Alerta de Seguridad Empresarial</h1>
        </div>
        
        <div class="content">
            <p class="greeting">Hola, equipo de <strong>{self.nombre_empresa}</strong>,</p>
            
            <div class="alert-box">
                <strong>⚡ Hemos detectado actividad inusual en su cuenta empresarial</strong>
                <p style="margin: 8px 0 0 0; color: #856404;">Se registraron 3 intentos fallidos de inicio de sesión en la cuenta de su empresa en AUTONEW.</p>
            </div>
            
            <div class="info-box">
                <div class="info-row">
                    <span class="info-icon">🏢</span>
                    <span class="info-text"><strong>Empresa:</strong> {self.nombre_empresa}</span>
                </div>
                <div class="info-row">
                    <span class="info-icon">📧</span>
                    <span class="info-text"><strong>Email:</strong> {self.email}</span>
                </div>
                <div class="info-row">
                    <span class="info-icon">📅</span>
                    <span class="info-text"><strong>Fecha y hora:</strong> {timezone.now().strftime('%d/%m/%Y a las %H:%M:%S')}</span>
                </div>
                <div class="info-row">
                    <span class="info-icon">🔒</span>
                    <span class="info-text"><strong>Estado:</strong> Cuenta bloqueada temporalmente</span>
                </div>
                <div class="info-row">
                    <span class="info-icon">⏱️</span>
                    <span class="info-text"><strong>Duración del bloqueo:</strong> 15 minutos</span>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">✅ Si fue personal autorizado quien intentó acceder:</h2>
                <ul class="action-list">
                    <li>Su cuenta ha sido bloqueada temporalmente por 15 minutos como medida de seguridad preventiva.</li>
                    <li>Podrán volver a intentar iniciar sesión después de transcurrido este tiempo.</li>
                    <li>Asegúrense de verificar las credenciales correctas con el personal autorizado.</li>
                </ul>
            </div>
            
            <div class="section">
                <h2 class="section-title">🚨 Si NO fue personal autorizado:</h2>
                <ul class="action-list">
                    <li>Recomendamos cambiar la contraseña de acceso inmediatamente.</li>
                    <li>Revisen la actividad reciente de la cuenta empresarial.</li>
                    <li>Verifiquen que el correo electrónico de la empresa no haya sido comprometido.</li>
                    <li>Contacten con nuestro equipo de soporte si necesitan ayuda.</li>
                </ul>
            </div>
            
            <div class="warning-box">
                <p>⚠️ <strong>IMPORTANTE:</strong> Si se registran 3 intentos fallidos adicionales después del desbloqueo automático, su cuenta será desactivada y solo un administrador podrá reactivarla.</p>
            </div>
            
            <center>
                <a href="mailto:soporte@autonew.com" class="button">Contactar Soporte</a>
            </center>
        </div>
        
        <div class="footer">
            <p><strong>AUTONEW</strong> - Sistema de Gestión de Lavado Automotriz</p>
            <p>Este es un mensaje automático del sistema de seguridad.</p>
            <p style="font-size: 12px; color: #868e96; margin-top: 15px;">
                © 2025 AUTONEW. Todos los derechos reservados.<br>
                Si no solicitaron este correo, por favor ignórenlo y contacten a soporte.
            </p>
        </div>
    </div>
</body>
</html>
                """
                
                text_message = f"""
Hola, equipo de {self.nombre_empresa},

ALERTA DE SEGURIDAD EMPRESARIAL

Se detectaron 3 intentos fallidos de inicio de sesión en su cuenta empresarial de AUTONEW.

DETALLES:
• Empresa: {self.nombre_empresa}
• Email: {self.email}
• Fecha y hora: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}
• Estado: Cuenta bloqueada temporalmente por 15 minutos

Si fue personal autorizado:
- Su cuenta ha sido bloqueada temporalmente por 15 minutos
- Podrán volver a intentar después de este tiempo

Si NO fue personal autorizado:
- Cambien la contraseña inmediatamente
- Revisen la actividad reciente de su cuenta
- Contacten a soporte si necesitan ayuda

IMPORTANTE: Si se registran 3 intentos fallidos adicionales, su cuenta será desactivada.

Contacto: soporte@autonew.com

Equipo de Seguridad AUTONEW
                """
                
                msg = EmailMultiAlternatives(
                    subject='⚠️ Alerta de Seguridad - Intentos de Acceso a Cuenta Empresarial',
                    body=text_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[self.email]
                )
                msg.attach_alternative(html_message, "text/html")
                msg.send(fail_silently=True)
                
            except Exception as e:
                print(f"Error al enviar correo de alerta empresarial: {e}")
        
        # Segunda vez que llega a 3 intentos (después del bloqueo de 15 min)
        elif self.failed_login_attempts >= 6 and self.first_warning_sent:
            # DESACTIVAR LA CUENTA (solo admin puede activar)
            self.is_active = False
            self.lockout_time = None  # Ya no necesita bloqueo temporal
            
            # Enviar correo de cuenta desactivada
            try:
                html_message = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7fa; }}
        .email-container {{ max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); padding: 40px 30px; text-align: center; }}
        .header-icon {{ font-size: 64px; margin-bottom: 10px; }}
        .header h1 {{ color: #ffffff; margin: 0; font-size: 28px; font-weight: 600; }}
        .content {{ padding: 40px 30px; }}
        .greeting {{ font-size: 18px; color: #333333; margin-bottom: 20px; font-weight: 500; }}
        .critical-box {{ background: linear-gradient(135deg, #fee 0%, #fcc 100%); border: 2px solid #dc3545; padding: 25px; margin: 25px 0; border-radius: 8px; text-align: center; }}
        .critical-box .icon {{ font-size: 48px; margin-bottom: 15px; }}
        .critical-box h2 {{ color: #c0392b; margin: 0 0 10px 0; font-size: 22px; }}
        .critical-box p {{ color: #721c24; margin: 5px 0; font-size: 15px; }}
        .info-box {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 25px 0; }}
        .info-row {{ display: flex; align-items: center; margin: 12px 0; }}
        .info-icon {{ font-size: 20px; margin-right: 12px; width: 24px; }}
        .info-text {{ color: #495057; font-size: 15px; }}
        .info-text strong {{ color: #212529; }}
        .section {{ margin: 30px 0; }}
        .section-title {{ color: #dc3545; font-size: 18px; font-weight: 600; margin-bottom: 15px; border-bottom: 2px solid #e9ecef; padding-bottom: 8px; }}
        .step-box {{ background-color: #ffffff; border: 2px solid #e9ecef; padding: 20px; border-radius: 8px; margin: 15px 0; }}
        .step-box h3 {{ color: #495057; font-size: 16px; margin: 0 0 12px 0; }}
        .step-box ol {{ margin: 8px 0; padding-left: 20px; }}
        .step-box li {{ color: #495057; padding: 6px 0; line-height: 1.6; }}
        .support-box {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 8px; margin: 25px 0; text-align: center; }}
        .support-box h3 {{ margin: 0 0 15px 0; font-size: 20px; }}
        .support-box p {{ margin: 8px 0; font-size: 15px; }}
        .support-box a {{ color: #ffffff; font-weight: bold; text-decoration: none; font-size: 18px; }}
        .footer {{ background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e9ecef; }}
        .footer p {{ margin: 5px 0; color: #6c757d; font-size: 14px; }}
        .button {{ display: inline-block; padding: 14px 32px; background-color: #ffffff; color: #667eea !important; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 15px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        @media only screen and (max-width: 600px) {{
            .email-container {{ margin: 20px; }}
            .content {{ padding: 25px 20px; }}
            .header {{ padding: 30px 20px; }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="header-icon">🔒</div>
            <h1>Cuenta Empresarial Desactivada</h1>
        </div>
        
        <div class="content">
            <p class="greeting">Hola, equipo de <strong>{self.nombre_empresa}</strong>,</p>
            
            <div class="critical-box">
                <div class="icon">🚨</div>
                <h2>Su cuenta empresarial ha sido desactivada</h2>
                <p>Por razones de seguridad, la cuenta de su empresa en AUTONEW ha sido desactivada. Solo un administrador puede reactivarla.</p>
            </div>
            
            <div class="info-box">
                <div class="info-row">
                    <span class="info-icon">🏢</span>
                    <span class="info-text"><strong>Empresa:</strong> {self.nombre_empresa}</span>
                </div>
                <div class="info-row">
                    <span class="info-icon">📧</span>
                    <span class="info-text"><strong>Email:</strong> {self.email}</span>
                </div>
                <div class="info-row">
                    <span class="info-icon">📅</span>
                    <span class="info-text"><strong>Fecha y hora:</strong> {timezone.now().strftime('%d/%m/%Y a las %H:%M:%S')}</span>
                </div>
                <div class="info-row">
                    <span class="info-icon">🔴</span>
                    <span class="info-text"><strong>Razón:</strong> Múltiples intentos fallidos de inicio de sesión</span>
                </div>
                <div class="info-row">
                    <span class="info-icon">🔢</span>
                    <span class="info-text"><strong>Intentos registrados:</strong> {self.failed_login_attempts} intentos fallidos</span>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">📋 Detalles del Incidente</h2>
                <p style="color: #495057; line-height: 1.6;">
                    Nuestro sistema de seguridad detectó múltiples intentos fallidos de acceso a la cuenta de su empresa, 
                    incluso después de un bloqueo temporal previo. Como medida de protección, la cuenta ha 
                    sido desactivada automáticamente para prevenir accesos no autorizados. Solo un administrador 
                    puede reactivar su cuenta.
                </p>
            </div>
            
            <div class="section">
                <h2 class="section-title">🔐 ¿Qué hacer ahora?</h2>
                
                <div class="step-box">
                    <h3>✅ Si reconocen estos intentos de acceso:</h3>
                    <ol>
                        <li>Contacten a nuestro equipo de soporte para reactivar su cuenta</li>
                        <li>Les ayudaremos a restablecer la contraseña de forma segura</li>
                        <li>Verifiquen las credenciales con su personal autorizado</li>
                    </ol>
                </div>
                
                <div class="step-box">
                    <h3>⚠️ Si NO reconocen estos intentos:</h3>
                    <ol>
                        <li>Contacten <strong>INMEDIATAMENTE</strong> a nuestro equipo de soporte</li>
                        <li>Es posible que alguien esté intentando acceder a su cuenta empresarial</li>
                        <li>Verifiquen que el correo electrónico de la empresa no haya sido comprometido</li>
                        <li>Cambien las contraseñas de acceso de todas sus cuentas por seguridad</li>
                    </ol>
                </div>
            </div>
            
            <div class="support-box">
                <h3>📞 Contacto de Soporte 24/7</h3>
                <p><strong>Email:</strong> <a href="mailto:soporte@autonew.com">soporte@autonew.com</a></p>
                <p>Responderemos a su solicitud en menos de 24 horas</p>
                <a href="mailto:soporte@autonew.com" class="button">Contactar Ahora</a>
            </div>
            
            <p style="color: #6c757d; font-size: 14px; text-align: center; margin-top: 30px; line-height: 1.6;">
                <strong>La seguridad de su empresa es nuestra prioridad.</strong><br>
                Lamentamos las molestias, pero estas medidas son necesarias para proteger su información.
            </p>
        </div>
        
        <div class="footer">
            <p><strong>AUTONEW</strong> - Sistema de Gestión de Lavado Automotriz</p>
            <p>Este es un mensaje automático del sistema de seguridad.</p>
            <p style="font-size: 12px; color: #868e96; margin-top: 15px;">
                © 2025 AUTONEW. Todos los derechos reservados.<br>
                Si no solicitaron este correo, por favor contacten inmediatamente a soporte.
            </p>
        </div>
    </div>
</body>
</html>
                """
                
                text_message = f"""
Hola, equipo de {self.nombre_empresa},

CUENTA EMPRESARIAL DESACTIVADA POR SEGURIDAD

La cuenta de su empresa en AUTONEW ha sido DESACTIVADA por razones de seguridad.

DETALLES:
• Empresa: {self.nombre_empresa}
• Email: {self.email}
• Fecha y hora: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}
• Razón: Múltiples intentos fallidos de inicio de sesión
• Intentos registrados: {self.failed_login_attempts} intentos fallidos

¿QUÉ HACER AHORA?

Si reconocen estos intentos:
1. Contacten a soporte para reactivar su cuenta
2. Les ayudaremos a restablecer la contraseña

Si NO reconocen estos intentos:
1. Contacten INMEDIATAMENTE a soporte
2. Alguien puede estar intentando acceder a su cuenta
3. Verifiquen el correo electrónico de la empresa

CONTACTO DE SOPORTE 24/7:
Email: soporte@autonew.com

La seguridad de su empresa es nuestra prioridad.

Equipo de Seguridad AUTONEW
                """
                
                msg = EmailMultiAlternatives(
                    subject='🔒 Cuenta Empresarial Desactivada por Seguridad - AUTONEW',
                    body=text_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[self.email]
                )
                msg.attach_alternative(html_message, "text/html")
                msg.send(fail_silently=True)
                
            except Exception as e:
                print(f"Error al enviar correo de desactivación empresarial: {e}")
        
        self.save()
    
    def reset_failed_attempts(self):
        """Resetea el contador de intentos fallidos después de login exitoso"""
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.lockout_time = None
        self.first_warning_sent = False
        self.save()
    
    def can_attempt_login(self):
        """
        Verifica si la empresa puede intentar hacer login.
        Retorna True si puede, False si está bloqueado.
        """
        # Si la cuenta está desactivada, no puede intentar login
        if not self.is_active:
            return False
        
        # Si tiene lockout_time, verificar si han pasado 15 minutos
        if self.lockout_time:
            time_since_lockout = timezone.now() - self.lockout_time
            if time_since_lockout.total_seconds() > 900:  # 15 minutos = 900 segundos
                # Resetear solo el bloqueo temporal, pero mantener el contador y el flag de warning
                self.lockout_time = None
                # NO reseteamos failed_login_attempts ni first_warning_sent
                self.save()
                return True
            # Si no han pasado 15 minutos, está bloqueado temporalmente
            return False
        
        # Si no tiene lockout_time y está activo, puede intentar
        return True
    
    def get_remaining_attempts(self):
        """Obtiene el número de intentos restantes antes del bloqueo o desactivación"""
        if not self.first_warning_sent:
            # Primera fase: 3 intentos hasta bloqueo temporal
            return max(0, 3 - self.failed_login_attempts)
        else:
            # Segunda fase: 3 intentos más hasta desactivación (total 6)
            return max(0, 6 - self.failed_login_attempts)
    
    def get_lockout_remaining_time(self):
        """Obtiene el tiempo restante de bloqueo en minutos"""
        if not self.lockout_time:
            return 0
        
        time_since_lockout = timezone.now() - self.lockout_time
        remaining_seconds = 900 - time_since_lockout.total_seconds()  # 15 minutos = 900 segundos
        
        if remaining_seconds <= 0:
            return 0
        
        return int(remaining_seconds / 60) + 1  # Redondear hacia arriba
    



class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    numero_reserva = models.CharField(max_length=15, unique=True, blank=True, null=True, help_text="Número único de reserva generado automáticamente")
    fecha = models.DateField()
    hora = models.TimeField()
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('cancelada', 'Cancelada'),
    ]
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE) 
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    servicios = models.ManyToManyField(Servicio, through='ReservaServicio')
    
    # Campos existentes para suscripciones individuales
    suscripcion_utilizada = models.ForeignKey('SuscripcionUsuario', on_delete=models.SET_NULL, null=True, blank=True)
    es_pago_individual = models.BooleanField(default=False)  # True si no es parte de una suscripción
    
    # NUEVOS CAMPOS para soportar reservas empresariales
    suscripcion_empresarial = models.ForeignKey('SuscripcionEmpresarial', on_delete=models.SET_NULL, null=True, blank=True)
    es_reserva_empresarial = models.BooleanField(default=False)

    # Indica si se pagó a la empresa el valor de la reserva
    pagado_empresa = models.BooleanField(
        default=False,
        help_text="Indica si el pago correspondiente a la reserva fue transferido/pagado a la empresa",
        verbose_name="Pagado a la empresa"
    )
    
    # Campos específicos para reservas empresariales
    placa_vehiculo = models.CharField(max_length=20, blank=True, null=True)
    tipo_vehiculo = models.CharField(max_length=50, blank=True, choices=[
        ('sedan', 'Sedán'),
        ('suv', 'SUV'),
        ('camioneta', 'Camioneta'),
        ('bus', 'Bus'),
        ('microbus', 'Microbús'),
        ('camion', 'Camión'),
        ('taxi', 'Taxi'),
        ('moto', 'Motocicleta'),
    ])
    conductor_asignado = models.CharField(max_length=255, blank=True)
    observaciones_empresariales = models.TextField(blank=True)
    
    def clean(self):
        """Validación para asegurar que no se asignen ambos tipos de suscripción"""
        if self.suscripcion_utilizada and self.suscripcion_empresarial:
            raise ValidationError("Una reserva no puede tener ambos tipos de suscripción")
    
    def generar_numero_reserva(self):
        """
        Genera un número único de reserva en formato ANW-B9636010
        ANW = prefijo fijo
        B = tipo de reserva (B=básica, E=empresarial)
        9636010 = número aleatorio de 7 dígitos
        """
        import random
        import string
        
        # Determinar el tipo de reserva
        tipo_reserva = 'E' if self.es_reserva_empresarial else 'B'
        
        # Generar número aleatorio de 7 dígitos
        while True:
            numero_aleatorio = ''.join([str(random.randint(0, 9)) for _ in range(7)])
            numero_propuesto = f"ANW-{tipo_reserva}{numero_aleatorio}"
            
            # Verificar que no exista en la base de datos
            if not Reserva.objects.filter(numero_reserva=numero_propuesto).exists():
                return numero_propuesto
    
    def save(self, *args, **kwargs):
        """
        Sobrescribir save para generar automáticamente el número de reserva
        """
        if not self.numero_reserva:
            self.numero_reserva = self.generar_numero_reserva()
        super().save(*args, **kwargs)
    
    def calcular_total_reserva(self):
        """
        Calcula el total de la reserva sumando todos los servicios con sus precios aplicados
        """
        reserva_servicios = self.reservaservicio_set.all()
        total = sum([float(rs.precio_aplicado) for rs in reserva_servicios if rs.precio_aplicado])
        return total
    
    def obtener_detalle_servicios(self):
        """
        Retorna un diccionario con el detalle de servicios organizados por tipo
        """
        reserva_servicios = self.reservaservicio_set.all()
        
        detalle = {
            'servicios_plan': [],
            'servicios_adicionales': [],
            'servicios_empresariales': [],
            'total': 0,
            'total_original': 0,  # Total sin descuentos (para pago a empresas)
            'ahorro_total': 0,
        }
        
        for rs in reserva_servicios:
            # Si precio_original es NULL o 0, usar precio_aplicado o el precio del servicio
            precio_orig = float(rs.precio_original) if rs.precio_original else (
                float(rs.precio_aplicado) if rs.precio_aplicado else float(rs.servicio.precio)
            )
            precio_aplic = float(rs.precio_aplicado) if rs.precio_aplicado else precio_orig
            
            servicio_info = {
                'nombre': rs.servicio.nombre_servicio,
                'precio_original': precio_orig,
                'precio_aplicado': precio_aplic,
                'descuento': float(rs.obtener_descuento_aplicado()),
                'ahorro': max(0, precio_orig - precio_aplic),  # Calcular ahorro basado en valores actuales
            }
            
            if rs.es_servicio_plan and not self.es_reserva_empresarial:
                detalle['servicios_plan'].append(servicio_info)
            elif self.es_reserva_empresarial:
                detalle['servicios_empresariales'].append(servicio_info)
            else:
                detalle['servicios_adicionales'].append(servicio_info)
            
            detalle['total'] += precio_aplic
            detalle['total_original'] += precio_orig
            detalle['ahorro_total'] += servicio_info['ahorro']
        
        return detalle

    def __str__(self):
        numero = self.numero_reserva if self.numero_reserva else f"ID-{self.id_reserva}"
        if self.es_reserva_empresarial and self.placa_vehiculo:
            return f"{numero} - Empresarial - {self.placa_vehiculo}"
        return f"{numero} - {self.usuario.nombre_usuario}"

class ReservaServicio(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    
    # Campos para manejo empresarial
    descuento_empresarial = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0, 
        help_text="Descuento empresarial en porcentaje"
    )
    
    # Campos para manejo de planes individuales
    es_servicio_plan = models.BooleanField(
        default=False, 
        help_text="Indica si este servicio es parte del plan individual del usuario"
    )
    descuento_plan_individual = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        help_text="Descuento del plan individual en porcentaje (desde PlanServicio)"
    )
    
    # Precio calculado (se guarda al crear/actualizar)
    precio_aplicado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="Precio final aplicado con descuentos"
    )
    precio_original = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Precio original del servicio (sin descuentos)"
    )
    
    def calcular_precio_aplicado(self):
        """
        Calcula el precio aplicado según el tipo de reserva y descuentos.
        
        Prioridad:
        1. Si es servicio de plan individual -> aplicar descuento_plan_individual
        2. Si es reserva empresarial -> aplicar descuento_empresarial
        3. Si es servicio adicional -> precio completo sin descuento
        """
        precio_base = float(self.servicio.precio)
        self.precio_original = precio_base
        
        # Caso 1: Servicio incluido en plan individual (NO empresarial)
        if self.es_servicio_plan and not self.reserva.es_reserva_empresarial:
            if self.descuento_plan_individual > 0:
                descuento = (precio_base * float(self.descuento_plan_individual)) / 100
                self.precio_aplicado = precio_base - descuento
            else:
                self.precio_aplicado = precio_base
        
        # Caso 2: Reserva empresarial con descuento
        elif self.reserva.es_reserva_empresarial and self.descuento_empresarial > 0:
            descuento = (precio_base * float(self.descuento_empresarial)) / 100
            self.precio_aplicado = precio_base - descuento
        
        # Caso 3: Servicio adicional sin descuento
        else:
            self.precio_aplicado = precio_base
        
        return self.precio_aplicado
    
    def obtener_descuento_aplicado(self):
        """Retorna el porcentaje de descuento aplicado según el contexto"""
        if self.es_servicio_plan and not self.reserva.es_reserva_empresarial:
            return self.descuento_plan_individual
        elif self.reserva.es_reserva_empresarial:
            return self.descuento_empresarial
        return 0
    
    def obtener_ahorro(self):
        """Calcula el ahorro obtenido por el descuento"""
        if self.precio_original and self.precio_aplicado:
            return float(self.precio_original) - float(self.precio_aplicado)
        return 0
    
    def save(self, *args, **kwargs):
        """
        Sobrescribir save para calcular automáticamente el precio aplicado
        antes de guardar en la base de datos
        """
        self.calcular_precio_aplicado()
        super().save(*args, **kwargs)
    
    def __str__(self):
        tipo = ""
        if self.es_servicio_plan:
            tipo = " (Plan)"
        elif self.reserva.es_reserva_empresarial:
            tipo = " (Empresarial)"
        else:
            tipo = " (Adicional)"
        
        return f"Reserva {self.reserva.id_reserva} - {self.servicio.nombre_servicio}{tipo} - ${self.precio_aplicado}"
    
    class Meta:
        verbose_name = 'Servicio de Reserva'
        verbose_name_plural = 'Servicios de Reservas'




class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    fecha_pago = models.DateField(auto_now_add=True)
    monto = models.FloatField()
    metodo_pago = models.CharField(max_length=50) 
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE) 


    
class PasarelaDePago(models.Model):
    id_pasarela = models.AutoField(primary_key=True)
    nombre_pasarela = models.CharField(max_length=100)
    estado_transaccion = models.CharField(max_length=50)
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE)



# Modelo Mensaje o Queja (PQRS)
class MensajeQueja(models.Model):
    TIPOS_PQRS = [
        ('peticion', 'Petición'),
        ('queja', 'Queja'),
        ('reclamo', 'Reclamo'),
        ('sugerencia', 'Sugerencia'),
    ]
    
    NIVELES_URGENCIA = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    ESTADOS_PQRS = [
        ('recibido', 'Recibido'),
        ('en_proceso', 'En Proceso'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
    ]

    id_mensaje = models.AutoField(primary_key=True)
    
    # Campos del formulario PQRS
    tipo_pqrs = models.CharField(max_length=20, choices=TIPOS_PQRS)
    urgencia = models.CharField(max_length=20, choices=NIVELES_URGENCIA, default='media')
    nombre_contacto = models.CharField(max_length=255, blank=True, null=True)
    email_contacto = models.EmailField(blank=True, null=True)
    
    # Servicio relacionado (puede ser de la BD o categorías fijas)
    servicio_relacionado = models.CharField(max_length=100, blank=True, null=True)
    servicio_bd = models.ForeignKey(Servicio, on_delete=models.SET_NULL, null=True, blank=True, 
                                   help_text="Servicio seleccionado de la base de datos")
    
    # Contenido principal
    contenido = models.TextField()
    
    # Campos de seguimiento
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PQRS, default='recibido')
    respuesta = models.TextField(blank=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    
    # Usuario (puede ser null para PQRS anónimas)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    
    # Campos adicionales para seguimiento
    numero_radicado = models.CharField(max_length=20, unique=True, null=True, blank=True)
    acepto_terminos = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Generar número de radicado automáticamente
        if not self.numero_radicado:
            from django.utils import timezone
            from datetime import datetime, date
            
            fecha = timezone.now().strftime('%Y%m%d')
            
            # Obtener el inicio y fin del día actual para evitar problemas con SQLite
            hoy = date.today()
            inicio_dia = datetime.combine(hoy, datetime.min.time())
            fin_dia = datetime.combine(hoy, datetime.max.time())
            
            # Hacer timezone-aware
            if timezone.is_aware(timezone.now()):
                inicio_dia = timezone.make_aware(inicio_dia)
                fin_dia = timezone.make_aware(fin_dia)
            
            # Contar registros del día usando rango en lugar de __date
            count = MensajeQueja.objects.filter(
                fecha_envio__gte=inicio_dia,
                fecha_envio__lte=fin_dia
            ).count() + 1
            
            self.numero_radicado = f"PQRS-{fecha}-{count:04d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_tipo_pqrs_display()} - {self.numero_radicado}"
    
    class Meta:
        verbose_name = 'PQRS'
        verbose_name_plural = 'PQRS'
        ordering = ['-fecha_envio']   

class Comentario(models.Model):
    id_comentario = models.AutoField(primary_key=True)
    comentario = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)


# Nuevos modelos para manejar planes de suscripción
class Plan(models.Model):
    TIPOS_PLAN = [
        ('basico', 'Lavado Básico'),
        ('premium', 'Limpieza Premium'),
        ('completo', 'Limpieza Completa'),
    ]
    
    id_plan = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPOS_PLAN)
    descripcion = models.TextField()
    precio_mensual = models.DecimalField(max_digits=10, decimal_places=2)
    servicios_incluidos = models.ManyToManyField(
        Servicio, 
        through='PlanServicio',
        related_name='planes'
    )
    cantidad_servicios_mes = models.IntegerField(help_text="Cantidad de servicios permitidos por mes. 0 = ilimitado")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Características del plan
    incluye_lavado_asientos = models.BooleanField(default=True)
    incluye_aspirado = models.BooleanField(default=True)
    incluye_lavado_exterior = models.BooleanField(default=True)
    incluye_lavado_interior_humedo = models.BooleanField(default=False)
    incluye_encerado = models.BooleanField(default=False)
    incluye_detallado_completo = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio_mensual}"
    
    class Meta:
        ordering = ['precio_mensual']


class PlanServicio(models.Model):
    """
    Tabla intermedia para relacionar Planes con Servicios,
    incluyendo el porcentaje de descuento aplicado a cada servicio.
    """
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='plan_servicios')
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='servicio_planes')
    porcentaje_descuento = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=0.00,
        help_text="Porcentaje de descuento aplicado a este servicio (0-100)"
    )
    
    class Meta:
        unique_together = ('plan', 'servicio')
        verbose_name = 'Plan-Servicio'
        verbose_name_plural = 'Planes-Servicios'
    
    def __str__(self):
        return f"{self.plan.nombre} - {self.servicio.nombre} ({self.porcentaje_descuento}% desc.)"
    
    def get_precio_con_descuento(self):
        """Calcula el precio del servicio con el descuento aplicado"""
        if self.porcentaje_descuento > 0:
            descuento = (self.servicio.precio * self.porcentaje_descuento) / 100
            return self.servicio.precio - descuento
        return self.servicio.precio
    
    def clean(self):
        """Validación para asegurar que el descuento esté entre 0 y 100"""
        from django.core.exceptions import ValidationError
        if self.porcentaje_descuento < 0 or self.porcentaje_descuento > 100:
            raise ValidationError('El porcentaje de descuento debe estar entre 0 y 100')


class SuscripcionUsuario(models.Model):
    ESTADOS_SUSCRIPCION = [
        ('activa', 'Activa'),
        ('pausada', 'Pausada'),
        ('cancelada', 'Cancelada'),
        ('vencida', 'Vencida'),
    ]
    
    id_suscripcion = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='suscripciones')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS_SUSCRIPCION, default='activa')
    servicios_utilizados_mes = models.IntegerField(default=0)
    ultimo_reinicio_contador = models.DateTimeField(default=timezone.now)
    auto_renovar = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.fecha_fin:
            self.fecha_fin = self.fecha_inicio + timedelta(days=30)
        super().save(*args, **kwargs)
    
    def reiniciar_contador_mensual(self):
        """Reinicia el contador de servicios utilizados cada mes"""
        hoy = timezone.now()
        if (hoy - self.ultimo_reinicio_contador).days >= 30:
            self.servicios_utilizados_mes = 0
            self.ultimo_reinicio_contador = hoy
            self.save()
    
    def puede_usar_servicio(self):
        """Verifica si el usuario puede usar un servicio más este mes"""
        self.reiniciar_contador_mensual()
        if self.plan.cantidad_servicios_mes == 0:  # Ilimitado
            return True
        return self.servicios_utilizados_mes < self.plan.cantidad_servicios_mes
    
    def servicios_restantes(self):
        """Retorna la cantidad de servicios restantes este mes"""
        self.reiniciar_contador_mensual()
        if self.plan.cantidad_servicios_mes == 0:
            return "Ilimitado"
        return max(0, self.plan.cantidad_servicios_mes - self.servicios_utilizados_mes)
    
    def esta_activa(self):
        """Verifica si la suscripción está activa y no vencida"""
        from django.utils import timezone
        from datetime import datetime
        
        ahora = timezone.now()
        
        # Extraer solo la fecha de fecha_fin si es datetime
        if hasattr(self.fecha_fin, 'date'):
            fecha_fin_date = self.fecha_fin.date()
        else:
            fecha_fin_date = self.fecha_fin
            
        print(f"🔍 Debug esta_activa() para {self.usuario.nombre_usuario}:")
        print(f"  - Estado: {self.estado}")
        print(f"  - Fecha fin (original): {self.fecha_fin}")
        print(f"  - Fecha fin (date): {fecha_fin_date}")
        print(f"  - Ahora (datetime): {ahora}")
        print(f"  - Ahora (date): {ahora.date()}")
        print(f"  - Estado == 'activa': {self.estado == 'activa'}")
        print(f"  - Fecha no vencida (>=): {fecha_fin_date >= ahora.date()}")
        
        # Comparar fechas apropiadamente
        resultado = self.estado == 'activa' and fecha_fin_date >= ahora.date()
        print(f"  - Resultado final: {resultado}")
        return resultado
    
    def __str__(self):
        return f"{self.usuario.nombre_usuario} - {self.plan.nombre} ({self.estado})"
    
    class Meta:
        ordering = ['-fecha_inicio']


class HistorialPagosSuscripcion(models.Model):
    ESTADOS_PAGO = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('reembolsado', 'Reembolsado'),
    ]
    
    id_pago_suscripcion = models.AutoField(primary_key=True)
    suscripcion = models.ForeignKey(SuscripcionUsuario, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='pendiente')
    referencia_pago = models.CharField(max_length=255, unique=True)
    metodo_pago = models.CharField(max_length=50)
    
    def __str__(self):
        return f"Pago {self.referencia_pago} - {self.suscripcion.usuario.nombre_usuario}"


# NUEVOS MODELOS PARA PLANES EMPRESARIALES
class PlanEmpresarial(models.Model):
    TIPOS_PLAN_EMPRESARIAL = [
        ('basico_flota', 'Básico para Flotas'),
        ('premium_flota', 'Premium para Flotas'),
        ('corporativo', 'Plan Corporativo'),
        ('transporte_publico', 'Transporte Público'),
    ]
    
    id_plan = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=30, choices=TIPOS_PLAN_EMPRESARIAL)
    descripcion = models.TextField()
    precio_mensual_por_vehiculo = models.DecimalField(max_digits=10, decimal_places=2)
    precio_base_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Precio base fijo mensual")
    vehiculos_minimos = models.IntegerField(default=5, help_text="Mínimo de vehículos para este plan")
    vehiculos_maximos = models.IntegerField(null=True, blank=True, help_text="Máximo de vehículos (null = ilimitado)")
    servicios_incluidos = models.ManyToManyField(Servicio, related_name='planes_empresariales')
    servicios_por_vehiculo_mes = models.IntegerField(help_text="Servicios permitidos por vehículo por mes. 0 = ilimitado")
    descuento_volumen = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Descuento por volumen en porcentaje")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Características específicas del plan empresarial
    incluye_lavado_asientos = models.BooleanField(default=True)
    incluye_aspirado = models.BooleanField(default=True)
    incluye_lavado_exterior = models.BooleanField(default=True)
    incluye_lavado_interior_humedo = models.BooleanField(default=False)
    incluye_encerado = models.BooleanField(default=False)
    incluye_detallado_completo = models.BooleanField(default=False)
    incluye_servicio_domicilio = models.BooleanField(default=False)
    incluye_mantenimiento_programado = models.BooleanField(default=False)
    incluye_reporte_mensual = models.BooleanField(default=False)
    incluye_soporte_24_7 = models.BooleanField(default=False)
    
    def calcular_precio_total(self, cantidad_vehiculos):
        """Calcula el precio total mensual para una cantidad de vehículos"""
        if cantidad_vehiculos < self.vehiculos_minimos:
            return None
        
        if self.vehiculos_maximos and cantidad_vehiculos > self.vehiculos_maximos:
            return None
            
        precio_vehiculos = self.precio_mensual_por_vehiculo * cantidad_vehiculos
        precio_total = self.precio_base_mensual + precio_vehiculos
        
        # Aplicar descuento por volumen
        if self.descuento_volumen > 0:
            descuento = precio_total * (self.descuento_volumen / 100)
            precio_total -= descuento
            
        return precio_total
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio_mensual_por_vehiculo}/vehículo"
    
    class Meta:
        ordering = ['precio_mensual_por_vehiculo']
        verbose_name = 'Plan Empresarial'
        verbose_name_plural = 'Planes Empresariales'


class SuscripcionEmpresarial(models.Model):
    ESTADOS_SUSCRIPCION = [
        ('activa', 'Activa'),
        ('pausada', 'Pausada'),
        ('cancelada', 'Cancelada'),
        ('vencida', 'Vencida'),
    ]
    
    id_suscripcion = models.AutoField(primary_key=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='suscripciones_empresariales')
    plan = models.ForeignKey(PlanEmpresarial, on_delete=models.CASCADE)
    cantidad_vehiculos = models.IntegerField()
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS_SUSCRIPCION, default='activa')
    servicios_utilizados_mes = models.IntegerField(default=0)
    ultimo_reinicio_contador = models.DateTimeField(default=timezone.now)
    auto_renovar = models.BooleanField(default=True)
    precio_mensual_actual = models.DecimalField(max_digits=12, decimal_places=2)
    contacto_responsable = models.CharField(max_length=255)
    telefono_contacto = models.CharField(max_length=15)
    notas_especiales = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.fecha_fin:
            self.fecha_fin = self.fecha_inicio + timedelta(days=30)
        
        # Calcular y guardar el precio mensual actual
        if not self.precio_mensual_actual:
            self.precio_mensual_actual = self.plan.calcular_precio_total(self.cantidad_vehiculos)
        
        super().save(*args, **kwargs)
    
    def reiniciar_contador_mensual(self):
        """Reinicia el contador de servicios utilizados cada mes"""
        hoy = timezone.now()
        if (hoy - self.ultimo_reinicio_contador).days >= 30:
            self.servicios_utilizados_mes = 0
            self.ultimo_reinicio_contador = hoy
            self.save()
    
    def puede_usar_servicio(self):
        """Verifica si la empresa puede usar un servicio más este mes"""
        self.reiniciar_contador_mensual()
        servicios_permitidos_total = self.plan.servicios_por_vehiculo_mes * self.cantidad_vehiculos
        if servicios_permitidos_total == 0:  # Ilimitado
            return True
        return self.servicios_utilizados_mes < servicios_permitidos_total
    
    def servicios_restantes(self):
        """Retorna la cantidad de servicios restantes este mes"""
        self.reiniciar_contador_mensual()
        servicios_permitidos_total = self.plan.servicios_por_vehiculo_mes * self.cantidad_vehiculos
        if servicios_permitidos_total == 0:
            return "Ilimitado"
        return max(0, servicios_permitidos_total - self.servicios_utilizados_mes)
    
    def esta_activa(self):
        """Verifica si la suscripción está activa y no vencida"""
        return self.estado == 'activa' and self.fecha_fin > timezone.now()
    
    def __str__(self):
        return f"{self.empresa.nombre_empresa} - {self.plan.nombre} ({self.cantidad_vehiculos} vehículos)"
    
    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = 'Suscripción Empresarial'
        verbose_name_plural = 'Suscripciones Empresariales'


class HistorialPagosSuscripcionEmpresarial(models.Model):
    ESTADOS_PAGO = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('reembolsado', 'Reembolsado'),
    ]
    
    id_pago_suscripcion = models.AutoField(primary_key=True)
    suscripcion = models.ForeignKey(SuscripcionEmpresarial, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='pendiente')
    referencia_pago = models.CharField(max_length=255, unique=True)
    metodo_pago = models.CharField(max_length=50)
    periodo_facturado = models.CharField(max_length=20, help_text="Ej: 2024-01")
    
    def __str__(self):
        return f"Pago {self.referencia_pago} - {self.suscripcion.empresa.nombre_empresa}"
    
    class Meta:
        verbose_name = 'Pago Suscripción Empresarial'
        verbose_name_plural = 'Pagos Suscripciones Empresariales'


class DetalleReservaEmpresarial(models.Model):
    """Detalles específicos para reservas empresariales"""
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='detalle_empresarial')
    numero_interno_empresa = models.CharField(max_length=50, blank=True, help_text="Número interno de la empresa para el vehículo")
    departamento_solicitante = models.CharField(max_length=100, blank=True)
    centro_costo = models.CharField(max_length=50, blank=True)
    kilometraje_actual = models.IntegerField(null=True, blank=True)
    proxima_revision = models.DateField(null=True, blank=True)
    responsable_vehiculo = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"Detalle empresarial - Reserva {self.reserva.id_reserva}"
    
    class Meta:
        verbose_name = 'Detalle Reserva Empresarial'
        verbose_name_plural = 'Detalles Reservas Empresariales'


class SolicitudServicioEmpresa(models.Model):
    """Modelo para gestionar solicitudes de nuevos servicios por parte de empresas"""
    ESTADOS_SOLICITUD = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('en_revision', 'En Revisión'),
    ]
    
    id_solicitud = models.AutoField(primary_key=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='solicitudes_servicios')
    servicio_solicitado = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADOS_SOLICITUD, default='pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    motivo_solicitud = models.TextField(help_text="Razón por la cual necesita este servicio")
    respuesta_admin = models.TextField(blank=True, help_text="Respuesta del administrador")
    usuario_responsable = models.CharField(max_length=255, help_text="Persona responsable de la solicitud")
    telefono_contacto = models.CharField(max_length=15, help_text="Teléfono para contacto")
    
    def __str__(self):
        return f"{self.empresa.nombre_empresa} - {self.servicio_solicitado.nombre_servicio} ({self.estado})"
    
    def aprobar_solicitud(self):
        """Aprueba la solicitud y asigna el servicio a la empresa"""
        if self.estado == 'pendiente' or self.estado == 'en_revision':
            # Crear la relación EmpresaServicio si no existe
            empresa_servicio, created = EmpresaServicio.objects.get_or_create(
                empresa=self.empresa,
                servicio=self.servicio_solicitado
            )
            
            self.estado = 'aprobada'
            self.fecha_respuesta = timezone.now()
            self.save()
            
            return created  # True si se creó la relación, False si ya existía
        return False
    
    def rechazar_solicitud(self, motivo_rechazo):
        """Rechaza la solicitud con un motivo"""
        self.estado = 'rechazada'
        self.fecha_respuesta = timezone.now()
        self.respuesta_admin = motivo_rechazo
        self.save()
    
    class Meta:
        verbose_name = 'Solicitud de Servicio Empresa'
        verbose_name_plural = 'Solicitudes de Servicios Empresas'
        unique_together = [['empresa', 'servicio_solicitado', 'estado']]  # Evita duplicados pendientes


class SolicitudContactoPlan(models.Model):
    """Modelo para almacenar solicitudes de contacto de planes empresariales"""
    ESTADOS_SOLICITUD = [
        ('pendiente', 'Pendiente'),
        ('contactado', 'Contactado'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('cerrado', 'Cerrado'),
    ]
    
    id_solicitud = models.AutoField(primary_key=True)
    plan = models.ForeignKey(PlanEmpresarial, on_delete=models.CASCADE, related_name='solicitudes_contacto')
    
    # Datos del solicitante
    nombre_completo = models.CharField(max_length=200)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    empresa = models.CharField(max_length=200)
    cargo = models.CharField(max_length=100, blank=True)
    
    # Información adicional
    cantidad_vehiculos = models.IntegerField(help_text="Cantidad aproximada de vehículos en la flota")
    mensaje_adicional = models.TextField(blank=True, help_text="Información adicional o requerimientos específicos")
    
    # Metadatos
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_SOLICITUD, default='pendiente')
    ip_solicitante = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Información de seguimiento
    fecha_contacto = models.DateTimeField(null=True, blank=True)
    notas_seguimiento = models.TextField(blank=True)
    
    def __str__(self):
        return f"Solicitud de {self.nombre_completo} - {self.plan.nombre}"
    
    def marcar_como_contactado(self, notas=""):
        """Marca la solicitud como contactada"""
        self.estado = 'contactado'
        self.fecha_contacto = timezone.now()
        if notas:
            self.notas_seguimiento = notas
        self.save()
    
    class Meta:
        verbose_name = 'Solicitud de Contacto de Plan'
        verbose_name_plural = 'Solicitudes de Contacto de Planes'
        ordering = ['-fecha_solicitud']


# ================== MODELO PARA CONSENTIMIENTO DE POLÍTICAS (LEY 1581) ==================
class ConsentimientoUsuario(models.Model):
    """
    Modelo para registrar el consentimiento explícito de usuarios
    según la Ley 1581 de 2012 de Protección de Datos Personales
    """
    TIPOS_CONSENTIMIENTO = [
        ('registro', 'Registro Inicial'),
        ('actualizacion', 'Actualización de Políticas'),
        ('marketing', 'Comunicaciones de Marketing'),
    ]
    
    id_consentimiento = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='consentimientos')
    
    # Consentimientos obligatorios
    acepta_politica_privacidad = models.BooleanField(default=False, verbose_name="Acepta Aviso de Privacidad")
    acepta_tratamiento_datos = models.BooleanField(default=False, verbose_name="Acepta Política de Tratamiento de Datos")
    acepta_terminos_condiciones = models.BooleanField(default=False, verbose_name="Acepta Términos y Condiciones")
    
    # Consentimientos opcionales
    acepta_comunicaciones_comerciales = models.BooleanField(default=False, verbose_name="Acepta Comunicaciones Comerciales")
    acepta_compartir_datos_terceros = models.BooleanField(default=False, verbose_name="Acepta Compartir Datos con Terceros")
    
    # Información de registro
    tipo_consentimiento = models.CharField(max_length=20, choices=TIPOS_CONSENTIMIENTO, default='registro')
    fecha_consentimiento = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")
    user_agent = models.TextField(blank=True, verbose_name="Navegador/Dispositivo")
    
    # Versiones de documentos aceptados
    version_politica_privacidad = models.CharField(max_length=20, default="1.0")
    version_tratamiento_datos = models.CharField(max_length=20, default="1.0")
    version_terminos_condiciones = models.CharField(max_length=20, default="1.0")
    
    # Información adicional
    revocado = models.BooleanField(default=False, verbose_name="Consentimiento Revocado")
    fecha_revocacion = models.DateTimeField(null=True, blank=True)
    motivo_revocacion = models.TextField(blank=True)
    
    def __str__(self):
        return f"Consentimiento {self.usuario.nombre_usuario} - {self.fecha_consentimiento.strftime('%Y-%m-%d')}"
    
    def revocar_consentimiento(self, motivo=""):
        """Revoca el consentimiento del usuario"""
        self.revocado = True
        self.fecha_revocacion = timezone.now()
        self.motivo_revocacion = motivo
        self.save()
    
    def esta_vigente(self):
        """Verifica si el consentimiento está vigente (no revocado)"""
        return not self.revocado
    
    class Meta:
        verbose_name = 'Consentimiento de Usuario'
        verbose_name_plural = 'Consentimientos de Usuarios'
        ordering = ['-fecha_consentimiento']
        indexes = [
            models.Index(fields=['usuario', 'fecha_consentimiento']),
            models.Index(fields=['revocado']),
        ]


# ================== MODELOS PARA SISTEMA DE PAGOS A EMPRESAS ==================
import uuid

class PeriodoLiquidacion(models.Model):
    """
    Modelo para gestionar períodos de liquidación cada 15 días
    """
    ESTADOS_PERIODO = [
        ('activo', 'Activo'),
        ('cerrado', 'Cerrado'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado'),
    ]
    
    id_periodo = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='periodos_liquidacion')
    
    # Fechas del período
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    
    # Información financiera
    total_bruto = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Total sin descuentos
    total_descuentos = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Descuentos aplicados
    comision_autonew = models.DecimalField(max_digits=5, decimal_places=2, default=15.0)  # % comisión
    total_comision = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Valor comisión
    total_neto = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # A pagar a empresa
    
    # Estado y gestión
    estado = models.CharField(max_length=20, choices=ESTADOS_PERIODO, default='activo')
    reservas_incluidas = models.ManyToManyField(Reserva, related_name='periodos_liquidacion', blank=True)
    cantidad_reservas = models.IntegerField(default=0)
    
    # Información de pago
    metodo_pago = models.CharField(max_length=50, blank=True, choices=[
        ('transferencia', 'Transferencia Bancaria'),
        ('consignacion', 'Consignación'),
        ('efectivo', 'Efectivo'),
        ('cheque', 'Cheque'),
    ])
    referencia_pago = models.CharField(max_length=255, blank=True)
    observaciones = models.TextField(blank=True)
    
    # Auditoría
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='periodos_creados')
    pagado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='periodos_pagados')
    
    def calcular_totales(self):
        """
        Calcula todos los totales del período basado en las reservas incluidas
        """
        reservas = self.reservas_incluidas.filter(
            estado='completado',
            fecha__range=[self.fecha_inicio, self.fecha_fin],
            empresa=self.empresa
        )
        
        total_bruto = 0
        total_descuentos = 0
        
        for reserva in reservas:
            # Obtener detalles de servicios con descuentos aplicados
            detalle = reserva.obtener_detalle_servicios()
            
            # Sumar al total bruto (precio original de servicios)
            for servicio_info in detalle.get('servicios_plan', []) + \
                               detalle.get('servicios_adicionales', []) + \
                               detalle.get('servicios_empresariales', []):
                total_bruto += servicio_info['precio_original']
                total_descuentos += servicio_info['ahorro']
        
        self.total_bruto = total_bruto
        self.total_descuentos = total_descuentos
        
        # Calcular comisión sobre el total después de descuentos
        total_con_descuento = total_bruto - total_descuentos
        self.total_comision = (total_con_descuento * self.comision_autonew) / 100
        
        # Total neto a pagar a la empresa
        self.total_neto = total_con_descuento - self.total_comision
        
        # Actualizar cantidad de reservas
        self.cantidad_reservas = reservas.count()
        
        self.save()
        return {
            'total_bruto': self.total_bruto,
            'total_descuentos': self.total_descuentos,
            'total_comision': self.total_comision,
            'total_neto': self.total_neto,
            'cantidad_reservas': self.cantidad_reservas
        }
    
    def cerrar_periodo(self, usuario):
        """
        Cierra el período y calcula los totales finales
        """
        if self.estado == 'activo':
            # Incluir todas las reservas completadas del período
            reservas_periodo = Reserva.objects.filter(
                empresa=self.empresa,
                estado='completado',
                fecha__range=[self.fecha_inicio, self.fecha_fin]
            )
            self.reservas_incluidas.set(reservas_periodo)
            
            # Calcular totales
            self.calcular_totales()
            
            # Cambiar estado
            self.estado = 'cerrado'
            self.fecha_cierre = timezone.now()
            self.creado_por = usuario
            self.save()
            
            return True
        return False
    
    def marcar_como_pagado(self, usuario, metodo_pago, referencia_pago='', observaciones=''):
        """
        Marca el período como pagado
        """
        if self.estado == 'cerrado':
            self.estado = 'pagado'
            self.fecha_pago = timezone.now()
            self.pagado_por = usuario
            self.metodo_pago = metodo_pago
            self.referencia_pago = referencia_pago
            self.observaciones = observaciones
            self.save()
            return True
        return False
    
    @property
    def dias_transcurridos(self):
        """Calcula los días transcurridos desde el inicio del período"""
        if self.fecha_inicio:
            return (timezone.now() - self.fecha_inicio).days
        return 0
    
    @property
    def esta_vencido(self):
        """Verifica si el período ya debería estar cerrado (más de 15 días)"""
        return self.dias_transcurridos > 15 and self.estado == 'activo'
    
    def __str__(self):
        return f"{self.empresa.nombre_empresa} - {self.fecha_inicio.strftime('%d/%m/%Y')} al {self.fecha_fin.strftime('%d/%m/%Y')}"
    
    class Meta:
        verbose_name = 'Período de Liquidación'
        verbose_name_plural = 'Períodos de Liquidación'
        ordering = ['-fecha_inicio']


class DetalleLiquidacion(models.Model):
    """
    Detalles específicos de cada reserva dentro de un período de liquidación
    """
    periodo = models.ForeignKey(PeriodoLiquidacion, on_delete=models.CASCADE, related_name='detalles')
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    
    # Valores calculados al momento de la liquidación
    valor_bruto = models.DecimalField(max_digits=10, decimal_places=2)
    valor_descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_neto = models.DecimalField(max_digits=10, decimal_places=2)
    comision_aplicada = models.DecimalField(max_digits=5, decimal_places=2)
    valor_comision = models.DecimalField(max_digits=10, decimal_places=2)
    valor_final_empresa = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Información adicional
    fecha_servicio = models.DateTimeField()
    tipo_descuento = models.CharField(max_length=50, blank=True, choices=[
        ('plan_individual', 'Plan Individual'),
        ('plan_empresarial', 'Plan Empresarial'),
        ('descuento_especial', 'Descuento Especial'),
        ('sin_descuento', 'Sin Descuento'),
    ])
    
    fecha_calculo = models.DateTimeField(auto_now_add=True)
    
    def calcular_valores(self):
        """
        Calcula todos los valores para esta reserva específica
        """
        detalle_reserva = self.reserva.obtener_detalle_servicios()
        
        # Sumar valores de todos los servicios
        self.valor_bruto = sum([
            servicio['precio_original'] 
            for servicios in [
                detalle_reserva.get('servicios_plan', []),
                detalle_reserva.get('servicios_adicionales', []),
                detalle_reserva.get('servicios_empresariales', [])
            ]
            for servicio in servicios
        ])
        
        self.valor_descuento = detalle_reserva.get('ahorro_total', 0)
        self.valor_neto = self.valor_bruto - self.valor_descuento
        
        # Aplicar comisión del período
        self.comision_aplicada = self.periodo.comision_autonew
        self.valor_comision = (self.valor_neto * self.comision_aplicada) / 100
        self.valor_final_empresa = self.valor_neto - self.valor_comision
        
        # Determinar tipo de descuento
        if self.reserva.suscripcion_utilizada:
            self.tipo_descuento = 'plan_individual'
        elif self.reserva.suscripcion_empresarial:
            self.tipo_descuento = 'plan_empresarial'
        elif self.valor_descuento > 0:
            self.tipo_descuento = 'descuento_especial'
        else:
            self.tipo_descuento = 'sin_descuento'
        
        self.fecha_servicio = self.reserva.fecha
        self.save()
    
    def __str__(self):
        return f"Detalle - {self.reserva} - ${self.valor_final_empresa}"
    
    class Meta:
        verbose_name = 'Detalle de Liquidación'
        verbose_name_plural = 'Detalles de Liquidación'
        unique_together = ['periodo', 'reserva']


class ConfiguracionPagos(models.Model):
    """
    Configuración global para el sistema de pagos
    """
    # Configuración de períodos
    dias_por_periodo = models.IntegerField(default=15, help_text="Días por período de liquidación")
    comision_por_defecto = models.DecimalField(max_digits=5, decimal_places=2, default=15.0, help_text="Comisión por defecto (%)")
    
    # Configuración de notificaciones
    dias_aviso_vencimiento = models.IntegerField(default=3, help_text="Días de anticipación para avisar vencimiento")
    auto_cerrar_periodos = models.BooleanField(default=False, help_text="Cerrar automáticamente períodos vencidos")
    
    # Configuración de reportes
    incluir_reservas_canceladas = models.BooleanField(default=False, help_text="Incluir reservas canceladas en reportes")
    
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"Configuración de Pagos - {self.dias_por_periodo} días"
    
    class Meta:
        verbose_name = 'Configuración de Pagos'
        verbose_name_plural = 'Configuraciones de Pagos'
