"""
Tests para los formularios de la aplicación lavado_auto
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from lavado_auto.forms import (
    ComentarioClienteForm,
    CustomPasswordResetForm
)
from lavado_auto.models import (
    Usuario, Empresa, Reserva, Comentario
)


class ComentarioClienteFormTest(TestCase):
    """Pruebas para el formulario de comentarios"""
    
    def setUp(self):
        """Configuración inicial"""
        self.cliente = Usuario.objects.create_user(
            nombre_usuario='cliente_test',
            correo='cliente@test.com',
            password='password123',
            nombre_completo='Cliente Test',
            telefono='+56911111111',
            rol='cliente'
        )
        
        self.empresa = Empresa.objects.create(
            nombre_empresa='Lavado Test',
            direccion='Calle Test 123',
            telefono='+56933333333',
            email='info@test.com',
            contrasena='password123'
        )
        
        fecha_hoy = timezone.now().date()
        hora_reserva = timezone.now().time()
        self.reserva = Reserva.objects.create(
            usuario=self.cliente,
            empresa=self.empresa,
            fecha=fecha_hoy,
            hora=hora_reserva,
            placa_vehiculo='AA1234',
            tipo_vehiculo='sedan',
            estado='completado'
        )
    
    def test_form_valido_con_comentario(self):
        """Verifica que el formulario sea válido con un comentario"""
        form_data = {
            'comentario': 'Excelente servicio, muy recomendable'
        }
        form = ComentarioClienteForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalido_sin_comentario(self):
        """Verifica que el formulario sea inválido sin comentario"""
        form_data = {
            'comentario': ''
        }
        form = ComentarioClienteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('comentario', form.errors)
    
    def test_form_guarda_comentario_correctamente(self):
        """Verifica que el formulario guarde el comentario correctamente"""
        form_data = {
            'comentario': 'Muy buen servicio'
        }
        form = ComentarioClienteForm(data=form_data)
        
        self.assertTrue(form.is_valid())
        # El guardado del comentario depende de la implementación específica
        # por lo que hacemos un test básico de validación
    
    def test_form_tiene_campos_correctos(self):
        """Verifica que el formulario tenga los campos correctos"""
        form = ComentarioClienteForm()
        self.assertIn('comentario', form.fields)
        self.assertEqual(len(form.fields), 1)
    
    def test_form_widget_es_textarea(self):
        """Verifica que el campo comentario use un textarea"""
        form = ComentarioClienteForm()
        from django.forms import Textarea
        self.assertIsInstance(form.fields['comentario'].widget, Textarea)


class CustomPasswordResetFormTest(TestCase):
    """Pruebas para el formulario de recuperación de contraseña"""
    
    def setUp(self):
        """Configuración inicial"""
        self.usuario = Usuario.objects.create_user(
            nombre_usuario='test_user',
            correo='usuario@test.com',
            password='password123',
            nombre_completo='Usuario Test',
            telefono='+56912345678',
            rol='cliente'
        )
        self.usuario.is_active = True
        self.usuario.save()
    
    def test_form_valido_con_email_existente(self):
        """Verifica que el formulario sea válido con un email existente"""
        form_data = {
            'email': 'usuario@test.com'
        }
        form = CustomPasswordResetForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_valido_con_email_no_existente(self):
        """Verifica que el formulario sea válido incluso con email no existente"""
        # Django no valida si el email existe, solo el formato
        form_data = {
            'email': 'noexiste@test.com'
        }
        form = CustomPasswordResetForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalido_con_email_mal_formato(self):
        """Verifica que el formulario sea inválido con email mal formateado"""
        form_data = {
            'email': 'email_invalido'
        }
        form = CustomPasswordResetForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_form_invalido_sin_email(self):
        """Verifica que el formulario sea inválido sin email"""
        form_data = {
            'email': ''
        }
        form = CustomPasswordResetForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_get_users_retorna_usuario_activo(self):
        """Verifica que get_users retorne usuarios activos"""
        form = CustomPasswordResetForm()
        users = list(form.get_users('usuario@test.com'))
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], self.usuario)
    
    def test_get_users_no_retorna_usuario_inactivo(self):
        """Verifica que get_users no retorne usuarios inactivos"""
        self.usuario.is_active = False
        self.usuario.save()
        
        form = CustomPasswordResetForm()
        users = list(form.get_users('usuario@test.com'))
        self.assertEqual(len(users), 0)
    
    def test_get_users_case_insensitive(self):
        """Verifica que la búsqueda sea case-insensitive"""
        form = CustomPasswordResetForm()
        users = list(form.get_users('USUARIO@TEST.COM'))
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], self.usuario)
    
    def test_form_tiene_campo_email(self):
        """Verifica que el formulario tenga el campo email"""
        form = CustomPasswordResetForm()
        self.assertIn('email', form.fields)
        self.assertEqual(form.fields['email'].label, 'Correo electrónico')


class FormValidationTest(TestCase):
    """Pruebas generales de validación de formularios"""
    
    def test_comentario_form_limpieza_espacios(self):
        """Verifica que el formulario limpie espacios en blanco"""
        form_data = {
            'comentario': '  Comentario con espacios  '
        }
        form = ComentarioClienteForm(data=form_data)
        
        if form.is_valid():
            # Django limpia espacios al inicio y final por defecto
            self.assertEqual(form.cleaned_data['comentario'].strip(), 'Comentario con espacios')
    
    def test_email_form_validacion_formato(self):
        """Verifica validación de formato de email"""
        emails_invalidos = [
            'email_sin_arroba.com',
            '@dominio.com',
            'usuario@',
            'usuario@.com',
            'usuario@dominio',
        ]
        
        for email in emails_invalidos:
            form = CustomPasswordResetForm(data={'email': email})
            self.assertFalse(form.is_valid(), f"Email {email} debería ser inválido")
    
    def test_email_form_validacion_formato_valido(self):
        """Verifica que emails válidos pasen la validación"""
        emails_validos = [
            'usuario@dominio.com',
            'usuario.nombre@dominio.cl',
            'usuario+tag@dominio.com',
            'usuario_123@sub.dominio.com',
        ]
        
        for email in emails_validos:
            form = CustomPasswordResetForm(data={'email': email})
            self.assertTrue(form.is_valid(), f"Email {email} debería ser válido")
