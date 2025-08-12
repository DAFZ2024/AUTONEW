from django.db import models
from django.utils import timezone
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta


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
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
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

    objects = UsuarioManager()

    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = ['correo']
    
    def __str__(self):
        return self.nombre_usuario
    
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
    fecha_registro = models.DateTimeField(default=timezone.now)  # Fecha de registro con default
    verificada = models.BooleanField(default=False)  # Campo para verificación de empresa
    servicios = models.ManyToManyField(Servicio, through=EmpresaServicio)

    def __str__(self):
        return self.nombre_empresa
    



class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
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

    def __str__(self):
        if self.es_reserva_empresarial and self.placa_vehiculo:
            return f"Reserva Empresarial {self.id_reserva} - {self.placa_vehiculo}"
        return f"Reserva {self.id_reserva} - {self.usuario.nombre_usuario}"

class ReservaServicio(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    
    # Campos adicionales para manejo empresarial
    precio_aplicado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Precio específico aplicado")
    descuento_empresarial = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Descuento en porcentaje")
    
    def __str__(self):
        return f"Reserva {self.reserva.id_reserva} - Servicio {self.servicio.nombre_servicio}"




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



# Modelo Mensaje o Queja
class MensajeQueja(models.Model):
    id_mensaje = models.AutoField(primary_key=True)
    contenido = models.TextField()
    fecha_envio = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=50, default='no respondido')
    respuesta = models.TextField(blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)   

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
    servicios_incluidos = models.ManyToManyField(Servicio, related_name='planes')
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
        return self.estado == 'activa' and self.fecha_fin > timezone.now()
    
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
