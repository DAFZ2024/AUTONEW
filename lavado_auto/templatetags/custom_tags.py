from django import template
from datetime import datetime
import locale

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def filtrar_por_estado(queryset, estado):
    """Filtrar quejas por estado específico"""
    try:
        return [queja for queja in queryset if queja.estado == estado]
    except:
        return []

@register.filter
def add_class(field, css_class):
    """Agregar clases CSS a campos de formulario"""
    try:
        # Si el campo ya tiene clases, las combina
        existing_classes = field.field.widget.attrs.get('class', '')
        if existing_classes:
            css_class = f"{existing_classes} {css_class}"
        
        # Crea una copia del campo con las nuevas clases
        field.field.widget.attrs['class'] = css_class
        return field
    except:
        return field

@register.filter
def fecha_espanol(fecha):
    """Convertir fecha al formato en español"""
    if not fecha:
        return ""
    
    # Diccionario de traducción de días
    dias_semana = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes', 
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    
    # Diccionario de traducción de meses
    meses = {
        'January': 'Enero',
        'February': 'Febrero',
        'March': 'Marzo',
        'April': 'Abril', 
        'May': 'Mayo',
        'June': 'Junio',
        'July': 'Julio',
        'August': 'Agosto',
        'September': 'Septiembre',
        'October': 'Octubre',
        'November': 'Noviembre',
        'December': 'Diciembre'
    }
    
    try:
        # Convertir fecha si es string
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        # Obtener día de la semana, día del mes y mes en inglés
        dia_semana_en = fecha.strftime('%A')
        dia_numero = fecha.day
        mes_en = fecha.strftime('%B')
        año = fecha.year
        
        # Traducir al español
        dia_semana_es = dias_semana.get(dia_semana_en, dia_semana_en)
        mes_es = meses.get(mes_en, mes_en)
        
        # Formatear: "Lunes, 15 de Julio de 2024"
        return f"{dia_semana_es}, {dia_numero} de {mes_es} de {año}"
        
    except Exception as e:
        return str(fecha)

@register.filter 
def fecha_corta_espanol(fecha):
    """Convertir fecha al formato corto en español: DD/MM/YYYY"""
    if not fecha:
        return ""
    
    try:
        # Convertir fecha si es string
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        return fecha.strftime('%d/%m/%Y')
        
    except Exception as e:
        return str(fecha)

@register.filter
def hora_12h(hora):
    """Convertir hora al formato de 12 horas con AM/PM"""
    if not hora:
        return ""
    
    try:
        # Si es un string, convertir a objeto time
        if isinstance(hora, str):
            hora_obj = datetime.strptime(hora, '%H:%M').time()
        else:
            # Si es un objeto time o datetime
            if hasattr(hora, 'time'):
                hora_obj = hora.time()
            else:
                hora_obj = hora
        
        # Formatear a 12 horas con AM/PM
        return hora_obj.strftime('%I:%M %p')
    except Exception as e:
        return str(hora)

@register.filter
def hora_24h(hora_12h):
    """Convertir hora de formato 12h con AM/PM a formato 24h"""
    if not hora_12h:
        return ""
    
    try:
        hora_obj = datetime.strptime(hora_12h, '%I:%M %p').time()
        return hora_obj.strftime('%H:%M')
    except Exception as e:
        return str(hora_12h)

@register.filter
def filter_by_estado(queryset, estado):
    """Filtrar y contar reservas por estado específico"""
    try:
        if hasattr(queryset, 'filter'):
            # Si es un QuerySet
            return queryset.filter(estado=estado).count()
        else:
            # Si es una lista
            return len([reserva for reserva in queryset if reserva.estado == estado])
    except Exception as e:
        return 0

@register.filter
def calcular_precio_total(servicios):
    """Calcular el precio total de una lista de servicios"""
    try:
        total = 0
        if hasattr(servicios, 'all'):
            # Si es un QuerySet relacionado
            for servicio in servicios.all():
                total += float(servicio.precio)
        elif hasattr(servicios, '__iter__'):
            # Si es una lista o queryset
            for servicio in servicios:
                if hasattr(servicio, 'precio'):
                    total += float(servicio.precio)
        return "{:.2f}".format(total)
    except Exception as e:
        return "0.00"

@register.filter
def precio_formateado(precio):
    """Formatear precio con dos decimales"""
    try:
        return "{:.2f}".format(float(precio))
    except Exception as e:
        return "0.00"

@register.filter
def es_nueva_24h(fecha):
    """Verificar si una fecha está dentro de las últimas 24 horas"""
    try:
        from django.utils import timezone
        from datetime import timedelta
        
        if not fecha:
            return False
            
        ahora = timezone.now()
        hace_24_horas = ahora - timedelta(hours=24)
        
        return fecha >= hace_24_horas
    except Exception:
        return False