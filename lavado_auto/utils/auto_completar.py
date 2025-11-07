from django.utils import timezone
from datetime import datetime, timedelta
from .models import Reserva
import logging

logger = logging.getLogger(__name__)

def auto_completar_reservas_vencidas(horas_limite=4):
    """
    Marca automáticamente como completadas las reservas pendientes
    que han pasado el tiempo límite especificado.
    
    Args:
        horas_limite (int): Número de horas después de las cuales marcar como completada
        
    Returns:
        dict: Diccionario con estadísticas de la operación
    """
    ahora = timezone.now()
    tiempo_limite = ahora - timedelta(hours=horas_limite)
    
    # Buscar reservas pendientes que ya pasaron el tiempo límite
    # Nota: soportar el estado legacy 'no_completado' que existía en migraciones antiguas
    reservas_pendientes = Reserva.objects.filter(estado__in=['pendiente', 'no_completado'])
    
    reservas_para_completar = []
    
    for reserva in reservas_pendientes:
        # Combinar fecha y hora de la reserva y asegurarnos de que el datetime
        # resultante sea timezone-aware antes de compararlo con "tiempo_limite".
        try:
            dt = datetime.combine(reserva.fecha, reserva.hora)

            # Si el datetime es naive, convertirlo a aware usando la zona horaria
            # actual configurada en Django. Si ya es aware, lo dejamos tal cual.
            if timezone.is_naive(dt):
                fecha_hora_reserva = timezone.make_aware(dt, timezone.get_current_timezone())
            else:
                fecha_hora_reserva = dt

            # Verificar si han pasado las horas especificadas
            if fecha_hora_reserva <= tiempo_limite:
                reservas_para_completar.append(reserva)

        except Exception as e:
            logger.error(f"Error al procesar reserva #{getattr(reserva, 'id_reserva', 'unknown')}: {e}")
            continue
    
    # Marcar las reservas como completadas
    reservas_actualizadas = 0
    errores = 0
    
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
            errores += 1
            logger.error(f"Error al marcar reserva #{reserva.id_reserva} como completada: {e}")
    
    resultado = {
        'total_encontradas': len(reservas_para_completar),
        'actualizadas': reservas_actualizadas,
        'errores': errores,
        'tiempo_ejecucion': ahora,
        'tiempo_limite_usado': tiempo_limite
    }
    
    return resultado


def verificar_y_completar_reservas_automaticamente():
    """
    Función simplificada para llamar desde las vistas.
    Marca como completadas las reservas que han pasado 4 horas.
    """
    try:
        resultado = auto_completar_reservas_vencidas(4)
        
        if resultado['actualizadas'] > 0:
            logger.info(
                f"Auto-completado: {resultado['actualizadas']} reservas marcadas como completadas automáticamente."
            )
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error en auto-completado de reservas: {e}")
        return {
            'total_encontradas': 0,
            'actualizadas': 0,
            'errores': 1,
            'error_mensaje': str(e)
        }
