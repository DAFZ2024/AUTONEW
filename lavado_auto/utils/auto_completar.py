from django.utils import timezone
from datetime import timedelta
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
    reservas_pendientes = Reserva.objects.filter(estado='pendiente')
    
    reservas_para_completar = []
    
    for reserva in reservas_pendientes:
        # Combinar fecha y hora de la reserva
        try:
            fecha_hora_reserva = timezone.make_aware(
                timezone.datetime.combine(reserva.fecha, reserva.hora)
            )
            
            # Verificar si han pasado las horas especificadas
            if fecha_hora_reserva <= tiempo_limite:
                reservas_para_completar.append(reserva)
        except Exception as e:
            logger.error(f"Error al procesar reserva #{reserva.id_reserva}: {e}")
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
