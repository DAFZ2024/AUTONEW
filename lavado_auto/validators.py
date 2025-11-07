"""
Validadores personalizados de contraseñas en español para Django
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re


class MinimumLengthValidatorES:
    """
    Valida que la contraseña tenga al menos min_length caracteres.
    """
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                f"La contraseña debe contener al menos {self.min_length} caracteres.",
                code='password_too_short',
            )

    def get_help_text(self):
        return f"Tu contraseña debe contener al menos {self.min_length} caracteres."


class NumericPasswordValidatorES:
    """
    Valida que la contraseña no sea completamente numérica.
    """
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                "La contraseña no puede ser completamente numérica.",
                code='password_entirely_numeric',
            )

    def get_help_text(self):
        return "Tu contraseña no puede ser completamente numérica."


class CommonPasswordValidatorES:
    """
    Valida que la contraseña no sea una contraseña común.
    """
    def validate(self, password, user=None):
        # Lista de contraseñas comunes en español
        common_passwords = [
            '12345678', 'password', 'contraseña', '123456789', 'qwerty',
            'abc123', 'password123', 'admin', 'letmein', 'welcome',
            '123123', 'password1', '1234567890', 'iloveyou', 'monkey',
            'dragon', 'master', 'sunshine', 'princess', 'football',
            'starwars', 'superman', 'batman', 'baseball', 'trustno1'
        ]
        
        if password.lower() in common_passwords:
            raise ValidationError(
                "Esta contraseña es demasiado común. Por favor elige una contraseña más segura.",
                code='password_too_common',
            )

    def get_help_text(self):
        return "Tu contraseña no puede ser una contraseña muy común."


class UppercaseValidatorES:
    """
    Valida que la contraseña contenga al menos una letra mayúscula.
    """
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                "La contraseña debe contener al menos una letra mayúscula.",
                code='password_no_upper',
            )

    def get_help_text(self):
        return "Tu contraseña debe contener al menos una letra mayúscula."


class LowercaseValidatorES:
    """
    Valida que la contraseña contenga al menos una letra minúscula.
    """
    def validate(self, password, user=None):
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                "La contraseña debe contener al menos una letra minúscula.",
                code='password_no_lower',
            )

    def get_help_text(self):
        return "Tu contraseña debe contener al menos una letra minúscula."


class NumberValidatorES:
    """
    Valida que la contraseña contenga al menos un número.
    """
    def validate(self, password, user=None):
        if not re.search(r'\d', password):
            raise ValidationError(
                "La contraseña debe contener al menos un número.",
                code='password_no_number',
            )

    def get_help_text(self):
        return "Tu contraseña debe contener al menos un número."


class SpecialCharacterValidatorES:
    """
    Valida que la contraseña contenga al menos un carácter especial.
    """
    def validate(self, password, user=None):
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                "La contraseña debe contener al menos un carácter especial (!@#$%^&*...).",
                code='password_no_symbol',
            )

    def get_help_text(self):
        return "Tu contraseña debe contener al menos un carácter especial (!@#$%^&*...)."


class UserAttributeSimilarityValidatorES:
    """
    Valida que la contraseña no sea similar a la información del usuario.
    """
    def __init__(self, user_attributes=['username', 'first_name', 'last_name', 'email'], max_similarity=0.7):
        self.user_attributes = user_attributes
        self.max_similarity = max_similarity

    def validate(self, password, user=None):
        if not user:
            return

        password_lower = password.lower()
        
        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value:
                continue
            
            value_lower = value.lower()
            
            # Verificación simple: si la contraseña contiene el atributo o viceversa
            if value_lower in password_lower or password_lower in value_lower:
                raise ValidationError(
                    "La contraseña es muy similar a tu información personal.",
                    code='password_too_similar',
                )

    def get_help_text(self):
        return "Tu contraseña no puede ser muy similar a tu información personal."


def calcular_fortaleza_contrasena(password):
    """
    Calcula la fortaleza de una contraseña y retorna un diccionario con:
    - score: puntuación de 0 a 5
    - nivel: 'muy-debil', 'debil', 'media', 'fuerte', 'muy-fuerte'
    - requisitos: diccionario con cada requisito cumplido
    - mensaje: mensaje descriptivo
    """
    if not password:
        return {
            'score': 0,
            'nivel': 'muy-debil',
            'porcentaje': 0,
            'requisitos': {},
            'mensaje': 'Ingresa una contraseña'
        }
    
    score = 0
    requisitos = {
        'longitud_minima': len(password) >= 8,
        'longitud_recomendada': len(password) >= 12,
        'tiene_minuscula': bool(re.search(r'[a-z]', password)),
        'tiene_mayuscula': bool(re.search(r'[A-Z]', password)),
        'tiene_numero': bool(re.search(r'\d', password)),
        'tiene_especial': bool(re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', password)),
        'no_solo_numeros': not password.isdigit(),
        'no_comun': password.lower() not in [
            '12345678', 'password', 'contraseña', '123456789', 'qwerty',
            'abc123', 'password123', 'admin', 'letmein', 'welcome',
            '123123', 'password1', '1234567890'
        ]
    }
    
    # Calcular puntuación
    if requisitos['longitud_minima']:
        score += 1
    if requisitos['longitud_recomendada']:
        score += 1
    if requisitos['tiene_minuscula']:
        score += 0.5
    if requisitos['tiene_mayuscula']:
        score += 0.5
    if requisitos['tiene_numero']:
        score += 0.5
    if requisitos['tiene_especial']:
        score += 1
    if requisitos['no_solo_numeros']:
        score += 0.5
    if requisitos['no_comun']:
        score += 0.5
    
    # Bonificación por longitud extra
    if len(password) >= 16:
        score += 0.5
    
    # Determinar nivel
    if score < 2:
        nivel = 'muy-debil'
        mensaje = 'Contraseña muy débil'
        color = '#ef4444'  # rojo
    elif score < 3:
        nivel = 'debil'
        mensaje = 'Contraseña débil'
        color = '#f97316'  # naranja
    elif score < 4:
        nivel = 'media'
        mensaje = 'Contraseña media'
        color = '#eab308'  # amarillo
    elif score < 4.5:
        nivel = 'fuerte'
        mensaje = 'Contraseña fuerte'
        color = '#84cc16'  # verde-amarillo
    else:
        nivel = 'muy-fuerte'
        mensaje = 'Contraseña muy fuerte'
        color = '#22c55e'  # verde
    
    porcentaje = min(100, int((score / 5) * 100))
    
    return {
        'score': score,
        'nivel': nivel,
        'porcentaje': porcentaje,
        'requisitos': requisitos,
        'mensaje': mensaje,
        'color': color
    }