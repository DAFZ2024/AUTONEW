from django.core.management.base import BaseCommand
from django.utils import timezone
from lavado_auto.models import SuscripcionUsuario, Usuario, Plan

class Command(BaseCommand):
    help = 'Verifica el estado de las suscripciones y muestra información detallada'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            help='Nombre de usuario específico para verificar',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 Verificando estado de suscripciones...\n')
        )
        
        usuario_especifico = options.get('usuario')
        
        if usuario_especifico:
            try:
                usuario = Usuario.objects.get(nombre_usuario=usuario_especifico)
                suscripciones = SuscripcionUsuario.objects.filter(usuario=usuario)
            except Usuario.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Usuario "{usuario_especifico}" no encontrado')
                )
                return
        else:
            suscripciones = SuscripcionUsuario.objects.all()

        if not suscripciones.exists():
            self.stdout.write(
                self.style.WARNING('⚠️ No se encontraron suscripciones')
            )
            return

        for suscripcion in suscripciones:
            self.stdout.write('=' * 80)
            self.stdout.write(f'👤 Usuario: {suscripcion.usuario.nombre_usuario}')
            self.stdout.write(f'📋 Plan: {suscripcion.plan.nombre}')
            self.stdout.write(f'💰 Precio mensual: ${suscripcion.plan.precio_mensual}')
            self.stdout.write(f'📊 Estado: {suscripcion.get_estado_display()}')
            
            # Información de fechas
            self.stdout.write(f'📅 Fecha inicio: {suscripcion.fecha_inicio.strftime("%d/%m/%Y %H:%M")}')
            self.stdout.write(f'⏰ Fecha fin: {suscripcion.fecha_fin.strftime("%d/%m/%Y %H:%M")}')
            self.stdout.write(f'🔄 Último reinicio contador: {suscripcion.ultimo_reinicio_contador.strftime("%d/%m/%Y %H:%M")}')
            
            # Estado de la suscripción
            esta_activa = suscripcion.esta_activa()
            puede_usar = suscripcion.puede_usar_servicio()
            
            self.stdout.write(f'✅ ¿Está activa?: {esta_activa}')
            self.stdout.write(f'🎯 ¿Puede usar servicio?: {puede_usar}')
            
            # Información de servicios
            if suscripcion.plan.cantidad_servicios_mes == 0:
                self.stdout.write(f'🔄 Servicios permitidos: Ilimitado')
            else:
                self.stdout.write(f'🔄 Servicios permitidos por mes: {suscripcion.plan.cantidad_servicios_mes}')
            
            self.stdout.write(f'📊 Servicios utilizados este mes: {suscripcion.servicios_utilizados_mes}')
            
            servicios_restantes = suscripcion.servicios_restantes()
            self.stdout.write(f'📈 Servicios restantes: {servicios_restantes}')
            
            # Servicios incluidos en el plan
            servicios_incluidos = suscripcion.plan.servicios_incluidos.all()
            if servicios_incluidos.exists():
                self.stdout.write('🛠️ Servicios incluidos en el plan:')
                for servicio in servicios_incluidos:
                    self.stdout.write(f'   • {servicio.nombre_servicio} - ${servicio.precio}')
            else:
                self.stdout.write('🛠️ No hay servicios específicos configurados para este plan')
            
            # Características del plan
            caracteristicas = []
            if suscripcion.plan.incluye_lavado_asientos:
                caracteristicas.append('Lavado de asientos')
            if suscripcion.plan.incluye_aspirado:
                caracteristicas.append('Aspirado completo')
            if suscripcion.plan.incluye_lavado_exterior:
                caracteristicas.append('Lavado exterior')
            if suscripcion.plan.incluye_lavado_interior_humedo:
                caracteristicas.append('Interior húmedo')
            if suscripcion.plan.incluye_encerado:
                caracteristicas.append('Encerado')
            if suscripcion.plan.incluye_detallado_completo:
                caracteristicas.append('Detallado completo')
            
            if caracteristicas:
                self.stdout.write('🌟 Características incluidas:')
                for caracteristica in caracteristicas:
                    self.stdout.write(f'   ✓ {caracteristica}')
            
            # Verificar si necesita reinicio de contador
            hoy = timezone.now()
            dias_desde_reinicio = (hoy - suscripcion.ultimo_reinicio_contador).days
            
            if dias_desde_reinicio >= 30:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ ATENCIÓN: El contador debería reiniciarse (han pasado {dias_desde_reinicio} días)')
                )
            else:
                self.stdout.write(f'✅ Contador actualizado (hace {dias_desde_reinicio} días)')
            
            self.stdout.write('')

        self.stdout.write(
            self.style.SUCCESS('\n✅ Verificación completada')
        )