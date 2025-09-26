from django.core.management.base import BaseCommand
from lavado_auto.models import Usuario, Empresa, Servicio, Reserva, ReservaServicio
from faker import Faker
import random
from datetime import datetime, timedelta, time
from django.db import transaction

class Command(BaseCommand):
    help = 'Crea 500 reservas de prueba con usuarios aleatorios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=500,
            help='Cantidad de reservas a crear (default: 500)',
        )

    def handle(self, *args, **options):
        fake = Faker('es_ES')
        cantidad = options['cantidad']
        
        # Verificar que tenemos usuarios, empresas y servicios
        usuarios = list(Usuario.objects.filter(is_active=True))
        empresas = list(Empresa.objects.filter(verificada=True))
        servicios = list(Servicio.objects.all())
        
        if not usuarios:
            self.stdout.write(self.style.ERROR('No hay usuarios activos en el sistema'))
            return
            
        if not empresas:
            self.stdout.write(self.style.WARNING('No hay empresas verificadas. Creando algunas empresas de prueba...'))
            self.crear_empresas_prueba()
            empresas = list(Empresa.objects.filter(verificada=True))
            
        if not servicios:
            self.stdout.write(self.style.WARNING('No hay servicios disponibles. Creando servicios de prueba...'))
            self.crear_servicios_prueba()
            servicios = list(Servicio.objects.all())
        
        # Estados posibles para las reservas
        estados = ['pendiente', 'completado', 'cancelada']
        estados_pesos = [0.4, 0.5, 0.1]  # 40% pendiente, 50% completado, 10% cancelada
        
        # Tipos de vehículo para reservas empresariales
        tipos_vehiculo = ['sedan', 'suv', 'camioneta', 'bus', 'microbus', 'camion', 'taxi', 'moto']
        
        reservas_creadas = 0
        reservas_fallidas = 0
        
        self.stdout.write(f'Creando {cantidad} reservas...')
        
        with transaction.atomic():
            for i in range(cantidad):
                try:
                    # Seleccionar usuario y empresa aleatoriamente
                    usuario = random.choice(usuarios)
                    empresa = random.choice(empresas)
                    
                    # Generar fecha aleatoria (entre 60 días atrás y 30 días adelante)
                    fecha_inicio = datetime.now() - timedelta(days=60)
                    fecha_fin = datetime.now() + timedelta(days=30)
                    fecha_aleatoria = fake.date_between(start_date=fecha_inicio.date(), end_date=fecha_fin.date())
                    
                    # Generar hora aleatoria (horario comercial: 8:00 AM - 6:00 PM)
                    hora_inicio = 8
                    hora_fin = 18
                    hora_aleatoria = time(
                        hour=random.randint(hora_inicio, hora_fin-1),
                        minute=random.choice([0, 15, 30, 45])
                    )
                    
                    # Determinar estado de la reserva
                    estado = random.choices(estados, weights=estados_pesos)[0]
                    
                    # Determinar si es reserva empresarial (30% de probabilidad)
                    es_empresarial = random.random() < 0.3
                    
                    # Crear la reserva
                    reserva = Reserva.objects.create(
                        fecha=fecha_aleatoria,
                        hora=hora_aleatoria,
                        empresa=empresa,
                        estado=estado,
                        usuario=usuario,
                        es_pago_individual=not es_empresarial,
                        es_reserva_empresarial=es_empresarial
                    )
                    
                    # Si es reserva empresarial, agregar datos adicionales
                    if es_empresarial:
                        reserva.placa_vehiculo = self.generar_placa()
                        reserva.tipo_vehiculo = random.choice(tipos_vehiculo)
                        reserva.conductor_asignado = fake.name()
                        reserva.observaciones_empresariales = fake.text(max_nb_chars=200) if random.random() < 0.3 else ''
                        reserva.save()
                    
                    # Agregar servicios aleatorios a la reserva (1-3 servicios)
                    servicios_empresa = empresa.servicios.all()
                    if servicios_empresa.exists():
                        servicios_reserva = servicios_empresa
                    else:
                        servicios_reserva = servicios
                    
                    num_servicios = random.randint(1, min(3, len(servicios_reserva)))
                    servicios_seleccionados = random.sample(list(servicios_reserva), num_servicios)
                    
                    for servicio in servicios_seleccionados:
                        # Calcular precio con posible descuento empresarial
                        precio_base = servicio.precio
                        descuento = 0
                        
                        if es_empresarial and random.random() < 0.6:  # 60% de reservas empresariales tienen descuento
                            descuento = random.uniform(5, 25)  # Descuento entre 5% y 25%
                            precio_aplicado = precio_base * (1 - descuento/100)
                        else:
                            precio_aplicado = precio_base
                        
                        ReservaServicio.objects.create(
                            reserva=reserva,
                            servicio=servicio,
                            precio_aplicado=precio_aplicado,
                            descuento_empresarial=descuento
                        )
                    
                    reservas_creadas += 1
                    
                    if reservas_creadas % 50 == 0:
                        self.stdout.write(f'Creadas {reservas_creadas} reservas...')
                        
                except Exception as e:
                    reservas_fallidas += 1
                    self.stdout.write(
                        self.style.WARNING(f'Error al crear reserva {i+1}: {str(e)}')
                    )
        
        # Estadísticas finales
        self.stdout.write(
            self.style.SUCCESS(
                f'Proceso completado:\n'
                f'- Reservas creadas: {reservas_creadas}\n'
                f'- Reservas fallidas: {reservas_fallidas}\n'
                f'- Reservas individuales: {Reserva.objects.filter(es_pago_individual=True).count()}\n'
                f'- Reservas empresariales: {Reserva.objects.filter(es_reserva_empresarial=True).count()}'
            )
        )
    
    def generar_placa(self):
        """Genera una placa colombiana aleatoria"""
        # Formato colombiano: ABC123 o ABC12D
        letras = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
        if random.random() < 0.7:  # 70% formato antiguo ABC123
            numeros = ''.join(random.choices('0123456789', k=3))
            return f"{letras}{numeros}"
        else:  # 30% formato nuevo ABC12D
            numeros = ''.join(random.choices('0123456789', k=2))
            letra_final = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            return f"{letras}{numeros}{letra_final}"
    
    def crear_empresas_prueba(self):
        """Crea algunas empresas de prueba si no existen"""
        empresas_datos = [
            {'nombre': 'AutoWash Express', 'direccion': 'Calle 123 #45-67'},
            {'nombre': 'Lavado Premium', 'direccion': 'Carrera 78 #23-45'},
            {'nombre': 'CleanCar Service', 'direccion': 'Avenida 68 #12-34'},
            {'nombre': 'Super Lavado', 'direccion': 'Calle 45 #67-89'},
            {'nombre': 'Eco Wash', 'direccion': 'Carrera 123 #45-67'}
        ]
        
        for datos in empresas_datos:
            if not Empresa.objects.filter(nombre_empresa=datos['nombre']).exists():
                Empresa.objects.create(
                    nombre_empresa=datos['nombre'],
                    direccion=datos['direccion'],
                    telefono=f"57300{random.randint(1000000, 9999999)}",
                    email=f"{datos['nombre'].lower().replace(' ', '')}@example.com",
                    verificada=True
                )
        
        self.stdout.write(self.style.SUCCESS('Empresas de prueba creadas'))
    
    def crear_servicios_prueba(self):
        """Crea algunos servicios de prueba si no existen"""
        servicios_datos = [
            {'nombre': 'Lavado Básico', 'descripcion': 'Lavado exterior completo', 'precio': 15000},
            {'nombre': 'Lavado Premium', 'descripcion': 'Lavado exterior e interior completo', 'precio': 25000},
            {'nombre': 'Encerado', 'descripcion': 'Aplicación de cera protectora', 'precio': 35000},
            {'nombre': 'Aspirado Interior', 'descripcion': 'Limpieza completa del interior', 'precio': 12000},
            {'nombre': 'Lavado de Motor', 'descripcion': 'Limpieza y desengrase del motor', 'precio': 20000},
            {'nombre': 'Detailing Completo', 'descripcion': 'Servicio completo de detailing', 'precio': 80000},
        ]
        
        for datos in servicios_datos:
            if not Servicio.objects.filter(nombre_servicio=datos['nombre']).exists():
                Servicio.objects.create(
                    nombre_servicio=datos['nombre'],
                    descripcion=datos['descripcion'],
                    precio=datos['precio']
                )
        
        self.stdout.write(self.style.SUCCESS('Servicios de prueba creados'))
