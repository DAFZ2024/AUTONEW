from django.core.management.base import BaseCommand
from lavado_auto.models import Usuario
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Crea 1000 usuarios de prueba con el rol de cliente'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=1000,
            help='Cantidad de usuarios a crear (default: 1000)',
        )

    def handle(self, *args, **options):
        fake = Faker('es_ES')  # Configurar Faker para español
        cantidad = options['cantidad']
        
        usuarios_creados = 0
        usuarios_existentes = 0
        
        self.stdout.write(f'Creando {cantidad} usuarios...')
        
        for i in range(cantidad):
            # Generar datos únicos
            nombre_completo = fake.name()
            # Crear nombre de usuario único basado en el nombre
            nombre_usuario_base = nombre_completo.lower().replace(' ', '').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
            
            # Asegurar que el nombre de usuario sea único
            contador = 1
            nombre_usuario = nombre_usuario_base
            while Usuario.objects.filter(nombre_usuario=nombre_usuario).exists():
                nombre_usuario = f"{nombre_usuario_base}{contador}"
                contador += 1
            
            # Generar correo único
            correo_base = f"{nombre_usuario}@{fake.free_email_domain()}"
            correo = correo_base
            contador_correo = 1
            while Usuario.objects.filter(correo=correo).exists():
                correo = f"{nombre_usuario}{contador_correo}@{fake.free_email_domain()}"
                contador_correo += 1
            
            try:
                # Crear el usuario
                usuario = Usuario.objects.create_user(
                    nombre_usuario=nombre_usuario,
                    nombre_completo=nombre_completo,
                    correo=correo,
                    telefono=fake.phone_number()[:15],  # Limitar a 15 caracteres
                    direccion=fake.address()[:255],     # Limitar a 255 caracteres
                    password='password123',  # Contraseña por defecto
                    rol='cliente'  # Rol por defecto
                )
                usuarios_creados += 1
                
                if usuarios_creados % 100 == 0:
                    self.stdout.write(f'Creados {usuarios_creados} usuarios...')
                    
            except Exception as e:
                usuarios_existentes += 1
                self.stdout.write(
                    self.style.WARNING(f'Error al crear usuario {nombre_usuario}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Proceso completado: {usuarios_creados} usuarios creados, {usuarios_existentes} errores'
            )
        )
