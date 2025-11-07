from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from lavado_auto.models import Reserva
import logging

# Configurar logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Marca automáticamente como completadas las reservas que han pasado 4 horas desde su hora programada'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra las reservas que se marcarían como completadas sin realizar cambios',
        )
        parser.add_argument(
            '--horas',
            type=int,
            default=4,
            help='Número de horas después de las cuales marcar como completada (default: 4)',
        )
        parser.add_argument(
            '--yes',
            action='store_true',
            help='No pedir confirmación interactiva y aplicar cambios directamente',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        horas_limite = options['horas']
        
        # Calcular el tiempo límite (ahora - X horas)
        ahora = timezone.now()
        tiempo_limite = ahora - timedelta(hours=horas_limite)
        
        self.stdout.write(f"🕐 Hora actual: {ahora.strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write(f"⏰ Buscando reservas anteriores a: {tiempo_limite.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Buscar reservas pendientes (incluye estado legacy 'no_completado') que ya pasaron el tiempo límite
        reservas_pendientes = Reserva.objects.filter(
            estado__in=['pendiente', 'no_completado']
        )
        
        reservas_para_completar = []
        
        for reserva in reservas_pendientes:
            # Combinar fecha y hora de la reserva
            fecha_hora_reserva = timezone.make_aware(
                timezone.datetime.combine(reserva.fecha, reserva.hora)
            )
            
            # Verificar si han pasado las horas especificadas
            if fecha_hora_reserva <= tiempo_limite:
                reservas_para_completar.append(reserva)
        
        if not reservas_para_completar:
            self.stdout.write(
                self.style.SUCCESS('✅ No hay reservas pendientes que necesiten ser marcadas como completadas.')
            )
            return
        
        self.stdout.write(f"📋 Encontradas {len(reservas_para_completar)} reservas para marcar como completadas:")
        
        for reserva in reservas_para_completar:
            fecha_hora_reserva = timezone.make_aware(
                timezone.datetime.combine(reserva.fecha, reserva.hora)
            )
            tiempo_transcurrido = ahora - fecha_hora_reserva
            horas_transcurridas = tiempo_transcurrido.total_seconds() / 3600
            
            self.stdout.write(
                f"  • Reserva #{reserva.id_reserva} - {reserva.usuario.nombre_usuario} - "
                f"{reserva.empresa.nombre_empresa} - {fecha_hora_reserva.strftime('%Y-%m-%d %H:%M')} "
                f"({horas_transcurridas:.1f} horas transcurridas)"
            )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🧪 MODO DRY-RUN: No se realizaron cambios. Use sin --dry-run para aplicar los cambios.')
            )
            return
        
        # Confirmar antes de hacer cambios (a menos que --yes esté presente)
        if not options.get('yes'):
            confirm = input("¿Desea marcar estas reservas como completadas? (s/N): ")
            if confirm.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
                self.stdout.write(self.style.WARNING('❌ Operación cancelada por el usuario.'))
                return
        
        # Marcar las reservas como completadas
        reservas_actualizadas = 0
        for reserva in reservas_para_completar:
            try:
                reserva.estado = 'completado'
                reserva.save()
                reservas_actualizadas += 1
                
                # Log para auditoría
                logger.info(
                    f"Reserva #{reserva.id_reserva} marcada automáticamente como completada. "
                    f"Usuario: {reserva.usuario.nombre_usuario}, "
                    f"Empresa: {reserva.empresa.nombre_empresa}, "
                    f"Fecha original: {reserva.fecha} {reserva.hora}"
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error al actualizar reserva #{reserva.id_reserva}: {e}")
                )
                logger.error(f"Error al marcar reserva #{reserva.id_reserva} como completada: {e}")
        
        if reservas_actualizadas > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ {reservas_actualizadas} reservas marcadas como completadas exitosamente."
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR("❌ No se pudo actualizar ninguna reserva.")
            )
