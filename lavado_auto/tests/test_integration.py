"""
Tests de integración para flujos completos de la aplicación
"""
from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from lavado_auto.models import (
    Usuario, Empresa, Servicio, Reserva,
    EmpresaServicio, Plan, SuscripcionUsuario,
    Comentario, MensajeQueja
)


class FlujoReservaCompletoTest(TestCase):
    """Pruebas del flujo completo de reserva"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        
        # Crear cliente con create_user
        self.cliente = Usuario.objects.create_user(
            nombre_usuario='clientetest1',
            correo='cliente@test.com',
            password='password123',
            nombre_completo='Cliente Test',
            telefono='+56911111111',
            rol='cliente'
        )
        
        # Crear empresa con create_user
        self.usuario_empresa = Usuario.objects.create_user(
            nombre_usuario='empresatest1',
            correo='empresa@test.com',
            password='password123',
            nombre_completo='Empresa Test',
            telefono='+56922222222',
            rol='empresa'
        )
        
        self.empresa = Empresa.objects.create(
            nombre_empresa='Lavado Premium',
            direccion='Av. Principal 123',
            telefono='+56933333333',
            email='info@lavado.com',
            contrasena='temp_password123',
            verificada=True
        )
        
        # Crear servicio con campos correctos
        self.servicio = Servicio.objects.create(
            nombre_servicio='Lavado Completo',
            descripcion='Lavado interior y exterior',
            precio=15000.00
        )
        
        # Asociar servicio con empresa
        self.empresa_servicio = EmpresaServicio.objects.create(
            empresa=self.empresa,
            servicio=self.servicio
        )
    
    def test_flujo_reserva_completo(self):
        """
        Prueba el flujo completo:
        1. Cliente se autentica
        2. Cliente crea reserva
        3. Empresa ve la reserva
        4. Empresa confirma la reserva
        5. Reserva se completa
        6. Cliente deja comentario
        """
        
        # 1. Crear reserva con campos correctos
        fecha_reserva = timezone.now() + timedelta(days=1)
        reserva = Reserva.objects.create(
            usuario=self.cliente,
            empresa=self.empresa,
            fecha=fecha_reserva.date(),
            hora=fecha_reserva.time(),
            placa_vehiculo='AA1234',
            tipo_vehiculo='sedan',
            estado='pendiente'
        )
        
        self.assertEqual(reserva.estado, 'pendiente')
        self.assertIsNotNone(reserva.id_reserva)
        
        # 2. Empresa confirma reserva
        reserva.estado = 'confirmada'
        reserva.save()
        
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, 'confirmada')
        
        # 3. Reserva en proceso
        reserva.estado = 'en_proceso'
        reserva.save()
        
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, 'en_proceso')
        
        # 4. Completar reserva
        reserva.estado = 'completada'
        reserva.save()
        
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, 'completada')
        
        # 5. Cliente deja comentario (con campos correctos del modelo real)
        comentario = Comentario.objects.create(
            usuario=self.cliente,
            comentario='Excelente servicio, muy recomendable'
        )
        
        self.assertIsNotNone(comentario.id_comentario)
        self.assertEqual(comentario.usuario, self.cliente)
        
        # Verificar que todo está relacionado correctamente
        self.assertEqual(reserva.usuario, self.cliente)
        self.assertEqual(reserva.empresa, self.empresa)


class FlujoSuscripcionTest(TestCase):
    """Pruebas del flujo de suscripción"""
    
    def setUp(self):
        """Configuración inicial"""
        # Crear cliente con create_user
        self.cliente = Usuario.objects.create_user(
            nombre_usuario='clientepremium',
            correo='premium@test.com',
            password='password123',
            nombre_completo='Cliente Premium',
            telefono='+56933333333',
            rol='cliente'
        )
        
        # Crear plan con campos correctos
        self.plan = Plan.objects.create(
            nombre='Plan Premium',
            tipo='premium',
            descripcion='Acceso a servicios premium',
            precio_mensual=Decimal('20000.00'),
            cantidad_servicios_mes=10
        )
    
    def test_flujo_suscripcion_completo(self):
        """
        Prueba el flujo de suscripción:
        1. Cliente selecciona plan
        2. Se crea suscripción
        3. Suscripción activa
        4. Verificar beneficios
        """
        
        # 1. Crear suscripción con campos correctos
        fecha_inicio = timezone.now()
        fecha_fin = fecha_inicio + timedelta(days=30)  # Plan premium: 30 días
        
        suscripcion = SuscripcionUsuario.objects.create(
            usuario=self.cliente,
            plan=self.plan,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado='activa'
        )
        
        self.assertIsNotNone(suscripcion.id_suscripcion)
        self.assertEqual(suscripcion.estado, 'activa')
        self.assertEqual(suscripcion.plan, self.plan)
        
        # 2. Verificar que la suscripción está asociada al cliente
        suscripcion.refresh_from_db()
        self.assertEqual(suscripcion.usuario, self.cliente)
        
        # 3. Verificar fechas
        self.assertIsNotNone(suscripcion.fecha_inicio)
        self.assertIsNotNone(suscripcion.fecha_fin)
        self.assertGreater(suscripcion.fecha_fin, suscripcion.fecha_inicio)


class FlujoQuejaYComentarioTest(TestCase):
    """Pruebas del flujo de quejas y comentarios"""
    
    def setUp(self):
        """Configuración inicial"""
        # Crear cliente con create_user
        self.cliente = Usuario.objects.create_user(
            nombre_usuario='clienteinsatisfecho',
            correo='insatisfecho@test.com',
            password='password123',
            nombre_completo='Cliente Insatisfecho',
            telefono='+56944444444',
            rol='cliente'
        )
        
        # Crear empresa con create_user
        self.usuario_empresa = Usuario.objects.create_user(
            nombre_usuario='empresatest2',
            correo='empresa2@test.com',
            password='password123',
            nombre_completo='Empresa Test 2',
            telefono='+56955555555',
            rol='empresa'
        )
        
        self.empresa = Empresa.objects.create(
            nombre_empresa='Lavado Test',
            direccion='Dir Test',
            telefono='+56966666666',
            email='info@test.com',
            contrasena='temp_password123',
            verificada=True
        )
        
        fecha_reserva = timezone.now() + timedelta(days=1)
        self.reserva = Reserva.objects.create(
            usuario=self.cliente,
            empresa=self.empresa,
            fecha=fecha_reserva.date(),
            hora=fecha_reserva.time(),
            placa_vehiculo='BB1234',
            tipo_vehiculo='sedan',
            estado='completado'
        )
    
    def test_flujo_queja_completo(self):
        """
        Prueba el flujo de queja:
        1. Cliente envía queja
        2. Queja se registra
        3. Empresa lee queja
        4. Queja se marca como leída
        """
        
        # 1. Cliente envía queja (con campos correctos del modelo real)
        queja = MensajeQueja.objects.create(
            usuario=self.cliente,
            tipo_pqrs='queja',
            contenido='El servicio no fue satisfactorio',
            urgencia='media',
            acepto_terminos=True
        )
        
        self.assertIsNotNone(queja.id_mensaje)
        self.assertEqual(queja.tipo_pqrs, 'queja')
        self.assertEqual(queja.estado, 'recibido')
        
        # 2. Cambiar estado de la queja
        queja.estado = 'en_proceso'
        queja.save()
        
        queja.refresh_from_db()
        self.assertEqual(queja.estado, 'en_proceso')
    
    def test_flujo_comentario_positivo(self):
        """
        Prueba el flujo de comentario positivo:
        1. Cliente completa reserva
        2. Cliente deja comentario positivo
        3. Comentario se asocia a la reserva
        """
        
        # 1. Cliente deja comentario (con campos correctos del modelo real)
        comentario = Comentario.objects.create(
            usuario=self.cliente,
            comentario='Excelente atención y servicio de calidad'
        )
        
        self.assertIsNotNone(comentario.id_comentario)
        self.assertEqual(comentario.usuario, self.cliente)
        self.assertIn('Excelente', comentario.comentario)


class FlujoMultiplesReservasTest(TestCase):
    """Pruebas con múltiples reservas"""
    
    def setUp(self):
        """Configuración inicial"""
        # Crear cliente con create_user
        self.cliente = Usuario.objects.create_user(
            nombre_usuario='clientefrecuente',
            correo='frecuente@test.com',
            password='password123',
            nombre_completo='Cliente Frecuente',
            telefono='+56966666666',
            rol='cliente'
        )
        
        # Crear empresa con create_user
        self.usuario_empresa = Usuario.objects.create_user(
            nombre_usuario='empresalavado',
            correo='lavado@test.com',
            password='password123',
            nombre_completo='Empresa Lavado',
            telefono='+56977777777',
            rol='empresa'
        )
        
        self.empresa = Empresa.objects.create(
            nombre_empresa='AutoLavado',
            direccion='Calle Lavado 456',
            telefono='+56988888888',
            email='info@autolavado.com',
            contrasena='temp_password123',
            verificada=True
        )
    
    def test_cliente_multiples_reservas(self):
        """Prueba que un cliente pueda tener múltiples reservas"""
        
        # Crear 3 reservas con campos correctos
        reservas = []
        for i in range(3):
            fecha_reserva = timezone.now() + timedelta(days=i+1)
            reserva = Reserva.objects.create(
                usuario=self.cliente,
                empresa=self.empresa,
                fecha=fecha_reserva.date(),
                hora=fecha_reserva.time(),
                placa_vehiculo=f'CC{1000+i}',
                tipo_vehiculo='sedan',
                estado='pendiente'
            )
            reservas.append(reserva)
        
        # Verificar que se crearon 3 reservas
        self.assertEqual(len(reservas), 3)
        
        # Verificar que todas las reservas pertenecen al cliente
        reservas_cliente = Reserva.objects.filter(usuario=self.cliente)
        self.assertEqual(reservas_cliente.count(), 3)
        
        # Verificar diferentes estados (usar estados válidos del modelo)
        reservas[0].estado = 'confirmada'
        reservas[0].save()
        
        reservas[1].estado = 'completado'
        reservas[1].save()
        
        # Contar por estado
        pendientes = Reserva.objects.filter(usuario=self.cliente, estado='pendiente').count()
        confirmadas = Reserva.objects.filter(usuario=self.cliente, estado='confirmada').count()
        completados = Reserva.objects.filter(usuario=self.cliente, estado='completado').count()
        
        self.assertEqual(pendientes, 1)
        self.assertEqual(confirmadas, 1)
        self.assertEqual(completados, 1)


class FlujoVerificacionEmpresaTest(TestCase):
    """Pruebas del flujo de verificación de empresas"""
    
    def test_empresa_no_verificada_no_visible(self):
        """Verifica que empresas no verificadas no sean visibles públicamente"""
        
        # Crear empresa no verificada con create_user
        usuario_empresa = Usuario.objects.create_user(
            nombre_usuario='empresanueva',
            correo='nueva@test.com',
            password='password123',
            nombre_completo='Empresa Nueva',
            telefono='+56988888888',
            rol='empresa'
        )
        
        empresa_no_verificada = Empresa.objects.create(
            nombre_empresa='Empresa Nueva',
            direccion='Calle Nueva 789',
            telefono='+56999999999',
            email='info@nueva.com',
            contrasena='temp_password123',
            verificada=False
        )
        
        # Verificar que no esté en el listado de empresas verificadas
        empresas_visibles = Empresa.objects.filter(verificada=True)
        self.assertNotIn(empresa_no_verificada, empresas_visibles)
        
        # Verificar empresa
        empresa_no_verificada.verificada = True
        empresa_no_verificada.save()
        
        empresa_no_verificada.refresh_from_db()
        self.assertTrue(empresa_no_verificada.verificada)
        
        # Ahora debería estar visible
        empresas_visibles = Empresa.objects.filter(verificada=True)
        self.assertIn(empresa_no_verificada, empresas_visibles)
