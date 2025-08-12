# 📋 DICCIONARIO DE DATOS - SISTEMA AUTONEW
**Base de datos:** autonew_django  
**Fecha:** 11 de agosto de 2025  
**Versión:** 1.0  

---

## 📊 ÍNDICE DE TABLAS

1. [lavado_auto_usuario](#1-lavado_auto_usuario)
2. [lavado_auto_servicio](#2-lavado_auto_servicio)
3. [lavado_auto_empresa](#3-lavado_auto_empresa)
4. [lavado_auto_empresaservicio](#4-lavado_auto_empresaservicio)
5. [lavado_auto_plan](#5-lavado_auto_plan)
6. [lavado_auto_plan_servicios_incluidos](#6-lavado_auto_plan_servicios_incluidos)
7. [lavado_auto_planempresarial](#7-lavado_auto_planempresarial)
8. [lavado_auto_planempresarial_servicios_incluidos](#8-lavado_auto_planempresarial_servicios_incluidos)
9. [lavado_auto_suscripcionusuario](#9-lavado_auto_suscripcionusuario)
10. [lavado_auto_suscripcionempresarial](#10-lavado_auto_suscripcionempresarial)
11. [lavado_auto_reserva](#11-lavado_auto_reserva)
12. [lavado_auto_reservaservicio](#12-lavado_auto_reservaservicio)
13. [lavado_auto_pago](#13-lavado_auto_pago)
14. [lavado_auto_pasareladepago](#14-lavado_auto_pasareladepago)
15. [lavado_auto_historialpagossuscripcion](#15-lavado_auto_historialpagossuscripcion)
16. [lavado_auto_historialpagossuscripcionempresarial](#16-lavado_auto_historialpagossuscripcionempresarial)
17. [lavado_auto_mensajequeja](#17-lavado_auto_mensajequeja)
18. [lavado_auto_comentario](#18-lavado_auto_comentario)
19. [lavado_auto_detallereservaempresarial](#19-lavado_auto_detallereservaempresarial)
20. [lavado_auto_solicitudservicioempresa](#20-lavado_auto_solicitudservicioempresa)

---

## 1. `lavado_auto_usuario`
**Descripción:** Tabla principal para el sistema de autenticación personalizado de usuarios del sistema.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id_usuario` | INT | NO | PK | AUTO_INCREMENT | **Identificador único del usuario.** Clave primaria autoincremental que identifica de forma única a cada usuario en el sistema. |
| `nombre_completo` | VARCHAR(255) | NO | - | - | **Nombre completo del usuario.** Incluye nombres y apellidos completos del usuario registrado. Máximo 255 caracteres. |
| `nombre_usuario` | VARCHAR(20) | NO | UNIQUE | - | **Nombre de usuario único.** Username utilizado para el login. Debe ser único en todo el sistema. Máximo 20 caracteres alfanuméricos. |
| `profile_picture` | VARCHAR(100) | SÍ | - | NULL | **Ruta de la foto de perfil.** Almacena la ruta relativa al archivo de imagen del perfil del usuario. Opcional. |
| `correo` | VARCHAR(254) | NO | UNIQUE | - | **Dirección de correo electrónico.** Email único del usuario, utilizado para login alternativo y comunicaciones. Debe ser válido según RFC 5322. |
| `telefono` | VARCHAR(15) | SÍ | - | '' | **Número de teléfono.** Teléfono de contacto del usuario. Formato libre, máximo 15 caracteres. Opcional. |
| `direccion` | VARCHAR(255) | SÍ | - | '' | **Dirección física del usuario.** Dirección completa de residencia o trabajo. Máximo 255 caracteres. Opcional. |
| `password` | VARCHAR(128) | NO | - | - | **Contraseña encriptada.** Hash de la contraseña del usuario generado por Django (PBKDF2). Nunca se almacena en texto plano. |
| `token_reset` | VARCHAR(255) | SÍ | - | NULL | **Token para recuperación de contraseña.** Token temporal único generado para procesos de recuperación de contraseña. Se elimina tras su uso. |
| `rol` | VARCHAR(50) | NO | - | 'cliente' | **Rol del usuario en el sistema.** Define los permisos: 'cliente' (usuario normal) o 'admin' (administrador con permisos especiales). |
| `is_active` | BOOLEAN | NO | - | TRUE | **Estado de activación de la cuenta.** Indica si el usuario puede acceder al sistema. FALSE = cuenta deshabilitada. |
| `is_staff` | BOOLEAN | NO | - | FALSE | **Acceso al panel de administración.** Determina si el usuario puede acceder al admin de Django. TRUE solo para administradores. |
| `is_superuser` | BOOLEAN | NO | - | FALSE | **Permisos de superusuario.** Otorga todos los permisos en el sistema. TRUE solo para administradores principales. |
| `fecha_registro` | DATETIME | NO | - | CURRENT_TIMESTAMP | **Fecha y hora de registro.** Timestamp automático de cuando se creó la cuenta del usuario. No modificable. |
| `last_login` | DATETIME | SÍ | - | NULL | **Último inicio de sesión.** Timestamp del último login exitoso del usuario. NULL si nunca ha iniciado sesión. |

**Índices:**
- `idx_usuario_nombre`: Índice en `nombre_usuario` para optimizar búsquedas de login
- `idx_usuario_correo`: Índice en `correo` para optimizar búsquedas por email
- `idx_usuario_rol`: Índice en `rol` para filtros por tipo de usuario

---

## 2. `lavado_auto_servicio`
**Descripción:** Catálogo de servicios de lavado disponibles en el sistema.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id_servicio` | INT | NO | PK | AUTO_INCREMENT | **Identificador único del servicio.** Clave primaria autoincremental para cada servicio disponible. |
| `nombre_servicio` | VARCHAR(255) | NO | UNIQUE | - | **Nombre del servicio.** Denominación comercial del servicio (ej: "Lavado Premium"). Debe ser único en el catálogo. |
| `descripcion` | TEXT | NO | - | - | **Descripción detallada del servicio.** Explicación completa de qué incluye el servicio, procedimientos y beneficios. Sin límite de caracteres. |
| `precio` | FLOAT | NO | - | - | **Precio base del servicio.** Tarifa estándar en moneda local. Los descuentos empresariales se aplican por separado. |

**Índices:**
- `idx_servicio_nombre`: Índice en `nombre_servicio` para búsquedas rápidas

---

## 3. `lavado_auto_empresa`
**Descripción:** Registro de empresas clientes que utilizan servicios empresariales.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id_empresa` | INT | NO | PK | AUTO_INCREMENT | **Identificador único de la empresa.** Clave primaria autoincremental para cada empresa registrada. |
| `nombre_empresa` | VARCHAR(100) | NO | - | - | **Razón social de la empresa.** Nombre legal o comercial de la empresa cliente. Máximo 100 caracteres. |
| `direccion` | VARCHAR(255) | NO | - | - | **Dirección fiscal de la empresa.** Dirección completa de la sede principal o fiscal. Requerida para facturación. |
| `telefono` | VARCHAR(15) | NO | - | - | **Teléfono principal de contacto.** Número principal para comunicaciones comerciales. Máximo 15 caracteres. |
| `email` | VARCHAR(254) | NO | - | - | **Correo electrónico corporativo.** Email principal para comunicaciones oficiales y facturación electrónica. |
| `contrasena` | VARCHAR(255) | NO | - | 'temp_password' | **Contraseña temporal de acceso.** Contraseña inicial asignada. Debe cambiarse en el primer acceso. |
| `fecha_registro` | DATETIME | NO | - | CURRENT_TIMESTAMP | **Fecha de registro en el sistema.** Timestamp automático de cuando se registró la empresa. |
| `verificada` | BOOLEAN | NO | - | FALSE | **Estado de verificación de la empresa.** TRUE = empresa verificada por administración, puede usar servicios. FALSE = pendiente de verificación. |

**Índices:**
- `idx_empresa_nombre`: Índice en `nombre_empresa` para búsquedas
- `idx_empresa_verificada`: Índice en `verificada` para filtrar empresas activas

---

## 4. `lavado_auto_empresaservicio`
**Descripción:** Tabla intermedia que relaciona empresas con los servicios que tienen contratados.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id` | INT | NO | PK | AUTO_INCREMENT | **Identificador único de la relación.** Clave primaria autoincremental para cada asignación empresa-servicio. |
| `empresa_id` | INT | NO | FK | - | **Referencia a la empresa.** Clave foránea que apunta al `id_empresa` en la tabla `lavado_auto_empresa`. |
| `servicio_id` | INT | NO | FK | - | **Referencia al servicio.** Clave foránea que apunta al `id_servicio` en la tabla `lavado_auto_servicio`. |

**Restricciones:**
- `unique_empresa_servicio`: Única combinación empresa-servicio (evita duplicados)
- Eliminación en cascada cuando se elimina empresa o servicio

---

## 5. `lavado_auto_plan`
**Descripción:** Planes de suscripción para usuarios individuales.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id_plan` | INT | NO | PK | AUTO_INCREMENT | **Identificador único del plan.** Clave primaria autoincremental para cada plan de suscripción individual. |
| `nombre` | VARCHAR(100) | NO | - | - | **Nombre comercial del plan.** Denominación marketing del plan (ej: "Plan Premium Individual"). |
| `tipo` | VARCHAR(20) | NO | - | - | **Tipo de plan.** Categoría: 'basico', 'premium', 'completo'. Define el nivel de servicios incluidos. |
| `descripcion` | TEXT | NO | - | - | **Descripción completa del plan.** Detalle de beneficios, servicios incluidos y características especiales. |
| `precio_mensual` | DECIMAL(10,2) | NO | - | - | **Precio mensual del plan.** Costo de suscripción mensual en moneda local. Formato: 99999999.99 |
| `cantidad_servicios_mes` | INT | NO | - | - | **Servicios permitidos por mes.** Número de servicios que incluye el plan. 0 = ilimitados. |
| `activo` | BOOLEAN | NO | - | TRUE | **Estado del plan.** TRUE = disponible para nuevas suscripciones. FALSE = descontinuado. |
| `fecha_creacion` | DATETIME | NO | - | CURRENT_TIMESTAMP | **Fecha de creación del plan.** Timestamp de cuando se creó el plan en el sistema. |
| `incluye_lavado_asientos` | BOOLEAN | NO | - | TRUE | **Incluye limpieza de asientos.** TRUE = el plan incluye aspirado y limpieza de asientos. |
| `incluye_aspirado` | BOOLEAN | NO | - | TRUE | **Incluye aspirado interior.** TRUE = el plan incluye aspirado completo del habitáculo. |
| `incluye_lavado_exterior` | BOOLEAN | NO | - | TRUE | **Incluye lavado exterior.** TRUE = el plan incluye lavado completo de carrocería. |
| `incluye_lavado_interior_humedo` | BOOLEAN | NO | - | FALSE | **Incluye limpieza húmeda interior.** TRUE = incluye limpieza con productos específicos del interior. |
| `incluye_encerado` | BOOLEAN | NO | - | FALSE | **Incluye aplicación de cera.** TRUE = incluye encerado y pulido de la carrocería. |
| `incluye_detallado_completo` | BOOLEAN | NO | - | FALSE | **Incluye detallado profesional.** TRUE = incluye detallado completo con productos premium. |

**Índices:**
- `idx_plan_tipo`: Índice en `tipo` para filtros por categoría
- `idx_plan_activo`: Índice en `activo` para mostrar solo planes disponibles

---

## 6. `lavado_auto_plan_servicios_incluidos`
**Descripción:** Tabla intermedia que relaciona planes individuales con servicios específicos incluidos.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id` | INT | NO | PK | AUTO_INCREMENT | **Identificador único de la relación.** Clave primaria autoincremental para cada asignación plan-servicio. |
| `plan_id` | INT | NO | FK | - | **Referencia al plan individual.** Clave foránea que apunta al `id_plan` en la tabla `lavado_auto_plan`. |
| `servicio_id` | INT | NO | FK | - | **Referencia al servicio incluido.** Clave foránea que apunta al `id_servicio` en la tabla `lavado_auto_servicio`. |

**Restricciones:**
- `unique_plan_servicio`: Única combinación plan-servicio
- Eliminación en cascada cuando se elimina plan o servicio

---

## 7. `lavado_auto_planempresarial`
**Descripción:** Planes de suscripción diseñados específicamente para empresas con flotas vehiculares.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id_plan` | INT | NO | PK | AUTO_INCREMENT | **Identificador único del plan empresarial.** Clave primaria autoincremental para cada plan empresarial. |
| `nombre` | VARCHAR(100) | NO | - | - | **Nombre comercial del plan empresarial.** Denominación específica para el mercado B2B. |
| `tipo` | VARCHAR(30) | NO | - | - | **Tipo de plan empresarial.** Categorías: 'basico_flota', 'premium_flota', 'corporativo', 'transporte_publico'. |
| `descripcion` | TEXT | NO | - | - | **Descripción del plan empresarial.** Detalle completo de beneficios, servicios y características para empresas. |
| `precio_mensual_por_vehiculo` | DECIMAL(10,2) | NO | - | - | **Precio por vehículo al mes.** Tarifa mensual por cada vehículo incluido en la flota. |
| `precio_base_mensual` | DECIMAL(10,2) | NO | - | 0 | **Precio base fijo mensual.** Costo fijo mensual independiente del número de vehículos. |
| `vehiculos_minimos` | INT | NO | - | 5 | **Mínimo de vehículos requeridos.** Cantidad mínima de vehículos para contratar este plan. |
| `vehiculos_maximos` | INT | SÍ | - | NULL | **Máximo de vehículos permitidos.** Límite superior de vehículos. NULL = sin límite. |
| `servicios_por_vehiculo_mes` | INT | NO | - | - | **Servicios por vehículo mensual.** Cantidad de servicios permitidos por vehículo cada mes. 0 = ilimitados. |
| `descuento_volumen` | DECIMAL(5,2) | NO | - | 0 | **Descuento por volumen (%).** Porcentaje de descuento aplicado por contratar grandes flotas. |
| `activo` | BOOLEAN | NO | - | TRUE | **Estado del plan empresarial.** TRUE = disponible para contratación. FALSE = descontinuado. |
| `fecha_creacion` | DATETIME | NO | - | CURRENT_TIMESTAMP | **Fecha de creación del plan.** Timestamp de cuando se creó el plan empresarial. |
| `incluye_lavado_asientos` | BOOLEAN | NO | - | TRUE | **Incluye limpieza de asientos.** Específico para vehículos empresariales con mayor uso. |
| `incluye_aspirado` | BOOLEAN | NO | - | TRUE | **Incluye aspirado completo.** Aspirado profesional para vehículos de trabajo. |
| `incluye_lavado_exterior` | BOOLEAN | NO | - | TRUE | **Incluye lavado exterior completo.** Mantenimiento de imagen corporativa del vehículo. |
| `incluye_lavado_interior_humedo` | BOOLEAN | NO | - | FALSE | **Incluye limpieza húmeda interior.** Desinfección y limpieza profunda para vehículos compartidos. |
| `incluye_encerado` | BOOLEAN | NO | - | FALSE | **Incluye encerado profesional.** Protección adicional para vehículos de representación. |
| `incluye_detallado_completo` | BOOLEAN | NO | - | FALSE | **Incluye detallado completo.** Servicio premium para vehículos ejecutivos. |
| `incluye_servicio_domicilio` | BOOLEAN | NO | - | FALSE | **Incluye servicio a domicilio.** Recogida y entrega en las instalaciones de la empresa. |
| `incluye_mantenimiento_programado` | BOOLEAN | NO | - | FALSE | **Incluye mantenimiento programado.** Calendario automático de servicios preventivos. |
| `incluye_reporte_mensual` | BOOLEAN | NO | - | FALSE | **Incluye reportes mensuales.** Informes detallados de servicios realizados y estado de flota. |
| `incluye_soporte_24_7` | BOOLEAN | NO | - | FALSE | **Incluye soporte 24/7.** Atención al cliente especializada las 24 horas. |

**Índices:**
- `idx_plan_empresarial_tipo`: Índice en `tipo` para categorización
- `idx_plan_empresarial_activo`: Índice en `activo` para planes disponibles

---

## 8. `lavado_auto_planempresarial_servicios_incluidos`
**Descripción:** Tabla intermedia que relaciona planes empresariales con servicios específicos.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id` | INT | NO | PK | AUTO_INCREMENT | **Identificador único de la relación.** Clave primaria para cada asignación plan empresarial-servicio. |
| `planempresarial_id` | INT | NO | FK | - | **Referencia al plan empresarial.** Clave foránea que apunta al `id_plan` en `lavado_auto_planempresarial`. |
| `servicio_id` | INT | NO | FK | - | **Referencia al servicio incluido.** Clave foránea que apunta al `id_servicio` en `lavado_auto_servicio`. |

---

## 9. `lavado_auto_suscripcionusuario`
**Descripción:** Suscripciones activas de usuarios individuales a planes de servicio.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id_suscripcion` | INT | NO | PK | AUTO_INCREMENT | **Identificador único de la suscripción.** Clave primaria autoincremental para cada suscripción individual. |
| `usuario_id` | INT | NO | FK | - | **Referencia al usuario suscrito.** Clave foránea que apunta al `id_usuario` en `lavado_auto_usuario`. |
| `plan_id` | INT | NO | FK | - | **Referencia al plan contratado.** Clave foránea que apunta al `id_plan` en `lavado_auto_plan`. |
| `fecha_inicio` | DATETIME | NO | - | CURRENT_TIMESTAMP | **Fecha de inicio de suscripción.** Timestamp de cuando comenzó la vigencia del plan. |
| `fecha_fin` | DATETIME | NO | - | - | **Fecha de vencimiento.** Timestamp de cuando expira la suscripción. Se calcula automáticamente (+30 días). |
| `estado` | VARCHAR(20) | NO | - | 'activa' | **Estado de la suscripción.** Valores: 'activa', 'pausada', 'cancelada', 'vencida'. |
| `servicios_utilizados_mes` | INT | NO | - | 0 | **Servicios consumidos este mes.** Contador de servicios utilizados en el período actual. Se reinicia mensualmente. |
| `ultimo_reinicio_contador` | DATETIME | NO | - | CURRENT_TIMESTAMP | **Última fecha de reinicio del contador.** Timestamp del último reinicio mensual del contador de servicios. |
| `auto_renovar` | BOOLEAN | NO | - | TRUE | **Renovación automática.** TRUE = se renueva automáticamente al vencer. FALSE = se debe renovar manualmente. |

**Índices:**
- `idx_suscripcion_estado`: Índice en `estado` para filtros de estado
- `idx_suscripcion_fecha_fin`: Índice en `fecha_fin` para verificar vencimientos

---

## 10. `lavado_auto_suscripcionempresarial`
**Descripción:** Suscripciones empresariales para gestión de flotas vehiculares.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id_suscripcion` | INT | NO | PK | AUTO_INCREMENT | **Identificador único de suscripción empresarial.** Clave primaria para cada suscripción empresarial. |
| `empresa_id` | INT | NO | FK | - | **Referencia a la empresa suscrita.** Clave foránea que apunta al `id_empresa` en `lavado_auto_empresa`. |
| `plan_id` | INT | NO | FK | - | **Referencia al plan empresarial.** Clave foránea que apunta al `id_plan` en `lavado_auto_planempresarial`. |
| `cantidad_vehiculos` | INT | NO | - | - | **Número de vehículos en la flota.** Cantidad total de vehículos cubiertos por la suscripción. |
| `fecha_inicio` | DATETIME | NO | - | CURRENT_TIMESTAMP | **Fecha de inicio de suscripción.** Timestamp de cuando comenzó la vigencia del plan empresarial. |
| `fecha_fin` | DATETIME | NO | - | - | **Fecha de vencimiento.** Timestamp de cuando expira la suscripción empresarial. |
| `estado` | VARCHAR(20) | NO | - | 'activa' | **Estado de la suscripción.** Valores: 'activa', 'pausada', 'cancelada', 'vencida'. |
| `servicios_utilizados_mes` | INT | NO | - | 0 | **Servicios consumidos este mes.** Contador total de servicios utilizados por toda la flota en el período. |
| `ultimo_reinicio_contador` | DATETIME | NO | - | CURRENT_TIMESTAMP | **Última fecha de reinicio del contador.** Timestamp del último reinicio mensual del contador. |
| `auto_renovar` | BOOLEAN | NO | - | TRUE | **Renovación automática.** TRUE = renovación automática al vencer. FALSE = renovación manual. |
| `precio_mensual_actual` | DECIMAL(12,2) | NO | - | - | **Precio mensual calculado.** Monto total mensual basado en la cantidad de vehículos y descuentos aplicados. |
| `contacto_responsable` | VARCHAR(255) | NO | - | - | **Responsable de la cuenta.** Nombre de la persona encargada de la gestión de la flota en la empresa. |
| `telefono_contacto` | VARCHAR(15) | NO | - | - | **Teléfono del responsable.** Número directo del responsable para coordinaciones operativas. |
| `notas_especiales` | TEXT | SÍ | - | '' | **Notas y observaciones especiales.** Información adicional sobre requisitos especiales o acuerdos particulares. |

**Índices:**
- `idx_suscripcion_empresarial_estado`: Índice en `estado`
- `idx_suscripcion_empresarial_fecha_fin`: Índice en `fecha_fin`

---

## 11. `lavado_auto_reserva`
**Descripción:** Tabla central para el registro de todas las reservas de servicios, tanto individuales como empresariales.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id_reserva` | INT | NO | PK | AUTO_INCREMENT | **Identificador único de la reserva.** Clave primaria autoincremental para cada reserva del sistema. |
| `fecha` | DATE | NO | - | - | **Fecha programada del servicio.** Día en que se realizará el servicio de lavado. |
| `hora` | TIME | NO | - | - | **Hora programada del servicio.** Hora específica de inicio del servicio. |
| `estado` | VARCHAR(20) | NO | - | 'pendiente' | **Estado actual de la reserva.** Valores: 'pendiente', 'completado', 'cancelada'. |
| `empresa_id` | INT | NO | FK | - | **Empresa que realizará el servicio.** Clave foránea que apunta al `id_empresa` en `lavado_auto_empresa`. |
| `usuario_id` | INT | NO | FK | - | **Usuario que realizó la reserva.** Clave foránea que apunta al `id_usuario` en `lavado_auto_usuario`. |
| `suscripcion_utilizada_id` | INT | SÍ | FK | NULL | **Suscripción individual utilizada.** Referencia a la suscripción individual si aplica. NULL para pagos individuales. |
| `es_pago_individual` | BOOLEAN | NO | - | FALSE | **Indica si es pago por servicio.** TRUE = pago individual sin suscripción. FALSE = usa suscripción. |
| `suscripcion_empresarial_id` | INT | SÍ | FK | NULL | **Suscripción empresarial utilizada.** Referencia a la suscripción empresarial si aplica. |
| `es_reserva_empresarial` | BOOLEAN | NO | - | FALSE | **Indica si es reserva empresarial.** TRUE = reserva de flota empresarial. FALSE = reserva individual. |
| `placa_vehiculo` | VARCHAR(20) | SÍ | - | NULL | **Placa del vehículo a lavar.** Identificación del vehículo para reservas empresariales. |
| `tipo_vehiculo` | VARCHAR(50) | SÍ | - | NULL | **Tipo de vehículo.** Categoría: 'sedan', 'suv', 'camioneta', 'bus', 'microbus', 'camion', 'taxi', 'moto'. |
| `conductor_asignado` | VARCHAR(255) | SÍ | - | '' | **Conductor responsable.** Nombre del conductor del vehículo para reservas empresariales. |
| `observaciones_empresariales` | TEXT | SÍ | - | '' | **Observaciones especiales.** Notas adicionales para el servicio empresarial (daños existentes, urgencia, etc.). |

**Índices:**
- `idx_reserva_fecha`: Índice en `fecha` para búsquedas por día
- `idx_reserva_estado`: Índice en `estado` para filtros de estado
- `idx_reserva_placa`: Índice en `placa_vehiculo` para búsquedas vehiculares

---

## 12. `lavado_auto_reservaservicio`
**Descripción:** Tabla intermedia que relaciona reservas con servicios específicos solicitados.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id` | INT | NO | PK | AUTO_INCREMENT | **Identificador único de la relación.** Clave primaria para cada asignación reserva-servicio. |
| `reserva_id` | INT | NO | FK | - | **Referencia a la reserva.** Clave foránea que apunta al `id_reserva` en `lavado_auto_reserva`. |
| `servicio_id` | INT | NO | FK | - | **Referencia al servicio solicitado.** Clave foránea que apunta al `id_servicio` en `lavado_auto_servicio`. |
| `precio_aplicado` | DECIMAL(10,2) | SÍ | - | NULL | **Precio específico aplicado.** Precio final cobrado, puede incluir descuentos empresariales o promociones. |
| `descuento_empresarial` | DECIMAL(5,2) | NO | - | 0 | **Descuento empresarial aplicado (%).** Porcentaje de descuento aplicado por ser cliente empresarial. |

**Restricciones:**
- `unique_reserva_servicio`: Única combinación reserva-servicio

---

## 13. `lavado_auto_pago`
**Descripción:** Registro de todos los pagos realizados por servicios individuales.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id_pago` | INT | NO | PK | AUTO_INCREMENT | **Identificador único del pago.** Clave primaria autoincremental para cada transacción de pago. |
| `fecha_pago` | DATE | NO | - | AUTO_ADD | **Fecha del pago.** Día en que se procesó el pago. Se asigna automáticamente. |
| `monto` | FLOAT | NO | - | - | **Monto total pagado.** Cantidad total abonada por los servicios de la reserva. |
| `metodo_pago` | VARCHAR(50) | NO | - | - | **Método de pago utilizado.** Forma de pago: 'efectivo', 'tarjeta', 'transferencia', 'billetera_digital', etc. |
| `reserva_id` | INT | NO | FK | - | **Referencia a la reserva pagada.** Clave foránea que apunta al `id_reserva` en `lavado_auto_reserva`. |
| `usuario_id` | INT | NO | FK | - | **Usuario que realizó el pago.** Clave foránea que apunta al `id_usuario` en `lavado_auto_usuario`. |

**Índices:**
- `idx_pago_fecha`: Índice en `fecha_pago` para reportes financieros

---

## 14. `lavado_auto_pasareladepago`
**Descripción:** Información de transacciones procesadas a través de pasarelas de pago externas.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id_pasarela` | INT | NO | PK | AUTO_INCREMENT | **Identificador único de transacción.** Clave primaria para cada transacción de pasarela externa. |
| `nombre_pasarela` | VARCHAR(100) | NO | - | - | **Nombre de la pasarela de pago.** Identificación del proveedor: 'PayPal', 'Stripe', 'MercadoPago', etc. |
| `estado_transaccion` | VARCHAR(50) | NO | - | - | **Estado de la transacción.** Estado reportado por la pasarela: 'approved', 'pending', 'rejected', 'refunded'. |
| `pago_id` | INT | NO | FK | - | **Referencia al pago asociado.** Clave foránea que apunta al `id_pago` en `lavado_auto_pago`. |

---

## 15. `lavado_auto_historialpagossuscripcion`
**Descripción:** Historial completo de pagos de suscripciones individuales.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id_pago_suscripcion` | INT | NO | PK | AUTO_INCREMENT | **Identificador único del pago de suscripción.** Clave primaria para cada pago de suscripción individual. |
| `suscripcion_id` | INT | NO | FK | - | **Referencia a la suscripción.** Clave foránea que apunta al `id_suscripcion` en `lavado_auto_suscripcionusuario`. |
| `monto` | DECIMAL(10,2) | NO | - | - | **Monto del pago de suscripción.** Cantidad abonada por el período de suscripción. |
| `fecha_pago` | DATETIME | NO | - | CURRENT_TIMESTAMP | **Fecha y hora del pago.** Timestamp exacto de cuando se procesó el pago. |
| `estado` | VARCHAR(20) | NO | - | 'pendiente' | **Estado del pago.** Valores: 'pendiente', 'aprobado', 'rechazado', 'reembolsado'. |
| `referencia_pago` | VARCHAR(255) | NO | UNIQUE | - | **Referencia única del pago.** Código único generado para identificar y rastrear el pago. |
| `metodo_pago` | VARCHAR(50) | NO | - | - | **Método de pago utilizado.** Forma de pago para la suscripción. |

**Índices:**
- `idx_historial_pago_estado`: Índice en `estado`
- `idx_historial_pago_fecha`: Índice en `fecha_pago`

---

## 16. `lavado_auto_historialpagossuscripcionempresarial`
**Descripción:** Historial de pagos para suscripciones empresariales con mayor volumen.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id_pago_suscripcion` | INT | NO | PK | AUTO_INCREMENT | **Identificador único del pago empresarial.** Clave primaria para cada pago de suscripción empresarial. |
| `suscripcion_id` | INT | NO | FK | - | **Referencia a la suscripción empresarial.** Clave foránea que apunta al `id_suscripcion` en `lavado_auto_suscripcionempresarial`. |
| `monto` | DECIMAL(12,2) | NO | - | - | **Monto del pago empresarial.** Cantidad total facturada (mayor precisión para montos corporativos). |
| `fecha_pago` | DATETIME | NO | - | CURRENT_TIMESTAMP | **Fecha y hora del pago.** Timestamp exacto del procesamiento del pago empresarial. |
| `estado` | VARCHAR(20) | NO | - | 'pendiente' | **Estado del pago empresarial.** Valores: 'pendiente', 'aprobado', 'rechazado', 'reembolsado'. |
| `referencia_pago` | VARCHAR(255) | NO | UNIQUE | - | **Referencia única empresarial.** Código único para facturación y seguimiento empresarial. |
| `metodo_pago` | VARCHAR(50) | NO | - | - | **Método de pago empresarial.** Forma de pago corporativa (transferencia, cheque, etc.). |
| `periodo_facturado` | VARCHAR(20) | NO | - | - | **Período facturado.** Identificación del período: '2024-01', '2024-02', etc. |

**Índices:**
- `idx_historial_pago_empresarial_estado`: Índice en `estado`
- `idx_historial_pago_empresarial_fecha`: Índice en `fecha_pago`

---

## 17. `lavado_auto_mensajequeja`
**Descripción:** Sistema de mensajería y gestión de quejas de usuarios.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id_mensaje` | INT | NO | PK | AUTO_INCREMENT | **Identificador único del mensaje.** Clave primaria autoincremental para cada mensaje o queja. |
| `contenido` | TEXT | NO | - | - | **Contenido del mensaje o queja.** Texto completo del mensaje enviado por el usuario. Sin límite de caracteres. |
| `fecha_envio` | DATE | NO | - | AUTO_ADD | **Fecha de envío.** Día en que el usuario envió el mensaje. Se asigna automáticamente. |
| `estado` | VARCHAR(50) | NO | - | 'no respondido' | **Estado del mensaje.** Valores: 'no respondido', 'en proceso', 'respondido', 'cerrado'. |
| `respuesta` | TEXT | SÍ | - | '' | **Respuesta del administrador.** Texto de respuesta oficial del equipo de atención al cliente. |
| `usuario_id` | INT | NO | FK | - | **Usuario que envió el mensaje.** Clave foránea que apunta al `id_usuario` en `lavado_auto_usuario`. |

**Índices:**
- `idx_mensaje_estado`: Índice en `estado` para gestión de cola de atención
- `idx_mensaje_fecha`: Índice en `fecha_envio` para orden cronológico

---

## 18. `lavado_auto_comentario`
**Descripción:** Comentarios y reseñas de usuarios sobre servicios recibidos.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id_comentario` | INT | NO | PK | AUTO_INCREMENT | **Identificador único del comentario.** Clave primaria autoincremental para cada comentario. |
| `comentario` | TEXT | NO | - | - | **Texto del comentario.** Reseña o comentario completo del usuario sobre el servicio. |
| `fecha` | DATETIME | NO | - | CURRENT_TIMESTAMP | **Fecha y hora del comentario.** Timestamp exacto de cuando se publicó el comentario. |
| `usuario_id` | INT | NO | FK | - | **Usuario que hizo el comentario.** Clave foránea que apunta al `id_usuario` en `lavado_auto_usuario`. |

**Índices:**
- `idx_comentario_fecha`: Índice en `fecha` para orden cronológico

---

## 19. `lavado_auto_detallereservaempresarial`
**Descripción:** Detalles adicionales específicos para reservas de flotas empresariales.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id` | INT | NO | PK | AUTO_INCREMENT | **Identificador único del detalle.** Clave primaria autoincremental para cada detalle empresarial. |
| `reserva_id` | INT | NO | FK,UNIQUE | - | **Referencia única a la reserva.** Clave foránea única que apunta al `id_reserva` en `lavado_auto_reserva`. |
| `numero_interno_empresa` | VARCHAR(50) | SÍ | - | '' | **Número interno del vehículo.** Código interno que la empresa asigna al vehículo para control. |
| `departamento_solicitante` | VARCHAR(100) | SÍ | - | '' | **Departamento que solicita.** Área o departamento de la empresa que solicita el servicio. |
| `centro_costo` | VARCHAR(50) | SÍ | - | '' | **Centro de costo contable.** Código contable al que se imputa el gasto del servicio. |
| `kilometraje_actual` | INT | SÍ | - | NULL | **Kilometraje del vehículo.** Odómetro actual del vehículo al momento del servicio. |
| `proxima_revision` | DATE | SÍ | - | NULL | **Fecha de próxima revisión.** Programación de próximo mantenimiento preventivo. |
| `responsable_vehiculo` | VARCHAR(255) | SÍ | - | '' | **Responsable del vehículo.** Empleado asignado como responsable del vehículo. |

---

## 20. `lavado_auto_solicitudservicioempresa`
**Descripción:** Gestión de solicitudes de empresas para agregar nuevos servicios a su contrato.

| Campo | Tipo | Nulo | Clave | Default | Descripción |
|-------|------|------|-------|---------|-------------|
| `id_solicitud` | INT | NO | PK | AUTO_INCREMENT | **Identificador único de la solicitud.** Clave primaria autoincremental para cada solicitud empresarial. |
| `empresa_id` | INT | NO | FK | - | **Empresa solicitante.** Clave foránea que apunta al `id_empresa` en `lavado_auto_empresa`. |
| `servicio_solicitado_id` | INT | NO | FK | - | **Servicio solicitado.** Clave foránea que apunta al `id_servicio` en `lavado_auto_servicio`. |
| `estado` | VARCHAR(20) | NO | - | 'pendiente' | **Estado de la solicitud.** Valores: 'pendiente', 'aprobada', 'rechazada', 'en_revision'. |
| `fecha_solicitud` | DATETIME | NO | - | CURRENT_TIMESTAMP | **Fecha de la solicitud.** Timestamp de cuando la empresa envió la solicitud. |
| `fecha_respuesta` | DATETIME | SÍ | - | NULL | **Fecha de respuesta.** Timestamp de cuando se respondió la solicitud. NULL si está pendiente. |
| `motivo_solicitud` | TEXT | NO | - | - | **Justificación de la solicitud.** Razón detallada por la cual la empresa necesita este servicio adicional. |
| `respuesta_admin` | TEXT | SÍ | - | '' | **Respuesta del administrador.** Justificación de aprobación o rechazo de la solicitud. |
| `usuario_responsable` | VARCHAR(255) | NO | - | - | **Responsable de la solicitud.** Persona de la empresa que realizó la solicitud. |
| `telefono_contacto` | VARCHAR(15) | NO | - | - | **Teléfono de contacto.** Número directo para coordinaciones sobre la solicitud. |

**Restricciones:**
- `unique_empresa_servicio_estado`: Evita solicitudes duplicadas pendientes
**Índices:**
- `idx_solicitud_estado`: Índice en `estado` para gestión de solicitudes
- `idx_solicitud_fecha`: Índice en `fecha_solicitud` para orden cronológico

---

## 🔍 VISTAS Y CONSULTAS ÚTILES

### Vista: `vista_reservas_completas`
**Descripción:** Vista consolidada que muestra información completa de reservas con datos de cliente, empresa y servicios.

**Campos incluidos:**
- `id_reserva`: ID de la reserva
- `fecha`: Fecha programada
- `hora`: Hora programada  
- `estado`: Estado actual
- `cliente`: Nombre completo del cliente
- `correo_cliente`: Email del cliente
- `nombre_empresa`: Empresa proveedora
- `placa_vehiculo`: Placa del vehículo (si aplica)
- `tipo_vehiculo`: Tipo de vehículo (si aplica)
- `es_reserva_empresarial`: Booleano si es empresarial
- `servicios`: Lista de servicios concatenados

### Vista: `vista_suscripciones_activas`
**Descripción:** Vista unificada de suscripciones activas (individuales y empresariales).

**Campos incluidos:**
- `tipo_suscripcion`: 'individual' o 'empresarial'
- `id_suscripcion`: ID de la suscripción
- `cliente`: Nombre del cliente o empresa
- `correo`: Email de contacto
- `plan`: Nombre del plan contratado
- `fecha_inicio`: Inicio de vigencia
- `fecha_fin`: Vencimiento
- `estado`: Estado actual
- `servicios_utilizados_mes`: Servicios consumidos
- `cantidad_servicios_mes`: Servicios permitidos

---

## 📈 TRIGGERS AUTOMÁTICOS

### `tr_suscripcion_fecha_fin`
**Función:** Calcula automáticamente la fecha de vencimiento (+30 días) para suscripciones individuales.

### `tr_suscripcion_empresarial_fecha_fin`
**Función:** Calcula automáticamente la fecha de vencimiento (+30 días) para suscripciones empresariales.

---

## 🔐 CONSIDERACIONES DE SEGURIDAD

1. **Contraseñas:** Todas las contraseñas se almacenan encriptadas usando hash PBKDF2 de Django.
2. **Tokens:** Los tokens de recuperación se eliminan después de su uso.
3. **Integridad referencial:** Todas las claves foráneas tienen restricciones de integridad.
4. **Índices:** Se incluyen índices para optimizar consultas frecuentes.

---

## 📝 NOTAS DE IMPLEMENTACIÓN

1. **Compatibilidad:** Optimizado para MySQL/MariaDB en XAMPP.
2. **Charset:** Utiliza UTF8MB4 para soporte completo de Unicode.
3. **Escalabilidad:** Diseñado para soportar crecimiento empresarial.
4. **Mantenimiento:** Incluye campos de auditoría y timestamps automáticos.
5. **Flexibilidad:** Soporta tanto clientes individuales como empresariales.

---

*Documento generado automáticamente basado en los modelos Django del sistema AUTONEW*
*Versión: 1.0 | Fecha: 11 de agosto de 2025*
