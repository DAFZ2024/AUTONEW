-- =====================================================
-- EXPORTACIÓN SQL PARA XAMPP - SISTEMA AUTONEW
-- Base de datos: autonew_django
-- Generado desde modelos Django
-- Fecha: 11 de agosto de 2025
-- =====================================================

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS autonew_django CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE autonew_django;

-- =====================================================
-- TABLA: lavado_auto_usuario
-- Modelo: Usuario (Sistema de autenticación personalizado)
-- =====================================================
CREATE TABLE lavado_auto_usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del usuario. Clave primaria autoincremental que identifica de forma única a cada usuario en el sistema.',
    nombre_completo VARCHAR(255) NOT NULL COMMENT 'Nombre completo del usuario. Incluye nombres y apellidos completos del usuario registrado. Máximo 255 caracteres.',
    nombre_usuario VARCHAR(20) UNIQUE NOT NULL COMMENT 'Nombre de usuario único. Username utilizado para el login. Debe ser único en todo el sistema. Máximo 20 caracteres alfanuméricos.',
    profile_picture VARCHAR(100) NULL COMMENT 'Ruta de la foto de perfil. Almacena la ruta relativa al archivo de imagen del perfil del usuario. Opcional.',
    correo VARCHAR(254) UNIQUE NOT NULL COMMENT 'Dirección de correo electrónico. Email único del usuario, utilizado para login alternativo y comunicaciones. Debe ser válido según RFC 5322.',
    telefono VARCHAR(15) DEFAULT '' COMMENT 'Número de teléfono. Teléfono de contacto del usuario. Formato libre, máximo 15 caracteres. Opcional.',
    direccion VARCHAR(255) DEFAULT '' COMMENT 'Dirección física del usuario. Dirección completa de residencia o trabajo. Máximo 255 caracteres. Opcional.',
    password VARCHAR(128) NOT NULL COMMENT 'Contraseña encriptada. Hash de la contraseña del usuario generado por Django (PBKDF2). Nunca se almacena en texto plano.',
    token_reset VARCHAR(255) NULL COMMENT 'Token para recuperación de contraseña. Token temporal único generado para procesos de recuperación de contraseña. Se elimina tras su uso.',
    rol VARCHAR(50) DEFAULT 'cliente' COMMENT 'Rol del usuario en el sistema. Define los permisos: cliente (usuario normal) o admin (administrador con permisos especiales).',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Estado de activación de la cuenta. Indica si el usuario puede acceder al sistema. FALSE = cuenta deshabilitada.',
    is_staff BOOLEAN DEFAULT FALSE COMMENT 'Acceso al panel de administración. Determina si el usuario puede acceder al admin de Django. TRUE solo para administradores.',
    is_superuser BOOLEAN DEFAULT FALSE COMMENT 'Permisos de superusuario. Otorga todos los permisos en el sistema. TRUE solo para administradores principales.',
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha y hora de registro. Timestamp automático de cuando se creó la cuenta del usuario. No modificable.',
    last_login DATETIME NULL COMMENT 'Último inicio de sesión. Timestamp del último login exitoso del usuario. NULL si nunca ha iniciado sesión.',
    
    INDEX idx_usuario_nombre (nombre_usuario) COMMENT 'Índice en nombre_usuario para optimizar búsquedas de login',
    INDEX idx_usuario_correo (correo) COMMENT 'Índice en correo para optimizar búsquedas por email',
    INDEX idx_usuario_rol (rol) COMMENT 'Índice en rol para filtros por tipo de usuario'
) COMMENT 'Tabla principal para el sistema de autenticación personalizado de usuarios del sistema.';

-- =====================================================
-- TABLA: lavado_auto_servicio
-- Modelo: Servicio
-- =====================================================
CREATE TABLE lavado_auto_servicio (
    id_servicio INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del servicio. Clave primaria autoincremental para cada servicio disponible.',
    nombre_servicio VARCHAR(255) UNIQUE NOT NULL COMMENT 'Nombre del servicio. Denominación comercial del servicio (ej: Lavado Premium). Debe ser único en el catálogo.',
    descripcion TEXT NOT NULL COMMENT 'Descripción detallada del servicio. Explicación completa de qué incluye el servicio, procedimientos y beneficios. Sin límite de caracteres.',
    precio FLOAT NOT NULL COMMENT 'Precio base del servicio. Tarifa estándar en moneda local. Los descuentos empresariales se aplican por separado.',
    
    INDEX idx_servicio_nombre (nombre_servicio) COMMENT 'Índice en nombre_servicio para búsquedas rápidas'
) COMMENT 'Catálogo de servicios de lavado disponibles en el sistema.';

-- =====================================================
-- TABLA: lavado_auto_empresa
-- Modelo: Empresa
-- =====================================================
CREATE TABLE lavado_auto_empresa (
    id_empresa INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la empresa. Clave primaria autoincremental para cada empresa registrada.',
    nombre_empresa VARCHAR(100) NOT NULL COMMENT 'Razón social de la empresa. Nombre legal o comercial de la empresa cliente. Máximo 100 caracteres.',
    direccion VARCHAR(255) NOT NULL COMMENT 'Dirección fiscal de la empresa. Dirección completa de la sede principal o fiscal. Requerida para facturación.',
    telefono VARCHAR(15) NOT NULL COMMENT 'Teléfono principal de contacto. Número principal para comunicaciones comerciales. Máximo 15 caracteres.',
    email VARCHAR(254) NOT NULL COMMENT 'Correo electrónico corporativo. Email principal para comunicaciones oficiales y facturación electrónica.',
    contrasena VARCHAR(255) DEFAULT 'temp_password' COMMENT 'Contraseña temporal de acceso. Contraseña inicial asignada. Debe cambiarse en el primer acceso.',
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de registro en el sistema. Timestamp automático de cuando se registró la empresa.',
    verificada BOOLEAN DEFAULT FALSE COMMENT 'Estado de verificación de la empresa. TRUE = empresa verificada por administración, puede usar servicios. FALSE = pendiente de verificación.',
    
    INDEX idx_empresa_nombre (nombre_empresa) COMMENT 'Índice en nombre_empresa para búsquedas',
    INDEX idx_empresa_verificada (verificada) COMMENT 'Índice en verificada para filtrar empresas activas'
) COMMENT 'Registro de empresas clientes que utilizan servicios empresariales.';

-- =====================================================
-- TABLA: lavado_auto_empresaservicio
-- Modelo: EmpresaServicio (Tabla intermedia)
-- =====================================================
CREATE TABLE lavado_auto_empresaservicio (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la relación. Clave primaria autoincremental para cada asignación empresa-servicio.',
    empresa_id INT NOT NULL COMMENT 'Referencia a la empresa. Clave foránea que apunta al id_empresa en la tabla lavado_auto_empresa.',
    servicio_id INT NOT NULL COMMENT 'Referencia al servicio. Clave foránea que apunta al id_servicio en la tabla lavado_auto_servicio.',
    
    FOREIGN KEY (empresa_id) REFERENCES lavado_auto_empresa(id_empresa) ON DELETE CASCADE,
    FOREIGN KEY (servicio_id) REFERENCES lavado_auto_servicio(id_servicio) ON DELETE CASCADE,
    UNIQUE KEY unique_empresa_servicio (empresa_id, servicio_id) COMMENT 'Única combinación empresa-servicio (evita duplicados)'
) COMMENT 'Tabla intermedia que relaciona empresas con los servicios que tienen contratados.';

-- =====================================================
-- TABLA: lavado_auto_plan
-- Modelo: Plan (Planes de suscripción individuales)
-- =====================================================
CREATE TABLE lavado_auto_plan (
    id_plan INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del plan. Clave primaria autoincremental para cada plan de suscripción individual.',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre comercial del plan. Denominación marketing del plan (ej: Plan Premium Individual).',
    tipo VARCHAR(20) NOT NULL COMMENT 'Tipo de plan. Categoría: basico, premium, completo. Define el nivel de servicios incluidos.',
    descripcion TEXT NOT NULL COMMENT 'Descripción completa del plan. Detalle de beneficios, servicios incluidos y características especiales.',
    precio_mensual DECIMAL(10,2) NOT NULL COMMENT 'Precio mensual del plan. Costo de suscripción mensual en moneda local. Formato: 99999999.99',
    cantidad_servicios_mes INT NOT NULL COMMENT 'Servicios permitidos por mes. Número de servicios que incluye el plan. 0 = ilimitados.',
    activo BOOLEAN DEFAULT TRUE COMMENT 'Estado del plan. TRUE = disponible para nuevas suscripciones. FALSE = descontinuado.',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de creación del plan. Timestamp de cuando se creó el plan en el sistema.',
    incluye_lavado_asientos BOOLEAN DEFAULT TRUE COMMENT 'Incluye limpieza de asientos. TRUE = el plan incluye aspirado y limpieza de asientos.',
    incluye_aspirado BOOLEAN DEFAULT TRUE COMMENT 'Incluye aspirado interior. TRUE = el plan incluye aspirado completo del habitáculo.',
    incluye_lavado_exterior BOOLEAN DEFAULT TRUE COMMENT 'Incluye lavado exterior. TRUE = el plan incluye lavado completo de carrocería.',
    incluye_lavado_interior_humedo BOOLEAN DEFAULT FALSE COMMENT 'Incluye limpieza húmeda interior. TRUE = incluye limpieza con productos específicos del interior.',
    incluye_encerado BOOLEAN DEFAULT FALSE COMMENT 'Incluye aplicación de cera. TRUE = incluye encerado y pulido de la carrocería.',
    incluye_detallado_completo BOOLEAN DEFAULT FALSE COMMENT 'Incluye detallado profesional. TRUE = incluye detallado completo con productos premium.',
    
    INDEX idx_plan_tipo (tipo) COMMENT 'Índice en tipo para filtros por categoría',
    INDEX idx_plan_activo (activo) COMMENT 'Índice en activo para mostrar solo planes disponibles'
) COMMENT 'Planes de suscripción para usuarios individuales.';

-- =====================================================
-- TABLA: lavado_auto_plan_servicios_incluidos
-- Tabla intermedia: Plan - Servicios
-- =====================================================
CREATE TABLE lavado_auto_plan_servicios_incluidos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la relación. Clave primaria autoincremental para cada asignación plan-servicio.',
    plan_id INT NOT NULL COMMENT 'Referencia al plan individual. Clave foránea que apunta al id_plan en la tabla lavado_auto_plan.',
    servicio_id INT NOT NULL COMMENT 'Referencia al servicio incluido. Clave foránea que apunta al id_servicio en la tabla lavado_auto_servicio.',
    
    FOREIGN KEY (plan_id) REFERENCES lavado_auto_plan(id_plan) ON DELETE CASCADE,
    FOREIGN KEY (servicio_id) REFERENCES lavado_auto_servicio(id_servicio) ON DELETE CASCADE,
    UNIQUE KEY unique_plan_servicio (plan_id, servicio_id) COMMENT 'Única combinación plan-servicio'
) COMMENT 'Tabla intermedia que relaciona planes individuales con servicios específicos incluidos.';

-- =====================================================
-- TABLA: lavado_auto_planempresarial
-- Modelo: PlanEmpresarial
-- =====================================================
CREATE TABLE lavado_auto_planempresarial (
    id_plan INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del plan empresarial. Clave primaria autoincremental para cada plan empresarial.',
    nombre VARCHAR(100) NOT NULL COMMENT 'Nombre comercial del plan empresarial. Denominación específica para el mercado B2B.',
    tipo VARCHAR(30) NOT NULL COMMENT 'Tipo de plan empresarial. Categorías: basico_flota, premium_flota, corporativo, transporte_publico.',
    descripcion TEXT NOT NULL COMMENT 'Descripción del plan empresarial. Detalle completo de beneficios, servicios y características para empresas.',
    precio_mensual_por_vehiculo DECIMAL(10,2) NOT NULL COMMENT 'Precio por vehículo al mes. Tarifa mensual por cada vehículo incluido en la flota.',
    precio_base_mensual DECIMAL(10,2) DEFAULT 0 COMMENT 'Precio base fijo mensual. Costo fijo mensual independiente del número de vehículos.',
    vehiculos_minimos INT DEFAULT 5 COMMENT 'Mínimo de vehículos requeridos. Cantidad mínima de vehículos para contratar este plan.',
    vehiculos_maximos INT NULL COMMENT 'Máximo de vehículos permitidos. Límite superior de vehículos. NULL = sin límite.',
    servicios_por_vehiculo_mes INT NOT NULL COMMENT 'Servicios por vehículo mensual. Cantidad de servicios permitidos por vehículo cada mes. 0 = ilimitados.',
    descuento_volumen DECIMAL(5,2) DEFAULT 0 COMMENT 'Descuento por volumen (%). Porcentaje de descuento aplicado por contratar grandes flotas.',
    activo BOOLEAN DEFAULT TRUE COMMENT 'Estado del plan empresarial. TRUE = disponible para contratación. FALSE = descontinuado.',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de creación del plan. Timestamp de cuando se creó el plan empresarial.',
    incluye_lavado_asientos BOOLEAN DEFAULT TRUE COMMENT 'Incluye limpieza de asientos. Específico para vehículos empresariales con mayor uso.',
    incluye_aspirado BOOLEAN DEFAULT TRUE COMMENT 'Incluye aspirado completo. Aspirado profesional para vehículos de trabajo.',
    incluye_lavado_exterior BOOLEAN DEFAULT TRUE COMMENT 'Incluye lavado exterior completo. Mantenimiento de imagen corporativa del vehículo.',
    incluye_lavado_interior_humedo BOOLEAN DEFAULT FALSE COMMENT 'Incluye limpieza húmeda interior. Desinfección y limpieza profunda para vehículos compartidos.',
    incluye_encerado BOOLEAN DEFAULT FALSE COMMENT 'Incluye encerado profesional. Protección adicional para vehículos de representación.',
    incluye_detallado_completo BOOLEAN DEFAULT FALSE COMMENT 'Incluye detallado completo. Servicio premium para vehículos ejecutivos.',
    incluye_servicio_domicilio BOOLEAN DEFAULT FALSE COMMENT 'Incluye servicio a domicilio. Recogida y entrega en las instalaciones de la empresa.',
    incluye_mantenimiento_programado BOOLEAN DEFAULT FALSE COMMENT 'Incluye mantenimiento programado. Calendario automático de servicios preventivos.',
    incluye_reporte_mensual BOOLEAN DEFAULT FALSE COMMENT 'Incluye reportes mensuales. Informes detallados de servicios realizados y estado de flota.',
    incluye_soporte_24_7 BOOLEAN DEFAULT FALSE COMMENT 'Incluye soporte 24/7. Atención al cliente especializada las 24 horas.',
    
    INDEX idx_plan_empresarial_tipo (tipo) COMMENT 'Índice en tipo para categorización',
    INDEX idx_plan_empresarial_activo (activo) COMMENT 'Índice en activo para planes disponibles'
) COMMENT 'Planes de suscripción diseñados específicamente para empresas con flotas vehiculares.';

-- =====================================================
-- TABLA: lavado_auto_planempresarial_servicios_incluidos
-- Tabla intermedia: PlanEmpresarial - Servicios
-- =====================================================
CREATE TABLE lavado_auto_planempresarial_servicios_incluidos (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la relación. Clave primaria para cada asignación plan empresarial-servicio.',
    planempresarial_id INT NOT NULL COMMENT 'Referencia al plan empresarial. Clave foránea que apunta al id_plan en lavado_auto_planempresarial.',
    servicio_id INT NOT NULL COMMENT 'Referencia al servicio incluido. Clave foránea que apunta al id_servicio en lavado_auto_servicio.',
    
    FOREIGN KEY (planempresarial_id) REFERENCES lavado_auto_planempresarial(id_plan) ON DELETE CASCADE,
    FOREIGN KEY (servicio_id) REFERENCES lavado_auto_servicio(id_servicio) ON DELETE CASCADE,
    UNIQUE KEY unique_plan_empresarial_servicio (planempresarial_id, servicio_id) COMMENT 'Única combinación plan empresarial-servicio'
) COMMENT 'Tabla intermedia que relaciona planes empresariales con servicios específicos.';

-- =====================================================
-- TABLA: lavado_auto_suscripcionusuario
-- Modelo: SuscripcionUsuario
-- =====================================================
CREATE TABLE lavado_auto_suscripcionusuario (
    id_suscripcion INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la suscripción. Clave primaria autoincremental para cada suscripción individual.',
    usuario_id INT NOT NULL COMMENT 'Referencia al usuario suscrito. Clave foránea que apunta al id_usuario en lavado_auto_usuario.',
    plan_id INT NOT NULL COMMENT 'Referencia al plan contratado. Clave foránea que apunta al id_plan en lavado_auto_plan.',
    fecha_inicio DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de inicio de suscripción. Timestamp de cuando comenzó la vigencia del plan.',
    fecha_fin DATETIME NOT NULL COMMENT 'Fecha de vencimiento. Timestamp de cuando expira la suscripción. Se calcula automáticamente (+30 días).',
    estado VARCHAR(20) DEFAULT 'activa' COMMENT 'Estado de la suscripción. Valores: activa, pausada, cancelada, vencida.',
    servicios_utilizados_mes INT DEFAULT 0 COMMENT 'Servicios consumidos este mes. Contador de servicios utilizados en el período actual. Se reinicia mensualmente.',
    ultimo_reinicio_contador DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Última fecha de reinicio del contador. Timestamp del último reinicio mensual del contador de servicios.',
    auto_renovar BOOLEAN DEFAULT TRUE COMMENT 'Renovación automática. TRUE = se renueva automáticamente al vencer. FALSE = se debe renovar manualmente.',
    
    FOREIGN KEY (usuario_id) REFERENCES lavado_auto_usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES lavado_auto_plan(id_plan) ON DELETE CASCADE,
    INDEX idx_suscripcion_estado (estado) COMMENT 'Índice en estado para filtros de estado',
    INDEX idx_suscripcion_fecha_fin (fecha_fin) COMMENT 'Índice en fecha_fin para verificar vencimientos'
) COMMENT 'Suscripciones activas de usuarios individuales a planes de servicio.';

-- =====================================================
-- TABLA: lavado_auto_suscripcionempresarial
-- Modelo: SuscripcionEmpresarial
-- =====================================================
CREATE TABLE lavado_auto_suscripcionempresarial (
    id_suscripcion INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de suscripción empresarial. Clave primaria para cada suscripción empresarial.',
    empresa_id INT NOT NULL COMMENT 'Referencia a la empresa suscrita. Clave foránea que apunta al id_empresa en lavado_auto_empresa.',
    plan_id INT NOT NULL COMMENT 'Referencia al plan empresarial. Clave foránea que apunta al id_plan en lavado_auto_planempresarial.',
    cantidad_vehiculos INT NOT NULL COMMENT 'Número de vehículos en la flota. Cantidad total de vehículos cubiertos por la suscripción.',
    fecha_inicio DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de inicio de suscripción. Timestamp de cuando comenzó la vigencia del plan empresarial.',
    fecha_fin DATETIME NOT NULL COMMENT 'Fecha de vencimiento. Timestamp de cuando expira la suscripción empresarial.',
    estado VARCHAR(20) DEFAULT 'activa' COMMENT 'Estado de la suscripción. Valores: activa, pausada, cancelada, vencida.',
    servicios_utilizados_mes INT DEFAULT 0 COMMENT 'Servicios consumidos este mes. Contador total de servicios utilizados por toda la flota en el período.',
    ultimo_reinicio_contador DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Última fecha de reinicio del contador. Timestamp del último reinicio mensual del contador.',
    auto_renovar BOOLEAN DEFAULT TRUE COMMENT 'Renovación automática. TRUE = renovación automática al vencer. FALSE = renovación manual.',
    precio_mensual_actual DECIMAL(12,2) NOT NULL COMMENT 'Precio mensual calculado. Monto total mensual basado en la cantidad de vehículos y descuentos aplicados.',
    contacto_responsable VARCHAR(255) NOT NULL COMMENT 'Responsable de la cuenta. Nombre de la persona encargada de la gestión de la flota en la empresa.',
    telefono_contacto VARCHAR(15) NOT NULL COMMENT 'Teléfono del responsable. Número directo del responsable para coordinaciones operativas.',
    notas_especiales TEXT DEFAULT '' COMMENT 'Notas y observaciones especiales. Información adicional sobre requisitos especiales o acuerdos particulares.',
    
    FOREIGN KEY (empresa_id) REFERENCES lavado_auto_empresa(id_empresa) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES lavado_auto_planempresarial(id_plan) ON DELETE CASCADE,
    INDEX idx_suscripcion_empresarial_estado (estado) COMMENT 'Índice en estado',
    INDEX idx_suscripcion_empresarial_fecha_fin (fecha_fin) COMMENT 'Índice en fecha_fin'
) COMMENT 'Suscripciones empresariales para gestión de flotas vehiculares.';

-- =====================================================
-- TABLA: lavado_auto_reserva
-- Modelo: Reserva
-- =====================================================
CREATE TABLE lavado_auto_reserva (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la reserva. Clave primaria autoincremental para cada reserva del sistema.',
    fecha DATE NOT NULL COMMENT 'Fecha programada del servicio. Día en que se realizará el servicio de lavado.',
    hora TIME NOT NULL COMMENT 'Hora programada del servicio. Hora específica de inicio del servicio.',
    estado VARCHAR(20) DEFAULT 'pendiente' COMMENT 'Estado actual de la reserva. Valores: pendiente, completado, cancelada.',
    empresa_id INT NOT NULL COMMENT 'Empresa que realizará el servicio. Clave foránea que apunta al id_empresa en lavado_auto_empresa.',
    usuario_id INT NOT NULL COMMENT 'Usuario que realizó la reserva. Clave foránea que apunta al id_usuario en lavado_auto_usuario.',
    suscripcion_utilizada_id INT NULL COMMENT 'Suscripción individual utilizada. Referencia a la suscripción individual si aplica. NULL para pagos individuales.',
    es_pago_individual BOOLEAN DEFAULT FALSE COMMENT 'Indica si es pago por servicio. TRUE = pago individual sin suscripción. FALSE = usa suscripción.',
    suscripcion_empresarial_id INT NULL COMMENT 'Suscripción empresarial utilizada. Referencia a la suscripción empresarial si aplica.',
    es_reserva_empresarial BOOLEAN DEFAULT FALSE COMMENT 'Indica si es reserva empresarial. TRUE = reserva de flota empresarial. FALSE = reserva individual.',
    placa_vehiculo VARCHAR(20) NULL COMMENT 'Placa del vehículo a lavar. Identificación del vehículo para reservas empresariales.',
    tipo_vehiculo VARCHAR(50) NULL COMMENT 'Tipo de vehículo. Categoría: sedan, suv, camioneta, bus, microbus, camion, taxi, moto.',
    conductor_asignado VARCHAR(255) DEFAULT '' COMMENT 'Conductor responsable. Nombre del conductor del vehículo para reservas empresariales.',
    observaciones_empresariales TEXT DEFAULT '' COMMENT 'Observaciones especiales. Notas adicionales para el servicio empresarial (daños existentes, urgencia, etc.).',
    
    FOREIGN KEY (empresa_id) REFERENCES lavado_auto_empresa(id_empresa) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES lavado_auto_usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (suscripcion_utilizada_id) REFERENCES lavado_auto_suscripcionusuario(id_suscripcion) ON DELETE SET NULL,
    FOREIGN KEY (suscripcion_empresarial_id) REFERENCES lavado_auto_suscripcionempresarial(id_suscripcion) ON DELETE SET NULL,
    
    INDEX idx_reserva_fecha (fecha) COMMENT 'Índice en fecha para búsquedas por día',
    INDEX idx_reserva_estado (estado) COMMENT 'Índice en estado para filtros de estado',
    INDEX idx_reserva_placa (placa_vehiculo) COMMENT 'Índice en placa_vehiculo para búsquedas vehiculares'
) COMMENT 'Tabla central para el registro de todas las reservas de servicios, tanto individuales como empresariales.';

-- =====================================================
-- TABLA: lavado_auto_reservaservicio
-- Modelo: ReservaServicio (Tabla intermedia)
-- =====================================================
CREATE TABLE lavado_auto_reservaservicio (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la relación. Clave primaria para cada asignación reserva-servicio.',
    reserva_id INT NOT NULL COMMENT 'Referencia a la reserva. Clave foránea que apunta al id_reserva en lavado_auto_reserva.',
    servicio_id INT NOT NULL COMMENT 'Referencia al servicio solicitado. Clave foránea que apunta al id_servicio en lavado_auto_servicio.',
    precio_aplicado DECIMAL(10,2) NULL COMMENT 'Precio específico aplicado. Precio final cobrado, puede incluir descuentos empresariales o promociones.',
    descuento_empresarial DECIMAL(5,2) DEFAULT 0 COMMENT 'Descuento empresarial aplicado (%). Porcentaje de descuento aplicado por ser cliente empresarial.',
    
    FOREIGN KEY (reserva_id) REFERENCES lavado_auto_reserva(id_reserva) ON DELETE CASCADE,
    FOREIGN KEY (servicio_id) REFERENCES lavado_auto_servicio(id_servicio) ON DELETE CASCADE,
    UNIQUE KEY unique_reserva_servicio (reserva_id, servicio_id) COMMENT 'Única combinación reserva-servicio'
) COMMENT 'Tabla intermedia que relaciona reservas con servicios específicos solicitados.';

-- =====================================================
-- TABLA: lavado_auto_pago
-- Modelo: Pago
-- =====================================================
CREATE TABLE lavado_auto_pago (
    id_pago INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del pago. Clave primaria autoincremental para cada transacción de pago.',
    fecha_pago DATE NOT NULL COMMENT 'Fecha del pago. Día en que se procesó el pago. Se asigna automáticamente.',
    monto FLOAT NOT NULL COMMENT 'Monto total pagado. Cantidad total abonada por los servicios de la reserva.',
    metodo_pago VARCHAR(50) NOT NULL COMMENT 'Método de pago utilizado. Forma de pago: efectivo, tarjeta, transferencia, billetera_digital, etc.',
    reserva_id INT NOT NULL COMMENT 'Referencia a la reserva pagada. Clave foránea que apunta al id_reserva en lavado_auto_reserva.',
    usuario_id INT NOT NULL COMMENT 'Usuario que realizó el pago. Clave foránea que apunta al id_usuario en lavado_auto_usuario.',
    
    FOREIGN KEY (reserva_id) REFERENCES lavado_auto_reserva(id_reserva) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES lavado_auto_usuario(id_usuario) ON DELETE CASCADE,
    INDEX idx_pago_fecha (fecha_pago) COMMENT 'Índice en fecha_pago para reportes financieros'
) COMMENT 'Registro de todos los pagos realizados por servicios individuales.';

-- =====================================================
-- TABLA: lavado_auto_pasareladepago
-- Modelo: PasarelaDePago
-- =====================================================
CREATE TABLE lavado_auto_pasareladepago (
    id_pasarela INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de transacción. Clave primaria para cada transacción de pasarela externa.',
    nombre_pasarela VARCHAR(100) NOT NULL COMMENT 'Nombre de la pasarela de pago. Identificación del proveedor: PayPal, Stripe, MercadoPago, etc.',
    estado_transaccion VARCHAR(50) NOT NULL COMMENT 'Estado de la transacción. Estado reportado por la pasarela: approved, pending, rejected, refunded.',
    pago_id INT NOT NULL COMMENT 'Referencia al pago asociado. Clave foránea que apunta al id_pago en lavado_auto_pago.',
    
    FOREIGN KEY (pago_id) REFERENCES lavado_auto_pago(id_pago) ON DELETE CASCADE
) COMMENT 'Información de transacciones procesadas a través de pasarelas de pago externas.';

-- =====================================================
-- TABLA: lavado_auto_historialpagossuscripcion
-- Modelo: HistorialPagosSuscripcion
-- =====================================================
CREATE TABLE lavado_auto_historialpagossuscripcion (
    id_pago_suscripcion INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del pago de suscripción. Clave primaria para cada pago de suscripción individual.',
    suscripcion_id INT NOT NULL COMMENT 'Referencia a la suscripción. Clave foránea que apunta al id_suscripcion en lavado_auto_suscripcionusuario.',
    monto DECIMAL(10,2) NOT NULL COMMENT 'Monto del pago de suscripción. Cantidad abonada por el período de suscripción.',
    fecha_pago DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha y hora del pago. Timestamp exacto de cuando se procesó el pago.',
    estado VARCHAR(20) DEFAULT 'pendiente' COMMENT 'Estado del pago. Valores: pendiente, aprobado, rechazado, reembolsado.',
    referencia_pago VARCHAR(255) UNIQUE NOT NULL COMMENT 'Referencia única del pago. Código único generado para identificar y rastrear el pago.',
    metodo_pago VARCHAR(50) NOT NULL COMMENT 'Método de pago utilizado. Forma de pago para la suscripción.',
    
    FOREIGN KEY (suscripcion_id) REFERENCES lavado_auto_suscripcionusuario(id_suscripcion) ON DELETE CASCADE,
    INDEX idx_historial_pago_estado (estado) COMMENT 'Índice en estado',
    INDEX idx_historial_pago_fecha (fecha_pago) COMMENT 'Índice en fecha_pago'
) COMMENT 'Historial completo de pagos de suscripciones individuales.';

-- =====================================================
-- TABLA: lavado_auto_historialpagossuscripcionempresarial
-- Modelo: HistorialPagosSuscripcionEmpresarial
-- =====================================================
CREATE TABLE lavado_auto_historialpagossuscripcionempresarial (
    id_pago_suscripcion INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del pago empresarial. Clave primaria para cada pago de suscripción empresarial.',
    suscripcion_id INT NOT NULL COMMENT 'Referencia a la suscripción empresarial. Clave foránea que apunta al id_suscripcion en lavado_auto_suscripcionempresarial.',
    monto DECIMAL(12,2) NOT NULL COMMENT 'Monto del pago empresarial. Cantidad total facturada (mayor precisión para montos corporativos).',
    fecha_pago DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha y hora del pago. Timestamp exacto del procesamiento del pago empresarial.',
    estado VARCHAR(20) DEFAULT 'pendiente' COMMENT 'Estado del pago empresarial. Valores: pendiente, aprobado, rechazado, reembolsado.',
    referencia_pago VARCHAR(255) UNIQUE NOT NULL COMMENT 'Referencia única empresarial. Código único para facturación y seguimiento empresarial.',
    metodo_pago VARCHAR(50) NOT NULL COMMENT 'Método de pago empresarial. Forma de pago corporativa (transferencia, cheque, etc.).',
    periodo_facturado VARCHAR(20) NOT NULL COMMENT 'Período facturado. Identificación del período: 2024-01, 2024-02, etc.',
    
    FOREIGN KEY (suscripcion_id) REFERENCES lavado_auto_suscripcionempresarial(id_suscripcion) ON DELETE CASCADE,
    INDEX idx_historial_pago_empresarial_estado (estado) COMMENT 'Índice en estado',
    INDEX idx_historial_pago_empresarial_fecha (fecha_pago) COMMENT 'Índice en fecha_pago'
) COMMENT 'Historial de pagos para suscripciones empresariales con mayor volumen.';

-- =====================================================
-- TABLA: lavado_auto_mensajequeja
-- Modelo: MensajeQueja
-- =====================================================
CREATE TABLE lavado_auto_mensajequeja (
    id_mensaje INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del mensaje. Clave primaria autoincremental para cada mensaje o queja.',
    contenido TEXT NOT NULL COMMENT 'Contenido del mensaje o queja. Texto completo del mensaje enviado por el usuario. Sin límite de caracteres.',
    fecha_envio DATE NOT NULL COMMENT 'Fecha de envío. Día en que el usuario envió el mensaje. Se asigna automáticamente.',
    estado VARCHAR(50) DEFAULT 'no respondido' COMMENT 'Estado del mensaje. Valores: no respondido, en proceso, respondido, cerrado.',
    respuesta TEXT DEFAULT '' COMMENT 'Respuesta del administrador. Texto de respuesta oficial del equipo de atención al cliente.',
    usuario_id INT NOT NULL COMMENT 'Usuario que envió el mensaje. Clave foránea que apunta al id_usuario en lavado_auto_usuario.',
    
    FOREIGN KEY (usuario_id) REFERENCES lavado_auto_usuario(id_usuario) ON DELETE CASCADE,
    INDEX idx_mensaje_estado (estado) COMMENT 'Índice en estado para gestión de cola de atención',
    INDEX idx_mensaje_fecha (fecha_envio) COMMENT 'Índice en fecha_envio para orden cronológico'
) COMMENT 'Sistema de mensajería y gestión de quejas de usuarios.';

-- =====================================================
-- TABLA: lavado_auto_comentario
-- Modelo: Comentario
-- =====================================================
CREATE TABLE lavado_auto_comentario (
    id_comentario INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del comentario. Clave primaria autoincremental para cada comentario.',
    comentario TEXT NOT NULL COMMENT 'Texto del comentario. Reseña o comentario completo del usuario sobre el servicio.',
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha y hora del comentario. Timestamp exacto de cuando se publicó el comentario.',
    usuario_id INT NOT NULL COMMENT 'Usuario que hizo el comentario. Clave foránea que apunta al id_usuario en lavado_auto_usuario.',
    
    FOREIGN KEY (usuario_id) REFERENCES lavado_auto_usuario(id_usuario) ON DELETE CASCADE,
    INDEX idx_comentario_fecha (fecha) COMMENT 'Índice en fecha para orden cronológico'
) COMMENT 'Comentarios y reseñas de usuarios sobre servicios recibidos.';

-- =====================================================
-- TABLA: lavado_auto_detallereservaempresarial
-- Modelo: DetalleReservaEmpresarial
-- =====================================================
CREATE TABLE lavado_auto_detallereservaempresarial (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del detalle. Clave primaria autoincremental para cada detalle empresarial.',
    reserva_id INT UNIQUE NOT NULL COMMENT 'Referencia única a la reserva. Clave foránea única que apunta al id_reserva en lavado_auto_reserva.',
    numero_interno_empresa VARCHAR(50) DEFAULT '' COMMENT 'Número interno del vehículo. Código interno que la empresa asigna al vehículo para control.',
    departamento_solicitante VARCHAR(100) DEFAULT '' COMMENT 'Departamento que solicita. Área o departamento de la empresa que solicita el servicio.',
    centro_costo VARCHAR(50) DEFAULT '' COMMENT 'Centro de costo contable. Código contable al que se imputa el gasto del servicio.',
    kilometraje_actual INT NULL COMMENT 'Kilometraje del vehículo. Odómetro actual del vehículo al momento del servicio.',
    proxima_revision DATE NULL COMMENT 'Fecha de próxima revisión. Programación de próximo mantenimiento preventivo.',
    responsable_vehiculo VARCHAR(255) DEFAULT '' COMMENT 'Responsable del vehículo. Empleado asignado como responsable del vehículo.',
    
    FOREIGN KEY (reserva_id) REFERENCES lavado_auto_reserva(id_reserva) ON DELETE CASCADE
) COMMENT 'Detalles adicionales específicos para reservas de flotas empresariales.';

-- =====================================================
-- TABLA: lavado_auto_solicitudservicioempresa
-- Modelo: SolicitudServicioEmpresa
-- =====================================================
CREATE TABLE lavado_auto_solicitudservicioempresa (
    id_solicitud INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la solicitud. Clave primaria autoincremental para cada solicitud empresarial.',
    empresa_id INT NOT NULL COMMENT 'Empresa solicitante. Clave foránea que apunta al id_empresa en lavado_auto_empresa.',
    servicio_solicitado_id INT NOT NULL COMMENT 'Servicio solicitado. Clave foránea que apunta al id_servicio en lavado_auto_servicio.',
    estado VARCHAR(20) DEFAULT 'pendiente' COMMENT 'Estado de la solicitud. Valores: pendiente, aprobada, rechazada, en_revision.',
    fecha_solicitud DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de la solicitud. Timestamp de cuando la empresa envió la solicitud.',
    fecha_respuesta DATETIME NULL COMMENT 'Fecha de respuesta. Timestamp de cuando se respondió la solicitud. NULL si está pendiente.',
    motivo_solicitud TEXT NOT NULL COMMENT 'Justificación de la solicitud. Razón detallada por la cual la empresa necesita este servicio adicional.',
    respuesta_admin TEXT DEFAULT '' COMMENT 'Respuesta del administrador. Justificación de aprobación o rechazo de la solicitud.',
    usuario_responsable VARCHAR(255) NOT NULL COMMENT 'Responsable de la solicitud. Persona de la empresa que realizó la solicitud.',
    telefono_contacto VARCHAR(15) NOT NULL COMMENT 'Teléfono de contacto. Número directo para coordinaciones sobre la solicitud.',
    
    FOREIGN KEY (empresa_id) REFERENCES lavado_auto_empresa(id_empresa) ON DELETE CASCADE,
    FOREIGN KEY (servicio_solicitado_id) REFERENCES lavado_auto_servicio(id_servicio) ON DELETE CASCADE,
    UNIQUE KEY unique_empresa_servicio_estado (empresa_id, servicio_solicitado_id, estado) COMMENT 'Evita solicitudes duplicadas pendientes',
    INDEX idx_solicitud_estado (estado) COMMENT 'Índice en estado para gestión de solicitudes',
    INDEX idx_solicitud_fecha (fecha_solicitud) COMMENT 'Índice en fecha_solicitud para orden cronológico'
) COMMENT 'Gestión de solicitudes de empresas para agregar nuevos servicios a su contrato.';

-- =====================================================
-- DATOS DE EJEMPLO PARA COMENZAR
-- =====================================================

-- Insertar servicios básicos
INSERT INTO lavado_auto_servicio (nombre_servicio, descripcion, precio) VALUES
('Lavado Básico', 'Lavado exterior completo del vehículo', 15.00),
('Lavado Premium', 'Lavado exterior e interior completo', 25.00),
('Lavado Completo', 'Lavado completo con encerado y detallado', 40.00),
('Aspirado Interior', 'Aspirado completo del interior', 8.00),
('Encerado', 'Aplicación de cera protectora', 20.00),
('Detallado Motor', 'Limpieza y detallado del motor', 30.00);

-- Insertar planes individuales
INSERT INTO lavado_auto_plan (nombre, tipo, descripcion, precio_mensual, cantidad_servicios_mes) VALUES
('Plan Básico', 'basico', 'Plan básico con 2 lavados al mes', 25.00, 2),
('Plan Premium', 'premium', 'Plan premium con 4 lavados al mes', 45.00, 4),
('Plan Completo', 'completo', 'Plan completo con lavados ilimitados', 80.00, 0);

-- Insertar planes empresariales
INSERT INTO lavado_auto_planempresarial (nombre, tipo, descripcion, precio_mensual_por_vehiculo, precio_base_mensual, vehiculos_minimos, servicios_por_vehiculo_mes) VALUES
('Flota Básica', 'basico_flota', 'Plan básico para flotas pequeñas', 20.00, 50.00, 5, 2),
('Flota Premium', 'premium_flota', 'Plan premium para flotas medianas', 35.00, 100.00, 10, 4),
('Plan Corporativo', 'corporativo', 'Plan completo para grandes empresas', 50.00, 200.00, 20, 0);

-- Insertar usuario administrador
INSERT INTO lavado_auto_usuario (nombre_completo, nombre_usuario, correo, password, rol, is_staff, is_superuser) VALUES
('Administrador Sistema', 'admin', 'admin@autonew.com', 'pbkdf2_sha256$260000$admin123$hash', 'admin', TRUE, TRUE);

-- =====================================================
-- ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- =====================================================

-- Índices compuestos para consultas frecuentes
CREATE INDEX idx_reserva_fecha_estado ON lavado_auto_reserva(fecha, estado) COMMENT 'Índice compuesto para búsquedas por fecha y estado simultáneamente';
CREATE INDEX idx_suscripcion_usuario_estado_compuesto ON lavado_auto_suscripcionusuario(usuario_id, estado) COMMENT 'Índice compuesto para consultas de suscripciones por usuario y estado';
CREATE INDEX idx_suscripcion_empresarial_empresa_estado ON lavado_auto_suscripcionempresarial(empresa_id, estado) COMMENT 'Índice compuesto para consultas empresariales por empresa y estado';

-- =====================================================
-- TRIGGERS PARA AUTOMATIZACIÓN
-- =====================================================

-- Trigger para auto-generar fecha_fin en suscripciones
DELIMITER //
CREATE TRIGGER tr_suscripcion_fecha_fin 
BEFORE INSERT ON lavado_auto_suscripcionusuario 
FOR EACH ROW 
BEGIN
    IF NEW.fecha_fin IS NULL THEN
        SET NEW.fecha_fin = DATE_ADD(NEW.fecha_inicio, INTERVAL 30 DAY);
    END IF;
END//

CREATE TRIGGER tr_suscripcion_empresarial_fecha_fin 
BEFORE INSERT ON lavado_auto_suscripcionempresarial 
FOR EACH ROW 
BEGIN
    IF NEW.fecha_fin IS NULL THEN
        SET NEW.fecha_fin = DATE_ADD(NEW.fecha_inicio, INTERVAL 30 DAY);
    END IF;
END//
DELIMITER ;

-- =====================================================
-- VISTAS ÚTILES PARA REPORTES
-- =====================================================

-- Vista para reservas con información completa
-- Muestra ID, fecha, hora, estado, cliente, correo, empresa, placa, tipo de vehículo, 
-- si es empresarial y lista de servicios concatenados
CREATE VIEW vista_reservas_completas AS
SELECT 
    r.id_reserva,
    r.fecha,
    r.hora,
    r.estado,
    u.nombre_completo as cliente,
    u.correo as correo_cliente,
    e.nombre_empresa,
    r.placa_vehiculo,
    r.tipo_vehiculo,
    r.es_reserva_empresarial,
    GROUP_CONCAT(s.nombre_servicio SEPARATOR ', ') as servicios
FROM lavado_auto_reserva r
JOIN lavado_auto_usuario u ON r.usuario_id = u.id_usuario
JOIN lavado_auto_empresa e ON r.empresa_id = e.id_empresa
LEFT JOIN lavado_auto_reservaservicio rs ON r.id_reserva = rs.reserva_id
LEFT JOIN lavado_auto_servicio s ON rs.servicio_id = s.id_servicio
GROUP BY r.id_reserva;

-- Vista para suscripciones activas
-- Unifica suscripciones individuales y empresariales mostrando:
-- tipo, ID, cliente, correo, plan, fechas, estado, servicios utilizados y permitidos
CREATE VIEW vista_suscripciones_activas AS
SELECT 
    'individual' as tipo_suscripcion,
    s.id_suscripcion,
    u.nombre_completo as cliente,
    u.correo,
    p.nombre as plan,
    s.fecha_inicio,
    s.fecha_fin,
    s.estado,
    s.servicios_utilizados_mes,
    p.cantidad_servicios_mes
FROM lavado_auto_suscripcionusuario s
JOIN lavado_auto_usuario u ON s.usuario_id = u.id_usuario
JOIN lavado_auto_plan p ON s.plan_id = p.id_plan
WHERE s.estado = 'activa'

UNION ALL

SELECT 
    'empresarial' as tipo_suscripcion,
    se.id_suscripcion,
    e.nombre_empresa as cliente,
    e.email as correo,
    pe.nombre as plan,
    se.fecha_inicio,
    se.fecha_fin,
    se.estado,
    se.servicios_utilizados_mes,
    (pe.servicios_por_vehiculo_mes * se.cantidad_vehiculos) as cantidad_servicios_mes
FROM lavado_auto_suscripcionempresarial se
JOIN lavado_auto_empresa e ON se.empresa_id = e.id_empresa
JOIN lavado_auto_planempresarial pe ON se.plan_id = pe.id_plan
WHERE se.estado = 'activa';

-- =====================================================
-- COMENTARIOS Y DOCUMENTACIÓN
-- =====================================================

/*
NOTAS IMPORTANTES:

1. Este script está optimizado para MySQL/MariaDB (XAMPP).

2. Las contraseñas en Django usan hash, por lo que necesitarás usar
   el panel de administración de Django para crear usuarios.

3. Los campos de imagen (profile_picture) almacenan rutas relativas.
   Asegúrate de configurar correctamente MEDIA_ROOT en Django.

4. Las fechas usan DATETIME para compatibilidad con timezone de Django.

5. Se incluyen índices para optimizar las consultas más frecuentes.

6. Las vistas facilitarán la generación de reportes.

7. Los triggers automatizan el cálculo de fechas de vencimiento.

PARA IMPORTAR EN XAMPP:
1. Abre phpMyAdmin
2. Crea una nueva base de datos llamada 'autonew_django'
3. Importa este archivo SQL
4. Ajusta la configuración de Django para usar esta base de datos

CONFIGURACIÓN DJANGO (settings.py):
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'autonew_django',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
*/
