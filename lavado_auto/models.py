from django.db import models
from django.utils import timezone
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


# Create your models here.

class UsuarioManager(BaseUserManager):
    def create_user(self, nombre_usuario, correo, contrasena=None, **extra_fields):
        if not correo:
            raise ValueError('El correo debe ser proporcionado')
        correo = self.normalize_email(correo)
        user = self.model(nombre_usuario=nombre_usuario, correo=correo, **extra_fields)
        user.set_password(contrasena) 
        user.save(using=self._db)
        return user

    def create_superuser(self, nombre_usuario, correo, contrasena=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        user = self.create_user(nombre_usuario, correo, contrasena, **extra_fields)
        user.save(using=self._db)  # Agrega esta línea para guardar el superusuario
        return user

class Usuario(AbstractBaseUser, PermissionsMixin):
    id_usuario = models.AutoField(primary_key=True)
    nombre_completo = models.CharField(max_length=255) 
    nombre_usuario = models.CharField(max_length=20, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    contrasena = models.CharField(max_length=255)
    last_login = models.DateTimeField(null=True, blank=True)
    token_reset = models.CharField(max_length=255, null=True, blank=True)
    rol = models.CharField(max_length=50, choices=(('cliente', 'Cliente'), ('admin', 'Administrador')), default='cliente')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UsuarioManager()


    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = ['correo']


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
    servicios = models.ManyToManyField(Servicio, through=EmpresaServicio)

    def __str__(self):
        return self.nombre_empresa
    



class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    fecha = models.DateField()
    hora = models.TimeField()
    ESTADOS = [
        ('no_completado', 'No Completado'),
        ('completado', 'Completado'),
    ]
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE) 
    estado = models.CharField(max_length=20, choices=ESTADOS, default='no_completado')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    servicios = models.ManyToManyField(Servicio, through='ReservaServicio')  


    def __str__(self):
        return f"Reserva {self.id_reserva} - {self.usuario.nombre_usuario}"

class ReservaServicio(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    
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
