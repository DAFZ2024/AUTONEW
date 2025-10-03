-- Script SQL para crear la base de datos AUTONEW en MySQL
-- Generado basado en los modelos de Django
-- Base de datos: autonew_db

CREATE DATABASE IF NOT EXISTS autonew_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE autonew_db;

-- Tabla: lavado_auto_usuario (Usuario)
CREATE TABLE lavado_auto_usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME(6) NULL,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    nombre_completo VARCHAR(255) NOT NULL,
    nombre_usuario VARCHAR(20) NOT NULL UNIQUE,
    profile_picture VARCHAR(100) NULL,
    correo VARCHAR(254) NOT NULL UNIQUE,
    telefono VARCHAR(15) NOT NULL DEFAULT '',
    direccion VARCHAR(255) NOT NULL DEFAULT '',
    token_reset VARCHAR(255) NULL,
    rol VARCHAR(50) NOT NULL DEFAULT 'cliente',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_registro DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    failed_login_attempts INT NOT NULL DEFAULT 0,
    last_failed_login DATETIME(6) NULL,
    is_locked_out BOOLEAN NOT NULL DEFAULT FALSE,
    lockout_time DATETIME(6) NULL,
    INDEX idx_usuario_correo (correo),
    INDEX idx_usuario_nombre_usuario (nombre_usuario)
);

-- Tabla: lavado_auto_servicio (Servicio)
CREATE TABLE lavado_auto_servicio (
    id_servicio INT AUTO_INCREMENT PRIMARY KEY,
    nombre_servicio VARCHAR(255) NOT NULL UNIQUE,
    descripcion TEXT NOT NULL,
    precio DOUBLE NOT NULL,
    INDEX idx_servicio_nombre (nombre_servicio)
);

-- Tabla: lavado_auto_empresa (Empresa)
CREATE TABLE lavado_auto_empresa (
    id_empresa INT AUTO_INCREMENT PRIMARY KEY,
    nombre_empresa VARCHAR(100) NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    email VARCHAR(254) NOT NULL,
    contrasena VARCHAR(255) NOT NULL DEFAULT 'temp_password',
    fecha_registro DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    verificada BOOLEAN NOT NULL DEFAULT FALSE,
    latitud DECIMAL(10, 8) NULL,
    longitud DECIMAL(11, 8) NULL,
    INDEX idx_empresa_nombre (nombre_empresa),
    INDEX idx_empresa_email (email)
);

-- Tabla: lavado_auto_empresaservicio (EmpresaServicio) - Tabla intermedia
CREATE TABLE lavado_auto_empresaservicio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    empresa_id INT NOT NULL,
    servicio_id INT NOT NULL,
    FOREIGN KEY (empresa_id) REFERENCES lavado_auto_empresa(id_empresa) ON DELETE CASCADE,
    FOREIGN KEY (servicio_id) REFERENCES lavado_auto_servicio(id_servicio) ON DELETE CASCADE,
    UNIQUE KEY unique_empresa_servicio (empresa_id, servicio_id)
);

-- Tabla: lavado_auto_plan (Plan)
CREATE TABLE lavado_auto_plan (
    id_plan INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    descripcion TEXT NOT NULL,
    precio_mensual DECIMAL(10, 2) NOT NULL,
    cantidad_servicios_mes INT NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    incluye_lavado_asientos BOOLEAN NOT NULL DEFAULT TRUE,
    incluye_aspirado BOOLEAN NOT NULL DEFAULT TRUE,
    incluye_lavado_exterior BOOLEAN NOT NULL DEFAULT TRUE,
    incluye_lavado_interior_humedo BOOLEAN NOT NULL DEFAULT FALSE,
    incluye_encerado BOOLEAN NOT NULL DEFAULT FALSE,
    incluye_detallado_completo BOOLEAN NOT NULL DEFAULT FALSE,
    INDEX idx_plan_tipo (tipo),
    INDEX idx_plan_activo (activo)
);

-- Tabla intermedia: lavado_auto_plan_servicios_incluidos
CREATE TABLE lavado_auto_plan_servicios_incluidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plan_id INT NOT NULL,
    servicio_id INT NOT NULL,
    FOREIGN KEY (plan_id) REFERENCES lavado_auto_plan(id_plan) ON DELETE CASCADE,
    FOREIGN KEY (servicio_id) REFERENCES lavado_auto_servicio(id_servicio) ON DELETE CASCADE,
    UNIQUE KEY unique_plan_servicio (plan_id, servicio_id)
);

-- Tabla: lavado_auto_planempresarial (PlanEmpresarial)
CREATE TABLE lavado_auto_planempresarial (
    id_plan INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(30) NOT NULL,
    descripcion TEXT NOT NULL,
    precio_mensual_por_vehiculo DECIMAL(10, 2) NOT NULL,
    precio_base_mensual DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    vehiculos_minimos INT NOT NULL DEFAULT 5,
    vehiculos_maximos INT NULL,
    servicios_por_vehiculo_mes INT NOT NULL,
    descuento_volumen DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    incluye_lavado_asientos BOOLEAN NOT NULL DEFAULT TRUE,
    incluye_aspirado BOOLEAN NOT NULL DEFAULT TRUE,
    incluye_lavado_exterior BOOLEAN NOT NULL DEFAULT TRUE,
    incluye_lavado_interior_humedo BOOLEAN NOT NULL DEFAULT FALSE,
    incluye_encerado BOOLEAN NOT NULL DEFAULT FALSE,
    incluye_detallado_completo BOOLEAN NOT NULL DEFAULT FALSE,
    incluye_servicio_domicilio BOOLEAN NOT NULL DEFAULT FALSE,
    incluye_mantenimiento_programado BOOLEAN NOT NULL DEFAULT FALSE,
    incluye_reporte_mensual BOOLEAN NOT NULL DEFAULT FALSE,
    incluye_soporte_24_7 BOOLEAN NOT NULL DEFAULT FALSE,
    INDEX idx_plan_empresarial_tipo (tipo),
    INDEX idx_plan_empresarial_activo (activo)
);

-- Tabla intermedia: lavado_auto_planempresarial_servicios_incluidos
CREATE TABLE lavado_auto_planempresarial_servicios_incluidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    planempresarial_id INT NOT NULL,
    servicio_id INT NOT NULL,
    FOREIGN KEY (planempresarial_id) REFERENCES lavado_auto_planempresarial(id_plan) ON DELETE CASCADE,
    FOREIGN KEY (servicio_id) REFERENCES lavado_auto_servicio(id_servicio) ON DELETE CASCADE,
    UNIQUE KEY unique_plan_empresarial_servicio (planempresarial_id, servicio_id)
);

-- Tabla: lavado_auto_suscripcionusuario (SuscripcionUsuario)
CREATE TABLE lavado_auto_suscripcionusuario (
    id_suscripcion INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    plan_id INT NOT NULL,
    fecha_inicio DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    fecha_fin DATETIME(6) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'activa',
    servicios_utilizados_mes INT NOT NULL DEFAULT 0,
    ultimo_reinicio_contador DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    auto_renovar BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (usuario_id) REFERENCES lavado_auto_usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES lavado_auto_plan(id_plan) ON DELETE CASCADE,
    INDEX idx_suscripcion_usuario (usuario_id),
    INDEX idx_suscripcion_estado (estado)
);

-- Tabla: lavado_auto_suscripcionempresarial (SuscripcionEmpresarial)
CREATE TABLE lavado_auto_suscripcionempresarial (
    id_suscripcion INT AUTO_INCREMENT PRIMARY KEY,
    empresa_id INT NOT NULL,
    plan_id INT NOT NULL,
    cantidad_vehiculos INT NOT NULL,
    fecha_inicio DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    fecha_fin DATETIME(6) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'activa',
    servicios_utilizados_mes INT NOT NULL DEFAULT 0,
    ultimo_reinicio_contador DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    auto_renovar BOOLEAN NOT NULL DEFAULT TRUE,
    precio_mensual_actual DECIMAL(12, 2) NOT NULL,
    contacto_responsable VARCHAR(255) NOT NULL,
    telefono_contacto VARCHAR(15) NOT NULL,
    notas_especiales TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (empresa_id) REFERENCES lavado_auto_empresa(id_empresa) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES lavado_auto_planempresarial(id_plan) ON DELETE CASCADE,
    INDEX idx_suscripcion_empresarial_empresa (empresa_id),
    INDEX idx_suscripcion_empresarial_estado (estado)
);

-- Tabla: lavado_auto_reserva (Reserva)
CREATE TABLE lavado_auto_reserva (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    empresa_id INT NOT NULL,
    usuario_id INT NOT NULL,
    suscripcion_utilizada_id INT NULL,
    es_pago_individual BOOLEAN NOT NULL DEFAULT FALSE,
    suscripcion_empresarial_id INT NULL,
    es_reserva_empresarial BOOLEAN NOT NULL DEFAULT FALSE,
    placa_vehiculo VARCHAR(20) NULL,
    tipo_vehiculo VARCHAR(50) NULL,
    conductor_asignado VARCHAR(255) NOT NULL DEFAULT '',
    observaciones_empresariales TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (empresa_id) REFERENCES lavado_auto_empresa(id_empresa) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES lavado_auto_usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (suscripcion_utilizada_id) REFERENCES lavado_auto_suscripcionusuario(id_suscripcion) ON DELETE SET NULL,
    FOREIGN KEY (suscripcion_empresarial_id) REFERENCES lavado_auto_suscripcionempresarial(id_suscripcion) ON DELETE SET NULL,
    INDEX idx_reserva_fecha (fecha),
    INDEX idx_reserva_estado (estado),
    INDEX idx_reserva_usuario (usuario_id),
    INDEX idx_reserva_empresa (empresa_id)
);

-- Tabla: lavado_auto_reservaservicio (ReservaServicio) - Tabla intermedia
CREATE TABLE lavado_auto_reservaservicio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reserva_id INT NOT NULL,
    servicio_id INT NOT NULL,
    precio_aplicado DECIMAL(10, 2) NULL,
    descuento_empresarial DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (reserva_id) REFERENCES lavado_auto_reserva(id_reserva) ON DELETE CASCADE,
    FOREIGN KEY (servicio_id) REFERENCES lavado_auto_servicio(id_servicio) ON DELETE CASCADE,
    UNIQUE KEY unique_reserva_servicio (reserva_id, servicio_id)
);

-- Tabla: lavado_auto_pago (Pago)
CREATE TABLE lavado_auto_pago (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    fecha_pago DATE NOT NULL,
    monto DOUBLE NOT NULL,
    metodo_pago VARCHAR(50) NOT NULL,
    reserva_id INT NOT NULL,
    usuario_id INT NOT NULL,
    FOREIGN KEY (reserva_id) REFERENCES lavado_auto_reserva(id_reserva) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES lavado_auto_usuario(id_usuario) ON DELETE CASCADE,
    INDEX idx_pago_fecha (fecha_pago),
    INDEX idx_pago_usuario (usuario_id)
);

-- Tabla: lavado_auto_pasareladepago (PasarelaDePago)
CREATE TABLE lavado_auto_pasareladepago (
    id_pasarela INT AUTO_INCREMENT PRIMARY KEY,
    nombre_pasarela VARCHAR(100) NOT NULL,
    estado_transaccion VARCHAR(50) NOT NULL,
    pago_id INT NOT NULL,
    FOREIGN KEY (pago_id) REFERENCES lavado_auto_pago(id_pago) ON DELETE CASCADE
);

-- Tabla: lavado_auto_historialpagosSuscripcion (HistorialPagosSuscripcion)
CREATE TABLE lavado_auto_historialpagosSuscripcion (
    id_pago_suscripcion INT AUTO_INCREMENT PRIMARY KEY,
    suscripcion_id INT NOT NULL,
    monto DECIMAL(10, 2) NOT NULL,
    fecha_pago DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    referencia_pago VARCHAR(255) NOT NULL UNIQUE,
    metodo_pago VARCHAR(50) NOT NULL,
    FOREIGN KEY (suscripcion_id) REFERENCES lavado_auto_suscripcionusuario(id_suscripcion) ON DELETE CASCADE,
    INDEX idx_pago_suscripcion_fecha (fecha_pago),
    INDEX idx_pago_suscripcion_estado (estado)
);

-- Tabla: lavado_auto_historialpagosSuscripcionempresarial (HistorialPagosSuscripcionEmpresarial)
CREATE TABLE lavado_auto_historialpagosSuscripcionempresarial (
    id_pago_suscripcion INT AUTO_INCREMENT PRIMARY KEY,
    suscripcion_id INT NOT NULL,
    monto DECIMAL(12, 2) NOT NULL,
    fecha_pago DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    referencia_pago VARCHAR(255) NOT NULL UNIQUE,
    metodo_pago VARCHAR(50) NOT NULL,
    periodo_facturado VARCHAR(20) NOT NULL,
    FOREIGN KEY (suscripcion_id) REFERENCES lavado_auto_suscripcionempresarial(id_suscripcion) ON DELETE CASCADE,
    INDEX idx_pago_suscripcion_emp_fecha (fecha_pago),
    INDEX idx_pago_suscripcion_emp_estado (estado)
);

-- Tabla: lavado_auto_mensajequeja (MensajeQueja - PQRS)
CREATE TABLE lavado_auto_mensajequeja (
    id_mensaje INT AUTO_INCREMENT PRIMARY KEY,
    tipo_pqrs VARCHAR(20) NOT NULL,
    urgencia VARCHAR(20) NOT NULL DEFAULT 'media',
    nombre_contacto VARCHAR(255) NULL,
    email_contacto VARCHAR(254) NULL,
    servicio_relacionado VARCHAR(100) NULL,
    servicio_bd_id INT NULL,
    contenido TEXT NOT NULL,
    fecha_envio DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    fecha_actualizacion DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    estado VARCHAR(20) NOT NULL DEFAULT 'recibido',
    respuesta TEXT NOT NULL DEFAULT '',
    fecha_respuesta DATETIME(6) NULL,
    usuario_id INT NULL,
    numero_radicado VARCHAR(20) NULL UNIQUE,
    acepto_terminos BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (servicio_bd_id) REFERENCES lavado_auto_servicio(id_servicio) ON DELETE SET NULL,
    FOREIGN KEY (usuario_id) REFERENCES lavado_auto_usuario(id_usuario) ON DELETE CASCADE,
    INDEX idx_pqrs_fecha (fecha_envio),
    INDEX idx_pqrs_estado (estado),
    INDEX idx_pqrs_tipo (tipo_pqrs)
);

-- Tabla: lavado_auto_comentario (Comentario)
CREATE TABLE lavado_auto_comentario (
    id_comentario INT AUTO_INCREMENT PRIMARY KEY,
    comentario TEXT NOT NULL,
    fecha DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    usuario_id INT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES lavado_auto_usuario(id_usuario) ON DELETE CASCADE,
    INDEX idx_comentario_fecha (fecha),
    INDEX idx_comentario_usuario (usuario_id)
);

-- Tabla: lavado_auto_detallereservaempresarial (DetalleReservaEmpresarial)
CREATE TABLE lavado_auto_detallereservaempresarial (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reserva_id INT NOT NULL UNIQUE,
    numero_interno_empresa VARCHAR(50) NOT NULL DEFAULT '',
    departamento_solicitante VARCHAR(100) NOT NULL DEFAULT '',
    centro_costo VARCHAR(50) NOT NULL DEFAULT '',
    kilometraje_actual INT NULL,
    proxima_revision DATE NULL,
    responsable_vehiculo VARCHAR(255) NOT NULL DEFAULT '',
    FOREIGN KEY (reserva_id) REFERENCES lavado_auto_reserva(id_reserva) ON DELETE CASCADE
);

-- Tabla: lavado_auto_solicitudservicioempresa (SolicitudServicioEmpresa)
CREATE TABLE lavado_auto_solicitudservicioempresa (
    id_solicitud INT AUTO_INCREMENT PRIMARY KEY,
    empresa_id INT NOT NULL,
    servicio_solicitado_id INT NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    fecha_solicitud DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    fecha_respuesta DATETIME(6) NULL,
    motivo_solicitud TEXT NOT NULL,
    respuesta_admin TEXT NOT NULL DEFAULT '',
    usuario_responsable VARCHAR(255) NOT NULL,
    telefono_contacto VARCHAR(15) NOT NULL,
    FOREIGN KEY (empresa_id) REFERENCES lavado_auto_empresa(id_empresa) ON DELETE CASCADE,
    FOREIGN KEY (servicio_solicitado_id) REFERENCES lavado_auto_servicio(id_servicio) ON DELETE CASCADE,
    UNIQUE KEY unique_empresa_servicio_estado (empresa_id, servicio_solicitado_id, estado),
    INDEX idx_solicitud_empresa (empresa_id),
    INDEX idx_solicitud_estado (estado)
);

-- Tabla: lavado_auto_solicitudcontactoplan (SolicitudContactoPlan)
CREATE TABLE lavado_auto_solicitudcontactoplan (
    id_solicitud INT AUTO_INCREMENT PRIMARY KEY,
    plan_id INT NOT NULL,
    nombre_completo VARCHAR(200) NOT NULL,
    email VARCHAR(254) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    empresa VARCHAR(200) NOT NULL,
    cargo VARCHAR(100) NOT NULL DEFAULT '',
    cantidad_vehiculos INT NOT NULL,
    mensaje_adicional TEXT NOT NULL DEFAULT '',
    fecha_solicitud DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    ip_solicitante INET6_ATON NULL,
    user_agent TEXT NOT NULL DEFAULT '',
    fecha_contacto DATETIME(6) NULL,
    notas_seguimiento TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (plan_id) REFERENCES lavado_auto_planempresarial(id_plan) ON DELETE CASCADE,
    INDEX idx_solicitud_contacto_fecha (fecha_solicitud),
    INDEX idx_solicitud_contacto_estado (estado)
);

-- Tabla para grupos de Django (necesaria para permisos)
CREATE TABLE auth_group (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
);

-- Tabla para permisos de Django
CREATE TABLE auth_permission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INT NOT NULL,
    codename VARCHAR(100) NOT NULL
);

-- Tabla para relación usuario-grupos de Django
CREATE TABLE lavado_auto_usuario_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    group_id INT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES lavado_auto_usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE,
    UNIQUE KEY unique_usuario_group (usuario_id, group_id)
);

-- Tabla para relación usuario-permisos de Django
CREATE TABLE lavado_auto_usuario_user_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    permission_id INT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES lavado_auto_usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE,
    UNIQUE KEY unique_usuario_permission (usuario_id, permission_id)
);

-- Insertar algunos datos de ejemplo

-- Servicios básicos
INSERT INTO lavado_auto_servicio (nombre_servicio, descripcion, precio) VALUES
('Lavado Básico', 'Lavado exterior del vehículo con agua y jabón', 15000),
('Lavado Premium', 'Lavado completo exterior e interior básico', 25000),
('Lavado Completo', 'Lavado completo con aspirado, limpieza de tapicería y encerado', 35000),
('Aspirado', 'Aspirado completo del interior del vehículo', 8000),
('Encerado', 'Aplicación de cera protectora en la carrocería', 12000),
('Limpieza de Tapicería', 'Limpieza profunda de asientos y tapicería', 18000),
('Lavado de Motor', 'Limpieza especializada del compartimiento del motor', 20000),
('Detallado Completo', 'Servicio completo de detallado interior y exterior', 50000);

-- Plan básico
INSERT INTO lavado_auto_plan (nombre, tipo, descripcion, precio_mensual, cantidad_servicios_mes) VALUES
('Plan Básico', 'basico', 'Plan básico con lavados mensuales', 45000.00, 3),
('Plan Premium', 'premium', 'Plan premium con servicios completos', 75000.00, 5),
('Plan Completo', 'completo', 'Plan completo con servicios ilimitados', 120000.00, 0);

-- Plan empresarial básico
INSERT INTO lavado_auto_planempresarial (nombre, tipo, descripcion, precio_mensual_por_vehiculo, vehiculos_minimos, servicios_por_vehiculo_mes) VALUES
('Plan Flota Básica', 'basico_flota', 'Plan básico para flotas de vehículos', 25000.00, 5, 2),
('Plan Flota Premium', 'premium_flota', 'Plan premium para flotas con servicios completos', 40000.00, 10, 4),
('Plan Corporativo', 'corporativo', 'Plan corporativo con servicios completos y soporte', 55000.00, 20, 0);

-- Usuario administrador (la contraseña debe ser hasheada en Django)
INSERT INTO lavado_auto_usuario (nombre_completo, nombre_usuario, correo, rol, is_staff, is_superuser, password) VALUES
('Administrador Sistema', 'admin', 'admin@autonew.com', 'admin', TRUE, TRUE, 'pbkdf2_sha256$390000$dummy$hash');

COMMIT;

-- Mensaje final
SELECT 'Base de datos AUTONEW creada exitosamente con todas las tablas y relaciones.' as Mensaje;