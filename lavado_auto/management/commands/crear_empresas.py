from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random
from datetime import datetime, timedelta
import re

from lavado_auto.models import Empresa, Servicio

class Command(BaseCommand):
    help = 'Crea 100 empresas nuevas con datos realistas en español'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=100,
            help='Cantidad de empresas a crear (default: 100)'
        )

    def handle(self, *args, **options):
        fake = Faker('es_ES')  # Configurar para español de España
        cantidad = options['cantidad']
        
        # Listas de tipos de empresas para variedad
        tipos_empresas = [
            "AutoLavado", "Lavadero", "Autolavado Express", "Car Wash", "Limpieza Automotriz",
            "Detailing", "Spa Automotriz", "Lavado Premium", "Auto Spa", "Wash & Go",
            "Lavadero Integral", "Centro de Lavado", "Autoservicio", "Lavado Ecológico",
            "Quick Wash", "Auto Clean", "Lavado 24h", "Super Wash", "Mega Lavado",
            "Lavadero del Centro", "Autolavado VIP", "Lavado Express"
        ]
        
        # Nombres adicionales creativos
        nombres_creativos = [
            "El Brillante", "La Espuma", "Agua Cristal", "Brillo Total", "Limpio y Seco",
            "Burbuja Azul", "Shine Car", "Crystal Clean", "Golden Wash", "Silver Shine",
            "Aqua Fresh", "Bubble Time", "Clean Master", "Fresh Auto", "Pure Shine",
            "Speed Wash", "Ultra Clean", "Maxi Brillo", "Super Limpio", "Mega Shine"
        ]
        
        # Ciudades colombianas
        ciudades = [
            "Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena", "Bucaramanga",
            "Pereira", "Santa Marta", "Ibagué", "Pasto", "Manizales", "Neiva",
            "Villavicencio", "Armenia", "Valledupar", "Montería", "Sincelejo",
            "Popayán", "Tunja", "Florencia", "Riohacha", "Quibdó", "Soacha",
            "Soledad", "Bello", "Envigado", "Itagüí", "Palmira", "Buenaventura",
            "Floridablanca", "Malambo", "Girón", "Zipaquirá", "Chía", "Facatativá"
        ]
        
        # Barrios/sectores comunes
        sectores = [
            "Centro", "Norte", "Sur", "Oriente", "Occidente", "La Candelaria", "Chapinero",
            "Zona Rosa", "El Poblado", "Laureles", "Estadio", "Normandía", "Boston",
            "Las Palmas", "Cabecera", "Provenza", "El Country", "Chicó", "La Macarena",
            "Quinta Camacho", "Zona Industrial", "Terminal", "Aeropuerto", "Universidad",
            "Hospital", "Centro Comercial", "Plaza Mayor", "Parque Central"
        ]
        
        empresas_creadas = 0
        empresas_fallidas = 0
        
        self.stdout.write(
            self.style.SUCCESS(f'🏢 Iniciando creación de {cantidad} empresas...')
        )
        
        for i in range(cantidad):
            try:
                # Generar nombre de empresa creativo
                if random.choice([True, False]):
                    # Combinar tipo de empresa con nombre creativo
                    tipo = random.choice(tipos_empresas)
                    nombre_creativo = random.choice(nombres_creativos)
                    nombre_empresa = f"{tipo} {nombre_creativo}"
                else:
                    # Usar solo nombre creativo con sufijo
                    nombre_base = random.choice(nombres_creativos)
                    sufijos = ["Auto", "Car", "Express", "Premium", "VIP", "Plus", "Pro", "Max"]
                    sufijo = random.choice(sufijos)
                    nombre_empresa = f"{nombre_base} {sufijo}"
                
                # Generar ciudad y sector
                ciudad = random.choice(ciudades)
                sector = random.choice(sectores)
                
                # Generar dirección realista
                numero_calle = fake.random_int(min=1, max=200)
                numero_bis = random.choice(["", " bis", " A", " B"])
                numero_interior = random.choice(["", f"-{fake.random_int(min=1, max=50)}"])
                
                direccion = f"Calle {numero_calle}{numero_bis} #{fake.random_int(min=1, max=100)}-{fake.random_int(min=1, max=199)}{numero_interior}, {sector}, {ciudad}"
                
                # Generar teléfono colombiano realista
                prefijos_movil = ["300", "301", "302", "310", "311", "312", "313", "314", "315", "316", "317", "318", "319", "320", "321", "322", "323", "324", "350", "351"]
                prefijos_fijo = ["601", "604", "602", "605", "606", "607", "608"]
                
                if random.choice([True, False]):  # 50% móvil, 50% fijo
                    prefijo = random.choice(prefijos_movil)
                    numero = f"{prefijo}{fake.random_int(min=1000000, max=9999999)}"
                else:
                    prefijo = random.choice(prefijos_fijo)
                    numero = f"{prefijo}{fake.random_int(min=1000000, max=9999999)}"
                
                # Generar email corporativo
                nombre_limpio = nombre_empresa.lower().replace(" ", "").replace("ñ", "n")
                # Limpiar caracteres especiales
                nombre_limpio = re.sub(r'[^a-z0-9]', '', nombre_limpio)
                
                dominios = ["gmail.com", "hotmail.com", "yahoo.com", "outlook.com", "empresas.com", "lavadero.com"]
                email = f"{nombre_limpio}@{random.choice(dominios)}"
                
                # Asegurar que el email no sea demasiado largo
                if len(email) > 50:
                    email = f"{nombre_limpio[:20]}@{random.choice(dominios)}"
                
                # Generar contraseña temporal
                contrasena = f"empresa{fake.random_int(min=1000, max=9999)}"
                
                # Fecha de registro aleatoria en los últimos 2 años
                fecha_inicio = timezone.now() - timedelta(days=730)
                fecha_registro = fake.date_time_between(start_date=fecha_inicio, end_date='now', tzinfo=timezone.get_current_timezone())
                
                # 80% de empresas verificadas
                verificada = random.choices([True, False], weights=[80, 20])[0]
                
                # Crear la empresa
                empresa = Empresa.objects.create(
                    nombre_empresa=nombre_empresa,
                    direccion=direccion,
                    telefono=numero,
                    email=email,
                    contrasena=contrasena,
                    fecha_registro=fecha_registro,
                    verificada=verificada
                )
                
                # Asignar servicios aleatorios (entre 1 y 5 servicios por empresa)
                servicios_disponibles = list(Servicio.objects.all())
                if servicios_disponibles:
                    cantidad_servicios = random.randint(1, min(5, len(servicios_disponibles)))
                    servicios_seleccionados = random.sample(servicios_disponibles, cantidad_servicios)
                    empresa.servicios.set(servicios_seleccionados)
                
                empresas_creadas += 1
                
                # Mostrar progreso cada 10 empresas
                if (i + 1) % 10 == 0:
                    self.stdout.write(f"✅ Progreso: {i + 1}/{cantidad} empresas procesadas...")
                
            except Exception as e:
                empresas_fallidas += 1
                self.stdout.write(
                    self.style.WARNING(f"⚠️  Error al crear empresa {i + 1}: {str(e)}")
                )
                continue
        
        # Mostrar resumen final
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Proceso completado:')
        )
        self.stdout.write(f"   - Empresas creadas: {empresas_creadas}")
        self.stdout.write(f"   - Empresas fallidas: {empresas_fallidas}")
        
        if empresas_creadas > 0:
            # Mostrar algunas empresas de ejemplo
            empresas_ejemplo = Empresa.objects.order_by('-fecha_registro')[:5]
            self.stdout.write(f"\n📋 Últimas 5 empresas creadas:")
            for empresa in empresas_ejemplo:
                verificacion = "✅ Verificada" if empresa.verificada else "⏳ Pendiente"
                self.stdout.write(f"   • {empresa.nombre_empresa} - {empresa.direccion} - {verificacion}")
        
        # Mostrar estadísticas totales
        total_empresas = Empresa.objects.count()
        empresas_verificadas = Empresa.objects.filter(verificada=True).count()
        
        self.stdout.write(f"\n📊 Estadísticas generales:")
        self.stdout.write(f"   - Total de empresas en sistema: {total_empresas}")
        self.stdout.write(f"   - Empresas verificadas: {empresas_verificadas}")
        self.stdout.write(f"   - Empresas pendientes: {total_empresas - empresas_verificadas}")
