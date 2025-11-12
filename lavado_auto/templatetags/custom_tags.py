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
def calcular_precio_reserva(reserva):
    """Calcular el precio total de una reserva considerando el precio_aplicado en ReservaServicio"""
    try:
        from lavado_auto.models import ReservaServicio
        total = 0
        
        # Obtener todas las relaciones ReservaServicio para esta reserva
        reserva_servicios = ReservaServicio.objects.filter(reserva=reserva)
        
        for rs in reserva_servicios:
            # Si tiene precio_aplicado, usar ese, si no usar el precio del servicio
            if rs.precio_aplicado is not None:
                total += float(rs.precio_aplicado)
            else:
                total += float(rs.servicio.precio)
        
        return "{:.2f}".format(total)
    except Exception as e:
        return "0.00"

@register.filter
def calcular_precio_servicios_adicionales(reserva):
    """Calcular solo el precio de los servicios adicionales (NO incluye servicios del plan)"""
    try:
        from lavado_auto.models import ReservaServicio
        total = 0
        
        # Obtener todas las relaciones ReservaServicio para esta reserva
        reserva_servicios = ReservaServicio.objects.filter(reserva=reserva)
        
        for rs in reserva_servicios:
            # Solo sumar si NO es servicio del plan
            if not rs.es_servicio_plan:
                if rs.precio_aplicado is not None:
                    total += float(rs.precio_aplicado)
                else:
                    total += float(rs.servicio.precio)
        
        return "{:.2f}".format(total)
    except Exception as e:
        return "0.00"

@register.filter
def obtener_servicios_con_precio(reserva):
    """Obtener lista de servicios de una reserva con su precio aplicado y descuentos"""
    try:
        from lavado_auto.models import ReservaServicio
        servicios_info = []
        
        # Obtener todas las relaciones ReservaServicio para esta reserva
        reserva_servicios = ReservaServicio.objects.filter(reserva=reserva).select_related('servicio')
        
        for rs in reserva_servicios:
            precio = rs.precio_aplicado if rs.precio_aplicado is not None else rs.servicio.precio
            precio_original = rs.precio_original if rs.precio_original is not None else rs.servicio.precio
            
            servicios_info.append({
                'servicio': rs.servicio,
                'precio_aplicado': float(precio),
                'precio_original': float(precio_original),
                'es_gratis': float(precio) == 0,
                'es_servicio_plan': rs.es_servicio_plan,
                'descuento_plan': float(rs.descuento_plan_individual) if rs.descuento_plan_individual else 0,
                'descuento_empresarial': float(rs.descuento_empresarial) if rs.descuento_empresarial else 0,
                'ahorro': rs.obtener_ahorro(),
            })
        
        return servicios_info
    except Exception as e:
        print(f"Error en obtener_servicios_con_precio: {e}")
        return []

@register.filter
def todos_servicios_son_plan(reserva):
    """Verificar si todos los servicios de la reserva son del plan (gratis)"""
    try:
        from lavado_auto.models import ReservaServicio
        reserva_servicios = ReservaServicio.objects.filter(reserva=reserva)
        
        if not reserva_servicios.exists():
            return False
        
        # Verificar si todos tienen precio_aplicado = 0 o son servicios del plan
        todos_gratis = all(
            (rs.precio_aplicado is not None and float(rs.precio_aplicado) == 0) or rs.es_servicio_plan
            for rs in reserva_servicios
        )
        
        return todos_gratis
    except Exception as e:
        return False

@register.filter
def tiene_servicios_adicionales(reserva):
    """Verificar si la reserva tiene servicios adicionales (no del plan)"""
    try:
        from lavado_auto.models import ReservaServicio
        reserva_servicios = ReservaServicio.objects.filter(reserva=reserva)
        
        # Verificar si hay al menos un servicio que no sea del plan
        tiene_adicionales = any(
            not rs.es_servicio_plan or (rs.precio_aplicado is not None and float(rs.precio_aplicado) > 0)
            for rs in reserva_servicios
        )
        
        return tiene_adicionales
    except Exception as e:
        return False

@register.filter
def precio_formateado(precio):
    """Formatear precio con dos decimales"""
    try:
        return "{:.2f}".format(float(precio))
    except Exception as e:
        return "0.00"

@register.filter
def calcular_total_reserva_con_descuentos(reserva):
    """Calcular el total de la reserva INCLUYENDO servicios del plan con descuento aplicado"""
    try:
        from lavado_auto.models import ReservaServicio
        total = 0
        
        # Obtener todas las relaciones ReservaServicio para esta reserva
        reserva_servicios = ReservaServicio.objects.filter(reserva=reserva)
        
        for rs in reserva_servicios:
            # Sumar TODOS los servicios con su precio_aplicado
            if rs.precio_aplicado is not None:
                total += float(rs.precio_aplicado)
            else:
                total += float(rs.servicio.precio)
        
        return "{:.2f}".format(total)
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

@register.filter
def lookup(dictionary, key):
    """Buscar valor en diccionario por clave"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    elif isinstance(dictionary, list):
        # Para listas de tuplas como meses_disponibles
        for item in dictionary:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                if item[0] == key:
                    return item[1]
    return None

@register.filter
def sum_attribute(lista, atributo):
    """Sumar un atributo específico de una lista de objetos/diccionarios"""
    total = 0
    for item in lista:
        if isinstance(item, dict):
            value = item.get(atributo, 0)
        else:
            value = getattr(item, atributo, 0)
        
        if value:
            try:
                total += float(value)
            except (ValueError, TypeError):
                continue
    return total