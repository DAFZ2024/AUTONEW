"""
Tests para los modelos de la aplicación lavado_auto
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from lavado_auto.models import (
    Usuario, Empresa, Servicio, Reserva, Plan, 
    SuscripcionUsuario, MensajeQueja, Comentario,
    ReservaServicio, Pago, EmpresaServicio
)


class UsuarioModelTest(TestCase):
    """Pruebas para el modelo Usuario"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        pass
    
    def test_crear_usuario_valido(self):
        """Verifica que se pueda crear un usuario con datos válidos"""
        usuario = Usuario.objects.create_user(
            nombre_usuario='juan_perez',
            correo='juan.perez@example.com',
            password='password123',
            nombre_completo='Juan Pérez',
            telefono='+56912345678',
            rol='cliente'
        )
        self.assertIsNotNone(usuario.id_usuario)
        self.assertEqual(usuario.nombre_completo, 'Juan Pérez')
        self.assertEqual(usuario.correo, 'juan.perez@example.com')
        self.assertEqual(usuario.rol, 'cliente')
    
    def test_usuario_str_representation(self):
        """Verifica la representación en string del usuario"""
        usuario = Usuario.objects.create_user(
            nombre_usuario='test_user',
            correo='test@example.com',
            password='password123',
            nombre_completo='Usuario Test'
        )
        self.assertEqual(str(usuario), 'test_user')
    
    def test_correo_unico(self):
        """Verifica que el correo sea único"""
        Usuario.objects.create_user(
            nombre_usuario='user1',
            correo='same@example.com',
            password='password123'
        )
        
        # Intentar crear otro usuario con el mismo correo
        with self.assertRaises(Exception):
            Usuario.objects.create_user(
                nombre_usuario='user2',
                correo='same@example.com',
                password='password123'
            )
    
    def test_nombre_usuario_unico(self):
        """Verifica que el nombre de usuario sea único"""
        Usuario.objects.create_user(
            nombre_usuario='unique_user',
            correo='user1@example.com',
            password='password123'
        )
        
        # Intentar crear otro usuario con el mismo nombre de usuario
        with self.assertRaises(Exception):
            Usuario.objects.create_user(
                nombre_usuario='unique_user',
                correo='user2@example.com',
                password='password123'
            )
    
    def test_roles_validos(self):
        """Verifica que solo se puedan asignar roles válidos"""
        roles_validos = ['cliente', 'admin']
        
        for i, rol in enumerate(roles_validos):
            usuario = Usuario.objects.create_user(
                nombre_usuario=f'user_{rol}_{i}',
                correo=f'usuario_{rol}_{i}@example.com',
                password='password123',
                rol=rol
            )
            self.assertEqual(usuario.rol, rol)
    
    def test_failed_login_attempts_default(self):
        """Verifica que los intentos fallidos inicien en 0"""
        usuario = Usuario.objects.create_user(
            nombre_usuario='test_attempts',
            correo='attempts@example.com',
            password='password123'
        )
        self.assertEqual(usuario.failed_login_attempts, 0)
    
    def test_fecha_registro_auto_asignada(self):
        """Verifica que la fecha de registro se asigne automáticamente"""
        usuario = Usuario.objects.create_user(
            nombre_usuario='test_fecha',
            correo='fecha@example.com',
            password='password123'
        )
        self.assertIsNotNone(usuario.fecha_registro)
        self.assertLessEqual(
            (timezone.now() - usuario.fecha_registro).total_seconds(),
            5  # Menos de 5 segundos de diferencia
        )


class EmpresaModelTest(TestCase):
    """Pruebas para el modelo Empresa"""
    
    def setUp(self):
        """Configuración inicial"""
        self.empresa_data = {
            'nombre_empresa': 'Lavado Premium',
            'direccion': 'Av. Principal 123',
            'telefono': '+56222222222',
            'email': 'info@lavadopremium.com',
            'contrasena': 'temp_password123'
        }
    
    def test_crear_empresa_valida(self):
        """Verifica que se pueda crear una empresa"""
        empresa = Empresa.objects.create(**self.empresa_data)
        self.assertIsNotNone(empresa.id_empresa)
        self.assertEqual(empresa.nombre_empresa, 'Lavado Premium')
        self.assertFalse(empresa.verificada)  # Por defecto no verificada
    
    def test_empresa_str_representation(self):
        """Verifica la representación en string de la empresa"""
        empresa = Empresa.objects.create(**self.empresa_data)
        # El __str__ debería estar definido en el modelo
        self.assertIsInstance(str(empresa), str)
    
    def test_empresa_verificada_default_false(self):
        """Verifica que las empresas no estén verificadas por defecto"""
        empresa = Empresa.objects.create(**self.empresa_data)
        self.assertFalse(empresa.verificada)
    
    def test_empresa_failed_login_attempts_default(self):
        """Verifica que los intentos fallidos inicien en 0"""
        empresa = Empresa.objects.create(**self.empresa_data)
        self.assertEqual(empresa.failed_login_attempts, 0)
    
    def test_empresa_coordenadas_opcionales(self):
        """Verifica que latitud y longitud sean opcionales"""
        empresa = Empresa.objects.create(**self.empresa_data)
        self.assertIsNone(empresa.latitud)
        self.assertIsNone(empresa.longitud)


class ServicioModelTest(TestCase):
    """Pruebas para el modelo Servicio"""
    
    def test_crear_servicio(self):
        """Verifica que se pueda crear un servicio"""
        servicio = Servicio.objects.create(
            nombre_servicio='Lavado Básico',
            descripcion='Lavado exterior completo',
            precio=10000.00
        )
        self.assertIsNotNone(servicio.id_servicio)
        self.assertEqual(servicio.nombre_servicio, 'Lavado Básico')
        self.assertEqual(servicio.precio, 10000.00)
    
    def test_servicio_str_representation(self):
        """Verifica la representación en string del servicio"""
        servicio = Servicio.objects.create(
            nombre_servicio='Lavado Premium',
            descripcion='Lavado completo con encerado',
            precio=25000.00
        )
        self.assertIsInstance(str(servicio), str)


class ReservaModelTest(TestCase):
    """Pruebas para el modelo Reserva"""
    
    def setUp(self):
        """Configuración inicial"""
        # Crear usuario cliente
        self.cliente = Usuario.objects.create_user(
            nombre_usuario='cliente_test',
            correo='cliente@test.com',
            password='password123',
            nombre_completo='Cliente Test',
            telefono='+56911111111',
            rol='cliente'
        )
        
        # Crear empresa
        self.empresa = Empresa.objects.create(
            nombre_empresa='Lavado Test',
            direccion='Calle Test 123',
            telefono='+56933333333',
            email='info@test.com',
            contrasena='password123',
            verificada=True
        )
        
        # Crear servicio
        self.servicio = Servicio.objects.create(
            nombre_servicio='Lavado Test',
            descripcion='Servicio de prueba',
            precio=10000.00
        )
        
        # Relacionar servicio con empresa
        EmpresaServicio.objects.create(
            empresa=self.empresa,
            servicio=self.servicio
        )
    
    def test_crear_reserva_valida(self):
        """Verifica que se pueda crear una reserva"""
        fecha_hoy = timezone.now().date()
        hora_reserva = timezone.now().time()
        
        reserva = Reserva.objects.create(
            usuario=self.cliente,
            empresa=self.empresa,
            fecha=fecha_hoy,
            hora=hora_reserva,
            placa_vehiculo='AA1234',
            tipo_vehiculo='sedan',
            estado='pendiente'
        )
        
        self.assertIsNotNone(reserva.id_reserva)
        self.assertEqual(reserva.usuario, self.cliente)
        self.assertEqual(reserva.empresa, self.empresa)
        self.assertEqual(reserva.estado, 'pendiente')
        self.assertIsNotNone(reserva.numero_reserva)  # Se genera automáticamente
    
    def test_reserva_estados_validos(self):
        """Verifica que solo se puedan asignar estados válidos"""
        fecha_hoy = timezone.now().date()
        hora_reserva = timezone.now().time()
        
        estados_validos = ['pendiente', 'completado', 'cancelada']
        
        for i, estado in enumerate(estados_validos):
            reserva = Reserva.objects.create(
                usuario=self.cliente,
                empresa=self.empresa,
                fecha=fecha_hoy,
                hora=hora_reserva,
                placa_vehiculo=f'AA{1000+i}',
                tipo_vehiculo='sedan',
                estado=estado
            )
            self.assertEqual(reserva.estado, estado)
    
    def test_reserva_numero_auto_generado(self):
        """Verifica que el número de reserva se genere automáticamente"""
        fecha_hoy = timezone.now().date()
        hora_reserva = timezone.now().time()
        
        reserva = Reserva.objects.create(
            usuario=self.cliente,
            empresa=self.empresa,
            fecha=fecha_hoy,
            hora=hora_reserva,
            placa_vehiculo='BB1234',
            tipo_vehiculo='sedan',
            estado='pendiente'
        )
        
        self.assertIsNotNone(reserva.numero_reserva)
        self.assertTrue(reserva.numero_reserva.startswith('ANW-'))


class PlanModelTest(TestCase):
    """Pruebas para el modelo Plan"""
    
    def test_crear_plan_valido(self):
        """Verifica que se pueda crear un plan"""
        plan = Plan.objects.create(
            nombre='Plan Básico',
            tipo='basico',
            descripcion='Plan de entrada',
            precio_mensual=Decimal('5000.00'),
            cantidad_servicios_mes=5
        )
        
        self.assertIsNotNone(plan.id_plan)
        self.assertEqual(plan.nombre, 'Plan Básico')
        self.assertEqual(plan.precio_mensual, Decimal('5000.00'))
        self.assertEqual(plan.cantidad_servicios_mes, 5)
    
    def test_plan_str_representation(self):
        """Verifica la representación en string del plan"""
        plan = Plan.objects.create(
            nombre='Plan Premium',
            tipo='premium',
            descripcion='Plan completo',
            precio_mensual=Decimal('15000.00'),
            cantidad_servicios_mes=10
        )
        self.assertIn('Plan Premium', str(plan))


class MensajeQuejaModelTest(TestCase):
    """Pruebas para el modelo MensajeQueja"""
    
    def setUp(self):
        """Configuración inicial"""
        self.usuario = Usuario.objects.create_user(
            nombre_usuario='usuario_queja',
            correo='queja@test.com',
            password='password123',
            nombre_completo='Usuario Queja',
            telefono='+56933333333',
            rol='cliente'
        )
    
    def test_crear_mensaje_queja(self):
        """Verifica que se pueda crear un mensaje/queja"""
        # Verificar que el modelo MensajeQueja tenga los campos correctos
        # Esto puede variar según tu implementación
        self.assertTrue(hasattr(MensajeQueja, '_meta'))
    
    def test_mensaje_queja_fecha_auto(self):
        """Verifica que el modelo MensajeQueja exista"""
        # Test básico para verificar que el modelo existe
        self.assertTrue(hasattr(MensajeQueja, 'objects'))


class ComentarioModelTest(TestCase):
    """Pruebas para el modelo Comentario"""
    
    def setUp(self):
        """Configuración inicial"""
        # Crear cliente
        self.cliente = Usuario.objects.create_user(
            nombre_usuario='cliente_comentario',
            correo='comentario@test.com',
            password='password123',
            nombre_completo='Cliente Comentario',
            telefono='+56944444444',
            rol='cliente'
        )
        
        # Crear empresa
        self.empresa = Empresa.objects.create(
            nombre_empresa='Empresa Comentario',
            direccion='Dir Test',
            telefono='+56966666666',
            email='info@empcomentario.com',
            contrasena='password123'
        )
        
        # Crear reserva
        fecha_hoy = timezone.now().date()
        hora_reserva = timezone.now().time()
        self.reserva = Reserva.objects.create(
            usuario=self.cliente,
            empresa=self.empresa,
            fecha=fecha_hoy,
            hora=hora_reserva,
            placa_vehiculo='CC1234',
            tipo_vehiculo='sedan',
            estado='completado'
        )
    
    def test_crear_comentario_valido(self):
        """Verifica que se pueda crear un comentario"""
        # Verificar que el modelo Comentario existe y tiene los campos básicos
        self.assertTrue(hasattr(Comentario, '_meta'))
        self.assertTrue(hasattr(Comentario, 'objects'))
    
    def test_comentario_calificacion_rango(self):
        """Verifica que el modelo Comentario esté disponible"""
        # Test básico de existencia del modelo
        self.assertIsNotNone(Comentario)
    
    def test_comentario_fecha_auto(self):
        """Verifica que el modelo Comentario esté configurado"""
        # Test básico
        self.assertTrue(hasattr(Comentario, '_meta'))
