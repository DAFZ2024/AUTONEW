from django.core.management.base import BaseCommand
from django.db import models
from faker import Faker
import random
from decimal import Decimal

from lavado_auto.models import Plan, PlanEmpresarial, Servicio

class Command(BaseCommand):
    help = 'Crea 10 planes individuales y 10 planes empresariales con datos realistas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--individuales',
            type=int,
            default=10,
            help='Cantidad de planes individuales a crear (default: 10)'
        )
        parser.add_argument(
            '--empresariales',
            type=int,
            default=10,
            help='Cantidad de planes empresariales a crear (default: 10)'
        )

    def handle(self, *args, **options):
        fake = Faker('es_ES')
        planes_individuales = options['individuales']
        planes_empresariales = options['empresariales']
        
        self.stdout.write(
            self.style.SUCCESS(f'📋 Iniciando creación de planes...')
        )
        self.stdout.write(f'   - {planes_individuales} planes individuales')
        self.stdout.write(f'   - {planes_empresariales} planes empresariales')
        
        # Crear planes individuales
        planes_ind_creados = self.crear_planes_individuales(planes_individuales)
        
        # Crear planes empresariales
        planes_emp_creados = self.crear_planes_empresariales(planes_empresariales)
        
        self.mostrar_resumen_final(planes_ind_creados, planes_emp_creados)

    def crear_planes_individuales(self, cantidad):
        self.stdout.write(f'\n👤 Creando {cantidad} planes individuales...')
        
        # Definir estructura de planes individuales
        planes_data = [
            {
                "nombre": "Plan Básico Mensual",
                "tipo": "basico",
                "descripcion": "Plan básico ideal para uso personal con lavados esenciales",
                "precio": 89000,
                "servicios_mes": 4,
                "caracteristicas": {
                    "incluye_lavado_asientos": True,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": False,
                    "incluye_encerado": False,
                    "incluye_detallado_completo": False
                }
            },
            {
                "nombre": "Plan Económico",
                "tipo": "basico",
                "descripcion": "La opción más económica para mantener tu vehículo limpio",
                "precio": 59000,
                "servicios_mes": 2,
                "caracteristicas": {
                    "incluye_lavado_asientos": True,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": False,
                    "incluye_encerado": False,
                    "incluye_detallado_completo": False
                }
            },
            {
                "nombre": "Plan Premium Individual",
                "tipo": "premium",
                "descripcion": "Servicio premium con encerado y limpieza profunda",
                "precio": 159000,
                "servicios_mes": 6,
                "caracteristicas": {
                    "incluye_lavado_asientos": True,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": True,
                    "incluye_encerado": True,
                    "incluye_detallado_completo": False
                }
            },
            {
                "nombre": "Plan VIP Total",
                "tipo": "completo",
                "descripcion": "El plan más completo con detallado y servicios ilimitados",
                "precio": 299000,
                "servicios_mes": 0,  # Ilimitado
                "caracteristicas": {
                    "incluye_lavado_asientos": True,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": True,
                    "incluye_encerado": True,
                    "incluye_detallado_completo": True
                }
            },
            {
                "nombre": "Plan Fin de Semana",
                "tipo": "basico",
                "descripcion": "Perfecto para quienes usan el auto solo los fines de semana",
                "precio": 45000,
                "servicios_mes": 2,
                "caracteristicas": {
                    "incluye_lavado_asientos": True,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": False,
                    "incluye_encerado": False,
                    "incluye_detallado_completo": False
                }
            },
            {
                "nombre": "Plan Estudiante",
                "tipo": "basico",
                "descripcion": "Descuento especial para estudiantes universitarios",
                "precio": 39000,
                "servicios_mes": 2,
                "caracteristicas": {
                    "incluye_lavado_asientos": False,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": False,
                    "incluye_encerado": False,
                    "incluye_detallado_completo": False
                }
            },
            {
                "nombre": "Plan Ejecutivo",
                "tipo": "premium",
                "descripcion": "Para profesionales que necesitan mantener su imagen",
                "precio": 199000,
                "servicios_mes": 8,
                "caracteristicas": {
                    "incluye_lavado_asientos": True,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": True,
                    "incluye_encerado": True,
                    "incluye_detallado_completo": False
                }
            },
            {
                "nombre": "Plan Familiar",
                "tipo": "premium",
                "descripción": "Ideal para familias con niños, incluye limpieza profunda",
                "precio": 139000,
                "servicios_mes": 5,
                "caracteristicas": {
                    "incluye_lavado_asientos": True,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": True,
                    "incluye_encerado": False,
                    "incluye_detallado_completo": False
                }
            },
            {
                "nombre": "Plan Express Mensual",
                "tipo": "basico",
                "descripcion": "Lavados rápidos para personas ocupadas",
                "precio": 69000,
                "servicios_mes": 6,
                "caracteristicas": {
                    "incluye_lavado_asientos": False,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": False,
                    "incluye_encerado": False,
                    "incluye_detallado_completo": False
                }
            },
            {
                "nombre": "Plan Luxury Car",
                "tipo": "completo",
                "descripcion": "Servicio especializado para vehículos de lujo y alta gama",
                "precio": 459000,
                "servicios_mes": 0,  # Ilimitado
                "caracteristicas": {
                    "incluye_lavado_asientos": True,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": True,
                    "incluye_encerado": True,
                    "incluye_detallado_completo": True
                }
            }
        ]
        
        planes_creados = 0
        planes_fallidos = 0
        
        for i, plan_data in enumerate(planes_data[:cantidad]):
            try:
                # Verificar si el plan ya existe
                if Plan.objects.filter(nombre=plan_data["nombre"]).exists():
                    self.stdout.write(f"⚠️  Plan '{plan_data['nombre']}' ya existe, omitiendo...")
                    continue
                
                # Crear el plan
                plan = Plan.objects.create(
                    nombre=plan_data["nombre"],
                    tipo=plan_data["tipo"],
                    descripcion=plan_data.get("descripcion", plan_data.get("descripción", "")),
                    precio_mensual=Decimal(str(plan_data["precio"])),
                    cantidad_servicios_mes=plan_data["servicios_mes"],
                    **plan_data["caracteristicas"]
                )
                
                # Asignar servicios aleatorios (2-8 servicios por plan)
                servicios_disponibles = list(Servicio.objects.all())
                if servicios_disponibles:
                    cantidad_servicios = random.randint(2, min(8, len(servicios_disponibles)))
                    servicios_seleccionados = random.sample(servicios_disponibles, cantidad_servicios)
                    plan.servicios_incluidos.set(servicios_seleccionados)
                
                planes_creados += 1
                self.stdout.write(f"✅ Plan individual creado: {plan.nombre} - ${plan.precio_mensual:,.0f}".replace(",", "."))
                
            except Exception as e:
                planes_fallidos += 1
                self.stdout.write(
                    self.style.WARNING(f"⚠️  Error al crear plan individual {i + 1}: {str(e)}")
                )
                continue
        
        return {"creados": planes_creados, "fallidos": planes_fallidos}

    def crear_planes_empresariales(self, cantidad):
        self.stdout.write(f'\n🏢 Creando {cantidad} planes empresariales...')
        
        # Definir estructura de planes empresariales
        planes_data = [
            {
                "nombre": "Plan Flota Básica",
                "tipo": "basico_flota",
                "descripcion": "Plan básico para pequeñas flotas de vehículos comerciales",
                "precio_por_vehiculo": 45000,
                "precio_base": 100000,
                "vehiculos_min": 3,
                "vehiculos_max": 15,
                "servicios_por_vehiculo": 2,
                "descuento": 5,
                "caracteristicas": {
                    "incluye_lavado_asientos": True,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": False,
                    "incluye_encerado": False,
                    "incluye_detallado_completo": False,
                    "incluye_servicio_domicilio": False,
                    "incluye_mantenimiento_programado": False,
                    "incluye_reporte_mensual": True,
                    "incluye_soporte_24_7": False
                }
            },
            {
                "nombre": "Plan Taxi & Uber",
                "tipo": "transporte_publico",
                "descripcion": "Especializado para conductores de taxi y plataformas digitales",
                "precio_por_vehiculo": 39000,
                "precio_base": 50000,
                "vehiculos_min": 1,
                "vehiculos_max": 10,
                "servicios_por_vehiculo": 6,
                "descuento": 10,
                "caracteristicas": {
                    "incluye_lavado_asientos": True,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": True,
                    "incluye_encerado": False,
                    "incluye_detallado_completo": False,
                    "incluye_servicio_domicilio": False,
                    "incluye_mantenimiento_programado": True,
                    "incluye_reporte_mensual": False,
                    "incluye_soporte_24_7": False
                }
            },
            {
                "nombre": "Plan Corporativo Premium",
                "tipo": "corporativo",
                "descripcion": "Solución completa para empresas con alta imagen corporativa",
                "precio_por_vehiculo": 89000,
                "precio_base": 300000,
                "vehiculos_min": 10,
                "vehiculos_max": 50,
                "servicios_por_vehiculo": 4,
                "descuento": 15,
                "caracteristicas": {
                    "incluye_lavado_asientos": True,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": True,
                    "incluye_encerado": True,
                    "incluye_detallado_completo": False,
                    "incluye_servicio_domicilio": True,
                    "incluye_mantenimiento_programado": True,
                    "incluye_reporte_mensual": True,
                    "incluye_soporte_24_7": True
                }
            },
            {
                "nombre": "Plan Mega Flota",
                "tipo": "corporativo",
                "descripcion": "Para grandes empresas con flotas extensas",
                "precio_por_vehiculo": 35000,
                "precio_base": 500000,
                "vehiculos_min": 50,
                "vehiculos_max": None,  # Ilimitado
                "servicios_por_vehiculo": 3,
                "descuento": 25,
                "caracteristicas": {
                    "incluye_lavado_asientos": True,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": True,
                    "incluye_encerado": False,
                    "incluye_detallado_completo": False,
                    "incluye_servicio_domicilio": True,
                    "incluye_mantenimiento_programado": True,
                    "incluye_reporte_mensual": True,
                    "incluye_soporte_24_7": True
                }
            },
            {
                "nombre": "Plan Transporte Público",
                "tipo": "transporte_publico",
                "descripcion": "Especializado para buses, colectivos y transporte masivo",
                "precio_por_vehiculo": 89000,
                "precio_base": 200000,
                "vehiculos_min": 5,
                "vehiculos_max": 100,
                "servicios_por_vehiculo": 2,
                "descuento": 20,
                "caracteristicas": {
                    "incluye_lavado_asientos": True,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": True,
                    "incluye_encerado": False,
                    "incluye_detallado_completo": False,
                    "incluye_servicio_domicilio": False,
                    "incluye_mantenimiento_programado": True,
                    "incluye_reporte_mensual": True,
                    "incluye_soporte_24_7": False
                }
            },
            {
                "nombre": "Plan Startup",
                "tipo": "basico_flota",
                "descripcion": "Ideal para empresas emergentes con presupuesto ajustado",
                "precio_por_vehiculo": 29000,
                "precio_base": 75000,
                "vehiculos_min": 2,
                "vehiculos_max": 8,
                "servicios_por_vehiculo": 2,
                "descuento": 0,
                "caracteristicas": {
                    "incluye_lavado_asientos": False,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": False,
                    "incluye_encerado": False,
                    "incluye_detallado_completo": False,
                    "incluye_servicio_domicilio": False,
                    "incluye_mantenimiento_programado": False,
                    "incluye_reporte_mensual": False,
                    "incluye_soporte_24_7": False
                }
            },
            {
                "nombre": "Plan Delivery Premium",
                "tipo": "premium_flota",
                "descripcion": "Para empresas de delivery que necesitan vehículos impecables",
                "precio_por_vehiculo": 59000,
                "precio_base": 150000,
                "vehiculos_min": 5,
                "vehiculos_max": 30,
                "servicios_por_vehiculo": 4,
                "descuento": 12,
                "caracteristicas": {
                    "incluye_lavado_asientos": True,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": True,
                    "incluye_encerado": False,
                    "incluye_detallado_completo": False,
                    "incluye_servicio_domicilio": True,
                    "incluye_mantenimiento_programado": True,
                    "incluye_reporte_mensual": True,
                    "incluye_soporte_24_7": False
                }
            },
            {
                "nombre": "Plan Ejecutivo Empresarial",
                "tipo": "premium_flota",
                "descripcion": "Para vehículos ejecutivos y de alta representación",
                "precio_por_vehiculo": 129000,
                "precio_base": 250000,
                "vehiculos_min": 3,
                "vehiculos_max": 20,
                "servicios_por_vehiculo": 6,
                "descuento": 8,
                "caracteristicas": {
                    "incluye_lavado_asientos": True,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": True,
                    "incluye_encerado": True,
                    "incluye_detallado_completo": True,
                    "incluye_servicio_domicilio": True,
                    "incluye_mantenimiento_programado": True,
                    "incluye_reporte_mensual": True,
                    "incluye_soporte_24_7": True
                }
            },
            {
                "nombre": "Plan Moto Flota",
                "tipo": "basico_flota",
                "descripcion": "Especializado para flotas de motocicletas y domicilios",
                "precio_por_vehiculo": 19000,
                "precio_base": 40000,
                "vehiculos_min": 5,
                "vehiculos_max": 50,
                "servicios_por_vehiculo": 4,
                "descuento": 15,
                "caracteristicas": {
                    "incluye_lavado_asientos": True,
                    "incluye_aspirado": False,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": False,
                    "incluye_encerado": False,
                    "incluye_detallado_completo": False,
                    "incluye_servicio_domicilio": False,
                    "incluye_mantenimiento_programado": True,
                    "incluye_reporte_mensual": False,
                    "incluye_soporte_24_7": False
                }
            },
            {
                "nombre": "Plan VIP Corporativo",
                "tipo": "corporativo",
                "descripcion": "El plan más exclusivo para corporaciones de élite",
                "precio_por_vehiculo": 199000,
                "precio_base": 800000,
                "vehiculos_min": 5,
                "vehiculos_max": 25,
                "servicios_por_vehiculo": 0,  # Ilimitado
                "descuento": 10,
                "caracteristicas": {
                    "incluye_lavado_asientos": True,
                    "incluye_aspirado": True,
                    "incluye_lavado_exterior": True,
                    "incluye_lavado_interior_humedo": True,
                    "incluye_encerado": True,
                    "incluye_detallado_completo": True,
                    "incluye_servicio_domicilio": True,
                    "incluye_mantenimiento_programado": True,
                    "incluye_reporte_mensual": True,
                    "incluye_soporte_24_7": True
                }
            }
        ]
        
        planes_creados = 0
        planes_fallidos = 0
        
        for i, plan_data in enumerate(planes_data[:cantidad]):
            try:
                # Verificar si el plan ya existe
                if PlanEmpresarial.objects.filter(nombre=plan_data["nombre"]).exists():
                    self.stdout.write(f"⚠️  Plan '{plan_data['nombre']}' ya existe, omitiendo...")
                    continue
                
                # Crear el plan empresarial
                plan = PlanEmpresarial.objects.create(
                    nombre=plan_data["nombre"],
                    tipo=plan_data["tipo"],
                    descripcion=plan_data["descripcion"],
                    precio_mensual_por_vehiculo=Decimal(str(plan_data["precio_por_vehiculo"])),
                    precio_base_mensual=Decimal(str(plan_data["precio_base"])),
                    vehiculos_minimos=plan_data["vehiculos_min"],
                    vehiculos_maximos=plan_data["vehiculos_max"],
                    servicios_por_vehiculo_mes=plan_data["servicios_por_vehiculo"],
                    descuento_volumen=Decimal(str(plan_data["descuento"])),
                    **plan_data["caracteristicas"]
                )
                
                # Asignar servicios aleatorios (3-10 servicios por plan)
                servicios_disponibles = list(Servicio.objects.all())
                if servicios_disponibles:
                    cantidad_servicios = random.randint(3, min(10, len(servicios_disponibles)))
                    servicios_seleccionados = random.sample(servicios_disponibles, cantidad_servicios)
                    plan.servicios_incluidos.set(servicios_seleccionados)
                
                planes_creados += 1
                precio_ejemplo = plan.calcular_precio_total(plan.vehiculos_minimos)
                self.stdout.write(f"✅ Plan empresarial creado: {plan.nombre} - ${plan.precio_mensual_por_vehiculo:,.0f}/veh (Ej: ${precio_ejemplo:,.0f} para {plan.vehiculos_minimos} veh)".replace(",", "."))
                
            except Exception as e:
                planes_fallidos += 1
                self.stdout.write(
                    self.style.WARNING(f"⚠️  Error al crear plan empresarial {i + 1}: {str(e)}")
                )
                continue
        
        return {"creados": planes_creados, "fallidos": planes_fallidos}

    def mostrar_resumen_final(self, resultado_ind, resultado_emp):
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Proceso completado:')
        )
        self.stdout.write(f"   📋 Planes individuales:")
        self.stdout.write(f"      - Creados: {resultado_ind['creados']}")
        self.stdout.write(f"      - Fallidos: {resultado_ind['fallidos']}")
        
        self.stdout.write(f"   🏢 Planes empresariales:")
        self.stdout.write(f"      - Creados: {resultado_emp['creados']}")
        self.stdout.write(f"      - Fallidos: {resultado_emp['fallidos']}")
        
        # Mostrar estadísticas generales
        total_planes_ind = Plan.objects.count()
        total_planes_emp = PlanEmpresarial.objects.count()
        
        self.stdout.write(f"\n📊 Estadísticas generales:")
        self.stdout.write(f"   - Total planes individuales: {total_planes_ind}")
        self.stdout.write(f"   - Total planes empresariales: {total_planes_emp}")
        
        if total_planes_ind > 0:
            precio_promedio_ind = Plan.objects.aggregate(promedio=models.Avg('precio_mensual'))['promedio']
            precio_min_ind = Plan.objects.aggregate(minimo=models.Min('precio_mensual'))['minimo']
            precio_max_ind = Plan.objects.aggregate(maximo=models.Max('precio_mensual'))['maximo']
            
            self.stdout.write(f"\n💰 Precios planes individuales:")
            self.stdout.write(f"   - Promedio: ${precio_promedio_ind:,.0f}".replace(",", "."))
            self.stdout.write(f"   - Mínimo: ${precio_min_ind:,.0f}".replace(",", "."))
            self.stdout.write(f"   - Máximo: ${precio_max_ind:,.0f}".replace(",", "."))
        
        if total_planes_emp > 0:
            precio_promedio_emp = PlanEmpresarial.objects.aggregate(promedio=models.Avg('precio_mensual_por_vehiculo'))['promedio']
            precio_min_emp = PlanEmpresarial.objects.aggregate(minimo=models.Min('precio_mensual_por_vehiculo'))['minimo']
            precio_max_emp = PlanEmpresarial.objects.aggregate(maximo=models.Max('precio_mensual_por_vehiculo'))['maximo']
            
            self.stdout.write(f"\n🏢 Precios planes empresariales (por vehículo):")
            self.stdout.write(f"   - Promedio: ${precio_promedio_emp:,.0f}".replace(",", "."))
            self.stdout.write(f"   - Mínimo: ${precio_min_emp:,.0f}".replace(",", "."))
            self.stdout.write(f"   - Máximo: ${precio_max_emp:,.0f}".replace(",", "."))
