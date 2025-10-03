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
