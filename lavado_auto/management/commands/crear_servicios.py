from django.core.management.base import BaseCommand
from django.db import models
from faker import Faker
import random
from decimal import Decimal

from lavado_auto.models import Servicio

class Command(BaseCommand):
    help = 'Crea 100 servicios nuevos con datos realistas para lavaderos de autos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=100,
            help='Cantidad de servicios a crear (default: 100)'
        )

    def handle(self, *args, **options):
        fake = Faker('es_ES')
        cantidad = options['cantidad']
        
        # Categorías de servicios con sus respectivos servicios específicos
        servicios_data = [
            # LAVADO BÁSICO
            {"nombre": "Lavado Exterior Básico", "descripcion": "Lavado exterior con agua y jabón, enjuague y secado básico", "precio_min": 15000, "precio_max": 25000},
            {"nombre": "Lavado Interior Básico", "descripcion": "Aspirado de asientos, alfombrillas y maletero, limpieza de superficies", "precio_min": 12000, "precio_max": 20000},
            {"nombre": "Lavado Completo Básico", "descripcion": "Lavado exterior e interior básico en un solo servicio", "precio_min": 25000, "precio_max": 40000},
            {"nombre": "Enjuague Rápido", "descripcion": "Enjuague con agua a presión para quitar polvo y suciedad superficial", "precio_min": 8000, "precio_max": 12000},
            {"nombre": "Lavado Express", "descripcion": "Lavado rápido exterior en 15 minutos", "precio_min": 18000, "precio_max": 28000},
            
            # LAVADO PREMIUM
            {"nombre": "Lavado Premium Exterior", "descripcion": "Lavado exterior con cera, brillo de llantas y protección de plásticos", "precio_min": 35000, "precio_max": 50000},
            {"nombre": "Lavado Premium Interior", "descripcion": "Limpieza profunda interior con productos especializados y aromatización", "precio_min": 30000, "precio_max": 45000},
            {"nombre": "Lavado VIP Completo", "descripcion": "Servicio completo premium exterior e interior con cera y detailing", "precio_min": 60000, "precio_max": 90000},
            {"nombre": "Lavado de Lujo", "descripcion": "Servicio exclusivo con productos de alta gama y acabados perfectos", "precio_min": 80000, "precio_max": 120000},
            {"nombre": "Spa Automotriz", "descripcion": "Tratamiento completo de embellecimiento vehicular", "precio_min": 100000, "precio_max": 150000},
            
            # ENCERADO Y PROTECCIÓN
            {"nombre": "Encerado Básico", "descripcion": "Aplicación de cera protectora para dar brillo y protección", "precio_min": 20000, "precio_max": 30000},
            {"nombre": "Encerado Premium", "descripcion": "Cera de alta calidad con duración extendida", "precio_min": 35000, "precio_max": 50000},
            {"nombre": "Cera Líquida", "descripcion": "Aplicación de cera líquida de secado rápido", "precio_min": 25000, "precio_max": 35000},
            {"nombre": "Cera Carnauba", "descripcion": "Cera natural carnauba para máximo brillo", "precio_min": 45000, "precio_max": 65000},
            {"nombre": "Sellador de Pintura", "descripcion": "Protección avanzada de la pintura contra rayos UV", "precio_min": 50000, "precio_max": 75000},
            {"nombre": "Coating Cerámico", "descripcion": "Protección cerámica de larga duración", "precio_min": 150000, "precio_max": 250000},
            
            # DETAILING ESPECÍFICO
            {"nombre": "Pulido de Faros", "descripcion": "Restauración y pulido de faros opacos", "precio_min": 25000, "precio_max": 40000},
            {"nombre": "Pulido de Pintura", "descripcion": "Eliminación de rayones menores y restauración del brillo", "precio_min": 60000, "precio_max": 100000},
            {"nombre": "Detailing de Llantas", "descripcion": "Limpieza profunda y brillo de llantas y rines", "precio_min": 15000, "precio_max": 25000},
            {"nombre": "Limpieza de Tapicería", "descripcion": "Limpieza profunda de asientos de tela o cuero", "precio_min": 35000, "precio_max": 55000},
            {"nombre": "Lavado de Alfombrillas", "descripcion": "Lavado y desinfección de alfombrillas removibles", "precio_min": 10000, "precio_max": 18000},
            {"nombre": "Limpieza de Cuero", "descripcion": "Tratamiento especializado para asientos de cuero", "precio_min": 40000, "precio_max": 60000},
            
            # MOTOR Y COMPARTIMENTO
            {"nombre": "Lavado de Motor", "descripcion": "Limpieza y desengrase del compartimento del motor", "precio_min": 30000, "precio_max": 50000},
            {"nombre": "Desengrase de Motor", "descripcion": "Eliminación de grasa y aceite acumulado en el motor", "precio_min": 25000, "precio_max": 40000},
            {"nombre": "Detailing de Motor", "descripcion": "Limpieza detallada y protección del compartimento del motor", "precio_min": 45000, "precio_max": 70000},
            {"nombre": "Limpieza de Radiador", "descripcion": "Limpieza externa del radiador para mejor enfriamiento", "precio_min": 20000, "precio_max": 30000},
            
            # SERVICIOS ESPECIALES
            {"nombre": "Eliminación de Olores", "descripcion": "Tratamiento para eliminar olores persistentes del interior", "precio_min": 25000, "precio_max": 40000},
            {"nombre": "Desinfección Interior", "descripcion": "Sanitización completa del habitáculo", "precio_min": 20000, "precio_max": 35000},
            {"nombre": "Aromatización", "descripcion": "Aplicación de fragancia personalizada", "precio_min": 8000, "precio_max": 15000},
            {"nombre": "Limpieza de Vidrios", "descripcion": "Limpieza especializada de cristales interior y exterior", "precio_min": 12000, "precio_max": 20000},
            {"nombre": "Anti-empañante", "descripcion": "Aplicación de producto anti-empañante en vidrios", "precio_min": 15000, "precio_max": 25000},
            
            # SERVICIOS POR VEHÍCULO
            {"nombre": "Lavado de Motocicleta", "descripcion": "Lavado especializado para motocicletas", "precio_min": 12000, "precio_max": 20000},
            {"nombre": "Lavado de Camioneta", "descripcion": "Lavado específico para vehículos grandes", "precio_min": 30000, "precio_max": 50000},
            {"nombre": "Lavado de Bus", "descripcion": "Lavado profesional para buses y microbuses", "precio_min": 50000, "precio_max": 80000},
            {"nombre": "Lavado de Camión", "descripcion": "Servicio especializado para vehículos pesados", "precio_min": 60000, "precio_max": 100000},
            {"nombre": "Lavado de Taxi", "descripcion": "Servicio rápido y económico para taxis", "precio_min": 15000, "precio_max": 25000},
            
            # SERVICIOS ADICIONALES
            {"nombre": "Aspirado Profundo", "descripcion": "Aspirado minucioso de todo el interior", "precio_min": 15000, "precio_max": 25000},
            {"nombre": "Limpieza de Maletero", "descripcion": "Limpieza completa del área de carga", "precio_min": 10000, "precio_max": 18000},
            {"nombre": "Shampoo de Alfombras", "descripcion": "Lavado profundo de alfombras y tapetes", "precio_min": 20000, "precio_max": 35000},
            {"nombre": "Limpieza de Consola", "descripcion": "Limpieza detallada del tablero y consola central", "precio_min": 12000, "precio_max": 20000},
            {"nombre": "Protección de Plásticos", "descripcion": "Aplicación de protector para plásticos exteriores", "precio_min": 18000, "precio_max": 28000},
            
            # SERVICIOS ESTACIONALES
            {"nombre": "Preparación para Invierno", "descripcion": "Tratamiento especial para temporada de lluvias", "precio_min": 35000, "precio_max": 55000},
            {"nombre": "Preparación para Verano", "descripcion": "Protección especial contra rayos UV y calor", "precio_min": 30000, "precio_max": 50000},
            {"nombre": "Lavado Post-Lluvia", "descripcion": "Limpieza especial después de días lluviosos", "precio_min": 20000, "precio_max": 30000},
            {"nombre": "Limpieza Anti-Polen", "descripcion": "Eliminación de polen y partículas estacionales", "precio_min": 15000, "precio_max": 25000},
            
            # SERVICIOS ECOLÓGICOS
            {"nombre": "Lavado Ecológico", "descripcion": "Lavado con productos biodegradables y ahorro de agua", "precio_min": 25000, "precio_max": 40000},
            {"nombre": "Lavado sin Agua", "descripcion": "Limpieza con productos especiales sin uso de agua", "precio_min": 30000, "precio_max": 45000},
            {"nombre": "Steam Cleaning", "descripcion": "Limpieza con vapor para desinfección profunda", "precio_min": 40000, "precio_max": 60000},
            
            # SERVICIOS DE MANTENIMIENTO
            {"nombre": "Revisión de Llantas", "descripcion": "Inspección básica del estado de las llantas", "precio_min": 8000, "precio_max": 15000},
            {"nombre": "Inflado de Llantas", "descripcion": "Verificación y ajuste de presión de aire", "precio_min": 5000, "precio_max": 10000},
            {"nombre": "Limpieza de Filtro de Aire", "descripcion": "Limpieza básica del filtro de aire del habitáculo", "precio_min": 12000, "precio_max": 20000},
            
            # SERVICIOS PREMIUM ESPECIALIZADOS
            {"nombre": "Paint Protection Film", "descripcion": "Instalación de película protectora transparente", "precio_min": 200000, "precio_max": 400000},
            {"nombre": "Tintado de Vidrios", "descripcion": "Aplicación de lámina solar en cristales", "precio_min": 80000, "precio_max": 150000},
            {"nombre": "Restauración de Convertible", "descripcion": "Limpieza y tratamiento de capota convertible", "precio_min": 60000, "precio_max": 100000},
            
            # SERVICIOS CORPORATIVOS
            {"nombre": "Lavado Flotilla Pequeña", "descripcion": "Descuento para 3-5 vehículos", "precio_min": 20000, "precio_max": 35000},
            {"nombre": "Lavado Flotilla Grande", "descripcion": "Servicio empresarial para más de 10 vehículos", "precio_min": 18000, "precio_max": 30000},
            {"nombre": "Suscripción Mensual", "descripcion": "Plan mensual de lavados ilimitados", "precio_min": 100000, "precio_max": 200000},
            {"nombre": "Suscripción Semanal", "descripcion": "Plan semanal para vehículos comerciales", "precio_min": 50000, "precio_max": 80000},
        ]
        
        # Servicios adicionales generados dinámicamente
        servicios_extra = []
        
        # Variaciones de productos
        productos = ["Jabón Premium", "Cera Sintética", "Protector UV", "Desengrasante", "Aromatizante", 
                    "Shampoo Especial", "Brillo Diamante", "Protector de Cuero", "Limpia Vidrios"]
        
        aplicaciones = ["Aplicación de", "Tratamiento con", "Servicio de", "Uso de"]
        
        for producto in productos:
            for aplicacion in aplicaciones:
                if len(servicios_extra) < 20:  # Limitar a 20 extras
                    precio_base = random.randint(15000, 60000)
                    servicios_extra.append({
                        "nombre": f"{aplicacion} {producto}",
                        "descripcion": f"{aplicacion.lower()} {producto.lower()} especializado para vehículos",
                        "precio_min": precio_base,
                        "precio_max": precio_base + random.randint(10000, 30000)
                    })
        
        # Combinar todos los servicios
        todos_los_servicios = servicios_data + servicios_extra
        
        # Si necesitamos más servicios, generar algunos adicionales
        while len(todos_los_servicios) < cantidad:
            tipo_servicio = random.choice(["Lavado", "Limpieza", "Pulido", "Detailing", "Tratamiento"])
            parte_vehiculo = random.choice(["Exterior", "Interior", "Motor", "Llantas", "Vidrios", "Tapicería"])
            nivel = random.choice(["Básico", "Premium", "Profesional", "Express", "Completo"])
            
            nombre = f"{tipo_servicio} {parte_vehiculo} {nivel}"
            descripcion = f"{tipo_servicio.lower()} especializado de {parte_vehiculo.lower()} nivel {nivel.lower()}"
            precio_base = random.randint(10000, 80000)
            
            todos_los_servicios.append({
                "nombre": nombre,
                "descripcion": descripcion,
                "precio_min": precio_base,
                "precio_max": precio_base + random.randint(10000, 40000)
            })
        
        servicios_creados = 0
        servicios_fallidos = 0
        servicios_duplicados = 0
        
        self.stdout.write(
            self.style.SUCCESS(f'🔧 Iniciando creación de {cantidad} servicios...')
        )
        
        # Tomar solo la cantidad solicitada
        servicios_a_crear = todos_los_servicios[:cantidad]
        
        for i, servicio_data in enumerate(servicios_a_crear):
            try:
                # Verificar si el servicio ya existe
                if Servicio.objects.filter(nombre_servicio=servicio_data["nombre"]).exists():
                    servicios_duplicados += 1
                    continue
                
                # Generar precio aleatorio dentro del rango
                precio = random.randint(servicio_data["precio_min"], servicio_data["precio_max"])
                
                # Crear el servicio
                servicio = Servicio.objects.create(
                    nombre_servicio=servicio_data["nombre"],
                    descripcion=servicio_data["descripcion"],
                    precio=precio
                )
                
                servicios_creados += 1
                
                # Mostrar progreso cada 10 servicios
                if (i + 1) % 10 == 0:
                    self.stdout.write(f"✅ Progreso: {i + 1}/{cantidad} servicios procesados...")
                
            except Exception as e:
                servicios_fallidos += 1
                self.stdout.write(
                    self.style.WARNING(f"⚠️  Error al crear servicio {i + 1}: {str(e)}")
                )
                continue
        
        # Mostrar resumen final
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Proceso completado:')
        )
        self.stdout.write(f"   - Servicios creados: {servicios_creados}")
        self.stdout.write(f"   - Servicios duplicados (omitidos): {servicios_duplicados}")
        self.stdout.write(f"   - Servicios fallidos: {servicios_fallidos}")
        
        if servicios_creados > 0:
            # Mostrar algunos servicios de ejemplo
            servicios_ejemplo = Servicio.objects.order_by('-id_servicio')[:5]
            self.stdout.write(f"\n📋 Últimos 5 servicios creados:")
            for servicio in servicios_ejemplo:
                precio_formateado = f"${servicio.precio:,.0f}".replace(",", ".")
                self.stdout.write(f"   • {servicio.nombre_servicio} - {precio_formateado}")
                self.stdout.write(f"     {servicio.descripcion[:80]}...")
        
        # Mostrar estadísticas generales
        total_servicios = Servicio.objects.count()
        precio_promedio = Servicio.objects.aggregate(promedio=models.Avg('precio'))['promedio']
        precio_min = Servicio.objects.aggregate(minimo=models.Min('precio'))['minimo']
        precio_max = Servicio.objects.aggregate(maximo=models.Max('precio'))['maximo']
        
        self.stdout.write(f"\n📊 Estadísticas generales:")
        self.stdout.write(f"   - Total de servicios en sistema: {total_servicios}")
        if precio_promedio:
            self.stdout.write(f"   - Precio promedio: ${precio_promedio:,.0f}".replace(",", "."))
            self.stdout.write(f"   - Precio mínimo: ${precio_min:,.0f}".replace(",", "."))
            self.stdout.write(f"   - Precio máximo: ${precio_max:,.0f}".replace(",", "."))
