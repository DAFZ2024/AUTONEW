from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from faker import Faker
import random
from decimal import Decimal
from datetime import timedelta

from lavado_auto.models import (
    SuscripcionUsuario, SuscripcionEmpresarial, 
    Usuario, Empresa, Plan, PlanEmpresarial
)

class Command(BaseCommand):
    help = 'Crea 100 suscripciones individuales y 100 suscripciones empresariales con datos realistas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--individuales',
            type=int,
            default=100,
            help='Cantidad de suscripciones individuales a crear (default: 100)'
        )
        parser.add_argument(
            '--empresariales',
            type=int,
            default=100,
            help='Cantidad de suscripciones empresariales a crear (default: 100)'
        )

    def handle(self, *args, **options):
        fake = Faker('es_ES')
        suscripciones_individuales = options['individuales']
        suscripciones_empresariales = options['empresariales']
        
        self.stdout.write(
            self.style.SUCCESS(f'📋 Iniciando creación de suscripciones...')
        )
        self.stdout.write(f'   - {suscripciones_individuales} suscripciones individuales')
        self.stdout.write(f'   - {suscripciones_empresariales} suscripciones empresariales')
        
        # Verificar que existan usuarios, empresas y planes
        if not self.verificar_prerequisitos():
            return
        
        # Crear suscripciones individuales
        suscripciones_ind_creadas = self.crear_suscripciones_individuales(suscripciones_individuales)
        
        # Crear suscripciones empresariales
        suscripciones_emp_creadas = self.crear_suscripciones_empresariales(suscripciones_empresariales)
        
        self.mostrar_resumen_final(suscripciones_ind_creadas, suscripciones_emp_creadas)

    def verificar_prerequisitos(self):
        """Verifica que existan los datos necesarios para crear suscripciones"""
        usuarios_count = Usuario.objects.count()
        empresas_count = Empresa.objects.count()
        planes_ind_count = Plan.objects.count()
        planes_emp_count = PlanEmpresarial.objects.count()
        
        self.stdout.write(f'\n🔍 Verificando prerequisitos:')
        self.stdout.write(f'   - Usuarios disponibles: {usuarios_count}')
        self.stdout.write(f'   - Empresas disponibles: {empresas_count}')
        self.stdout.write(f'   - Planes individuales: {planes_ind_count}')
        self.stdout.write(f'   - Planes empresariales: {planes_emp_count}')
        
        if usuarios_count < 10:
            self.stdout.write(
                self.style.ERROR(f'❌ Necesitas al menos 10 usuarios. Tienes {usuarios_count}')
            )
            return False
            
        if empresas_count < 10:
            self.stdout.write(
                self.style.ERROR(f'❌ Necesitas al menos 10 empresas. Tienes {empresas_count}')
            )
            return False
            
        if planes_ind_count < 1:
            self.stdout.write(
                self.style.ERROR(f'❌ Necesitas al menos 1 plan individual. Tienes {planes_ind_count}')
            )
            return False
            
        if planes_emp_count < 1:
            self.stdout.write(
                self.style.ERROR(f'❌ Necesitas al menos 1 plan empresarial. Tienes {planes_emp_count}')
            )
            return False
        
        self.stdout.write(self.style.SUCCESS('✅ Todos los prerequisitos están cumplidos'))
        return True

    def crear_suscripciones_individuales(self, cantidad):
        self.stdout.write(f'\n👤 Creando {cantidad} suscripciones individuales...')
        
        # Obtener datos necesarios
        usuarios = list(Usuario.objects.all())
        planes = list(Plan.objects.all())
        
        if len(usuarios) == 0 or len(planes) == 0:
            self.stdout.write(self.style.ERROR('❌ No hay usuarios o planes disponibles'))
            return {"creadas": 0, "fallidas": 0}
        
        suscripciones_creadas = 0
        suscripciones_fallidas = 0
        
        # Estados posibles con probabilidades realistas
        estados_probabilidades = [
            ('activa', 70),      # 70% activas
            ('pausada', 15),     # 15% pausadas
            ('cancelada', 10),   # 10% canceladas
            ('vencida', 5)       # 5% vencidas
        ]
        
        for i in range(cantidad):
            try:
                # Seleccionar usuario aleatorio (puede tener múltiples suscripciones)
                usuario = random.choice(usuarios)
                plan = random.choice(planes)
                
                # Verificar si ya tiene una suscripción activa con este plan
                if SuscripcionUsuario.objects.filter(
                    usuario=usuario, 
                    plan=plan, 
                    estado='activa'
                ).exists():
                    # Si ya tiene el plan activo, elegir otro plan
                    planes_disponibles = [p for p in planes if not SuscripcionUsuario.objects.filter(
                        usuario=usuario, plan=p, estado='activa'
                    ).exists()]
                    if planes_disponibles:
                        plan = random.choice(planes_disponibles)
                    else:
                        # Si ya tiene todos los planes activos, continuar de todas formas
                        pass
                
                # Generar fechas realistas
                fecha_inicio = self.generar_fecha_inicio()
                fecha_fin = fecha_inicio + timedelta(days=30)
                
                # Determinar estado basado en probabilidades
                estado = self.elegir_estado_aleatorio(estados_probabilidades, fecha_inicio, fecha_fin)
                
                # Ajustar fechas si está vencida
                if estado == 'vencida':
                    dias_vencida = random.randint(1, 30)
                    fecha_fin = timezone.now() - timedelta(days=dias_vencida)
                    fecha_inicio = fecha_fin - timedelta(days=30)
                
                # Servicios utilizados realistas
                servicios_utilizados = self.calcular_servicios_utilizados(plan, estado, fecha_inicio)
                
                # Determinar auto_renovar basado en estado
                auto_renovar = estado in ['activa', 'pausada'] and random.choice([True, True, True, False])  # 75% auto-renuevan
                
                # Crear la suscripción
                suscripcion = SuscripcionUsuario.objects.create(
                    usuario=usuario,
                    plan=plan,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    estado=estado,
                    servicios_utilizados_mes=servicios_utilizados,
                    ultimo_reinicio_contador=fecha_inicio,
                    auto_renovar=auto_renovar
                )
                
                suscripciones_creadas += 1
                
                if i % 20 == 0:  # Mostrar progreso cada 20 suscripciones
                    self.stdout.write(f"   ✅ {i + 1}/{cantidad} suscripciones individuales creadas...")
                
            except Exception as e:
                suscripciones_fallidas += 1
                if suscripciones_fallidas <= 5:  # Solo mostrar los primeros 5 errores
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  Error en suscripción individual {i + 1}: {str(e)}")
                    )
                continue
        
        self.stdout.write(f"✅ Suscripciones individuales completadas: {suscripciones_creadas} creadas, {suscripciones_fallidas} fallidas")
        return {"creadas": suscripciones_creadas, "fallidas": suscripciones_fallidas}

    def crear_suscripciones_empresariales(self, cantidad):
        self.stdout.write(f'\n🏢 Creando {cantidad} suscripciones empresariales...')
        
        # Obtener datos necesarios
        empresas = list(Empresa.objects.all())
        planes = list(PlanEmpresarial.objects.all())
        
        if len(empresas) == 0 or len(planes) == 0:
            self.stdout.write(self.style.ERROR('❌ No hay empresas o planes empresariales disponibles'))
            return {"creadas": 0, "fallidas": 0}
        
        suscripciones_creadas = 0
        suscripciones_fallidas = 0
        
        # Estados posibles con probabilidades para empresas
        estados_probabilidades = [
            ('activa', 80),      # 80% activas (las empresas suelen ser más constantes)
            ('pausada', 10),     # 10% pausadas
            ('cancelada', 7),    # 7% canceladas
            ('vencida', 3)       # 3% vencidas
        ]
        
        # Lista de contactos responsables realistas
        contactos_responsables = [
            "Gerente de Flota", "Director de Operaciones", "Jefe de Mantenimiento",
            "Coordinador de Vehículos", "Supervisor de Transporte", "Gerente General",
            "Jefe de Logística", "Director Administrativo", "Coordinador de Servicios",
            "Gerente de Recursos", "Jefe de Compras", "Director de Flota"
        ]
        
        for i in range(cantidad):
            try:
                # Seleccionar empresa y plan aleatorio
                empresa = random.choice(empresas)
                plan = random.choice(planes)
                
                # Verificar si ya tiene una suscripción activa con este plan
                if SuscripcionEmpresarial.objects.filter(
                    empresa=empresa, 
                    plan=plan, 
                    estado='activa'
                ).exists():
                    # Si ya tiene el plan activo, elegir otro plan
                    planes_disponibles = [p for p in planes if not SuscripcionEmpresarial.objects.filter(
                        empresa=empresa, plan=p, estado='activa'
                    ).exists()]
                    if planes_disponibles:
                        plan = random.choice(planes_disponibles)
                
                # Generar cantidad de vehículos dentro del rango del plan
                cantidad_vehiculos = self.generar_cantidad_vehiculos(plan)
                
                # Generar fechas realistas
                fecha_inicio = self.generar_fecha_inicio()
                fecha_fin = fecha_inicio + timedelta(days=30)
                
                # Determinar estado basado en probabilidades
                estado = self.elegir_estado_aleatorio(estados_probabilidades, fecha_inicio, fecha_fin)
                
                # Ajustar fechas si está vencida
                if estado == 'vencida':
                    dias_vencida = random.randint(1, 30)
                    fecha_fin = timezone.now() - timedelta(days=dias_vencida)
                    fecha_inicio = fecha_fin - timedelta(days=30)
                
                # Servicios utilizados realistas para empresas
                servicios_utilizados = self.calcular_servicios_utilizados_empresarial(
                    plan, cantidad_vehiculos, estado, fecha_inicio
                )
                
                # Determinar auto_renovar (las empresas tienden a auto-renovar más)
                auto_renovar = estado in ['activa', 'pausada'] and random.choice([True, True, True, True, False])  # 80% auto-renuevan
                
                # Calcular precio mensual actual
                precio_mensual_actual = plan.calcular_precio_total(cantidad_vehiculos)
                
                # Generar datos de contacto
                contacto_responsable = random.choice(contactos_responsables)
                telefono_contacto = self.generar_telefono_empresarial()
                notas_especiales = self.generar_notas_especiales() if random.choice([True, False, False]) else ""
                
                # Crear la suscripción empresarial
                suscripcion = SuscripcionEmpresarial.objects.create(
                    empresa=empresa,
                    plan=plan,
                    cantidad_vehiculos=cantidad_vehiculos,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    estado=estado,
                    servicios_utilizados_mes=servicios_utilizados,
                    ultimo_reinicio_contador=fecha_inicio,
                    auto_renovar=auto_renovar,
                    precio_mensual_actual=precio_mensual_actual,
                    contacto_responsable=contacto_responsable,
                    telefono_contacto=telefono_contacto,
                    notas_especiales=notas_especiales
                )
                
                suscripciones_creadas += 1
                
                if i % 20 == 0:  # Mostrar progreso cada 20 suscripciones
                    self.stdout.write(f"   ✅ {i + 1}/{cantidad} suscripciones empresariales creadas...")
                
            except Exception as e:
                suscripciones_fallidas += 1
                if suscripciones_fallidas <= 5:  # Solo mostrar los primeros 5 errores
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  Error en suscripción empresarial {i + 1}: {str(e)}")
                    )
                continue
        
        self.stdout.write(f"✅ Suscripciones empresariales completadas: {suscripciones_creadas} creadas, {suscripciones_fallidas} fallidas")
        return {"creadas": suscripciones_creadas, "fallidas": suscripciones_fallidas}

    def generar_fecha_inicio(self):
        """Genera una fecha de inicio realista (últimos 6 meses)"""
        ahora = timezone.now()
        dias_atras = random.randint(1, 180)  # Últimos 6 meses
        return ahora - timedelta(days=dias_atras)

    def elegir_estado_aleatorio(self, estados_probabilidades, fecha_inicio, fecha_fin):
        """Elige un estado aleatorio basado en probabilidades y fechas"""
        # Si la fecha de fin ya pasó, mayor probabilidad de estar vencida
        if fecha_fin < timezone.now():
            if random.randint(1, 100) <= 60:  # 60% de probabilidad de estar vencida si ya pasó la fecha
                return 'vencida'
        
        # Elegir basado en probabilidades normales
        numero_aleatorio = random.randint(1, 100)
        acumulado = 0
        
        for estado, probabilidad in estados_probabilidades:
            acumulado += probabilidad
            if numero_aleatorio <= acumulado:
                return estado
        
        return 'activa'  # Por defecto

    def calcular_servicios_utilizados(self, plan, estado, fecha_inicio):
        """Calcula servicios utilizados realistas para planes individuales"""
        if estado in ['cancelada', 'vencida']:
            if plan.cantidad_servicios_mes == 0:  # Ilimitado
                return random.randint(0, 15)
            else:
                return random.randint(0, plan.cantidad_servicios_mes)
        
        if estado == 'pausada':
            if plan.cantidad_servicios_mes == 0:
                return random.randint(0, 8)
            else:
                return random.randint(0, min(plan.cantidad_servicios_mes // 2, plan.cantidad_servicios_mes))
        
        # Estado activo
        if plan.cantidad_servicios_mes == 0:  # Ilimitado
            return random.randint(0, 20)
        else:
            # Entre 0 y cantidad_servicios_mes, con tendencia hacia usar la mayoría
            return random.randint(0, plan.cantidad_servicios_mes)

    def calcular_servicios_utilizados_empresarial(self, plan, cantidad_vehiculos, estado, fecha_inicio):
        """Calcula servicios utilizados realistas para planes empresariales"""
        servicios_totales_permitidos = plan.servicios_por_vehiculo_mes * cantidad_vehiculos
        
        if estado in ['cancelada', 'vencida']:
            if servicios_totales_permitidos == 0:  # Ilimitado
                return random.randint(0, cantidad_vehiculos * 8)
            else:
                return random.randint(0, servicios_totales_permitidos)
        
        if estado == 'pausada':
            if servicios_totales_permitidos == 0:
                return random.randint(0, cantidad_vehiculos * 4)
            else:
                return random.randint(0, servicios_totales_permitidos // 2)
        
        # Estado activo - las empresas tienden a usar más servicios
        if servicios_totales_permitidos == 0:  # Ilimitado
            return random.randint(cantidad_vehiculos, cantidad_vehiculos * 12)
        else:
            # Las empresas suelen usar entre 50% y 100% de sus servicios
            minimo = max(0, servicios_totales_permitidos // 2)
            return random.randint(minimo, servicios_totales_permitidos)

    def generar_cantidad_vehiculos(self, plan):
        """Genera una cantidad de vehículos realista para el plan"""
        minimo = plan.vehiculos_minimos
        maximo = plan.vehiculos_maximos if plan.vehiculos_maximos else minimo + 50
        
        # Dar más probabilidad a números menores (la mayoría de empresas tienen flotas pequeñas)
        if maximo - minimo <= 10:
            return random.randint(minimo, maximo)
        else:
            # Distribución sesgada hacia números menores
            rango = maximo - minimo
            factor = random.random() ** 2  # Esto sesga hacia números menores
            return minimo + int(factor * rango)

    def generar_telefono_empresarial(self):
        """Genera un número de teléfono empresarial colombiano"""
        # Teléfonos fijos de Bogotá (601) + 7 dígitos o celulares (3XX) + 7 dígitos
        if random.choice([True, False]):
            # Teléfono fijo Bogotá
            return f"601{random.randint(2000000, 9999999)}"
        else:
            # Celular
            prefijos = ['300', '301', '302', '310', '311', '312', '313', '314', '315', '316', '317', '318', '319', '320', '321', '322', '323']
            prefijo = random.choice(prefijos)
            return f"{prefijo}{random.randint(1000000, 9999999)}"

    def generar_notas_especiales(self):
        """Genera notas especiales realistas para suscripciones empresariales"""
        notas_posibles = [
            "Requiere servicio en horarios específicos de madrugada",
            "Flota incluye vehículos de carga pesada",
            "Necesita facturación electrónica con códigos específicos",
            "Vehículos utilizados para transporte de personal ejecutivo",
            "Requiere servicios de emergencia 24/7",
            "Flota incluye vehículos blindados - manejo especial",
            "Necesita reportes detallados semanales",
            "Vehículos con logos corporativos - cuidado especial",
            "Requiere certificación de lavado ecológico",
            "Flota rotativa - vehículos cambian mensualmente",
            "Necesita descuento adicional por volumen",
            "Vehículos para delivery - alta rotación diaria"
        ]
        return random.choice(notas_posibles)

    def mostrar_resumen_final(self, resultado_ind, resultado_emp):
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Proceso de suscripciones completado:')
        )
        
        # Resumen de creación
        self.stdout.write(f"   👤 Suscripciones individuales:")
        self.stdout.write(f"      - Creadas: {resultado_ind['creadas']}")
        self.stdout.write(f"      - Fallidas: {resultado_ind['fallidas']}")
        
        self.stdout.write(f"   🏢 Suscripciones empresariales:")
        self.stdout.write(f"      - Creadas: {resultado_emp['creadas']}")
        self.stdout.write(f"      - Fallidas: {resultado_emp['fallidas']}")
        
        # Estadísticas generales
        total_suscripciones_ind = SuscripcionUsuario.objects.count()
        total_suscripciones_emp = SuscripcionEmpresarial.objects.count()
        
        self.stdout.write(f"\n📊 Estadísticas generales:")
        self.stdout.write(f"   - Total suscripciones individuales: {total_suscripciones_ind}")
        self.stdout.write(f"   - Total suscripciones empresariales: {total_suscripciones_emp}")
        
        # Estadísticas por estado - Individuales
        if total_suscripciones_ind > 0:
            self.mostrar_estadisticas_estados_individuales()
        
        # Estadísticas por estado - Empresariales
        if total_suscripciones_emp > 0:
            self.mostrar_estadisticas_estados_empresariales()

    def mostrar_estadisticas_estados_individuales(self):
        """Muestra estadísticas de estados para suscripciones individuales"""
        self.stdout.write(f"\n📈 Estados suscripciones individuales:")
        
        estados = SuscripcionUsuario.objects.values('estado').annotate(
            count=models.Count('estado')
        ).order_by('-count')
        
        for estado_info in estados:
            self.stdout.write(f"   - {estado_info['estado'].title()}: {estado_info['count']}")
        
        # Promedio de servicios utilizados
        promedio_servicios = SuscripcionUsuario.objects.aggregate(
            promedio=models.Avg('servicios_utilizados_mes')
        )['promedio']
        
        if promedio_servicios:
            self.stdout.write(f"   - Promedio servicios utilizados/mes: {promedio_servicios:.1f}")

    def mostrar_estadisticas_estados_empresariales(self):
        """Muestra estadísticas de estados para suscripciones empresariales"""
        self.stdout.write(f"\n📈 Estados suscripciones empresariales:")
        
        estados = SuscripcionEmpresarial.objects.values('estado').annotate(
            count=models.Count('estado')
        ).order_by('-count')
        
        for estado_info in estados:
            self.stdout.write(f"   - {estado_info['estado'].title()}: {estado_info['count']}")
        
        # Promedio de vehículos y servicios
        estadisticas = SuscripcionEmpresarial.objects.aggregate(
            promedio_vehiculos=models.Avg('cantidad_vehiculos'),
            promedio_servicios=models.Avg('servicios_utilizados_mes'),
            promedio_precio=models.Avg('precio_mensual_actual')
        )
        
        if estadisticas['promedio_vehiculos']:
            self.stdout.write(f"   - Promedio vehículos por suscripción: {estadisticas['promedio_vehiculos']:.1f}")
        if estadisticas['promedio_servicios']:
            self.stdout.write(f"   - Promedio servicios utilizados/mes: {estadisticas['promedio_servicios']:.1f}")
        if estadisticas['promedio_precio']:
            self.stdout.write(f"   - Precio mensual promedio: ${estadisticas['promedio_precio']:,.0f}".replace(",", "."))
