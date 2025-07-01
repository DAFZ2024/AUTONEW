# 📋 Manual de Usuario - AutoNew

## 🎯 Introducción

Este manual te guiará paso a paso para usar todas las funcionalidades del sistema AutoNew, tanto si eres un cliente que quiere reservar servicios como si eres un administrador que gestiona el sistema.

## 👥 Tipos de Usuario

### 🧑‍💼 Cliente
- Puede registrarse y hacer login
- Reservar servicios de lavado
- Ver y comentar servicios
- Gestionar su perfil personal
- Enviar quejas o sugerencias

### 🔧 Administrador
- Acceso completo al panel administrativo
- Gestionar usuarios, empresas y servicios
- Administrar reservas y citas
- Moderar comentarios y responder quejas

---

# 👤 GUÍA PARA CLIENTES

## 1. 🔐 Registro e Inicio de Sesión

### Registro de Nueva Cuenta:
1. Ve a la página principal y haz clic en **"Iniciar Sesión"**
2. En la pestaña **"Registro"**, completa:
   - **Nombre Completo**: Tu nombre y apellidos
   - **Nombre de Usuario**: Único, sin espacios
   - **Correo Electrónico**: Email válido
   - **Teléfono**: Solo números (se agregará automáticamente el prefijo 57)
   - **Dirección**: Tu dirección completa
   - **Contraseña**: Mínimo 6 caracteres
   - **Confirmar Contraseña**: Debe coincidir con la anterior
3. Haz clic en **"Registrarse"**
4. Si todo está correcto, verás un mensaje de éxito

### Iniciar Sesión:
1. En la pestaña **"Iniciar Sesión"**:
   - **Nombre de Usuario**: El que creaste
   - **Contraseña**: Tu contraseña
2. Haz clic en **"Iniciar Sesión"**
3. Serás redirigido a la página principal

## 2. 👤 Gestión de Perfil

### Actualizar Perfil:
1. Haz clic en **"Perfil"** en el menú
2. Puedes modificar:
   - Nombre completo
   - Correo electrónico
   - Teléfono
   - Dirección
   - **Foto de Perfil**: Sube una imagen (JPG, PNG)
3. **Cambiar Contraseña** (opcional):
   - Nueva contraseña (mínimo 6 caracteres)
   - Confirmar nueva contraseña
4. Haz clic en **"Actualizar Perfil"**

## 3. 📅 Sistema de Reservas

### Hacer una Reserva:
1. Ve a **"Reservas"** en el menú principal
2. **Paso 1 - Seleccionar Empresa**:
   - Elige la empresa de tu preferencia
   - Se mostrarán los servicios disponibles para esa empresa
3. **Paso 2 - Seleccionar Servicios**:
   - Marca los servicios que deseas
   - Verás el precio total actualizándose
4. **Paso 3 - Fecha y Hora**:
   - Selecciona la fecha (no puede ser anterior a hoy)
   - Elige la hora disponible (las ocupadas aparecen deshabilitadas)
5. **Confirmar Reserva**:
   - Revisa todos los datos
   - Haz clic en **"Confirmar Reserva"**

### Estados de Reserva:
- **🟡 No Completado**: Reserva pendiente
- **🟢 Completado**: Servicio realizado

## 4. 💬 Comentarios y Reseñas

### Dejar un Comentario:
1. Ve a **"Servicios"** o **"Comentarios"**
2. En la sección de comentarios:
   - Escribe tu experiencia
   - Haz clic en **"Enviar Comentario"**
3. Tu comentario aparecerá con tu nombre y foto de perfil

## 5. 📝 Quejas y Sugerencias

### Enviar una Queja:
1. Ve a **"Contacto"**
2. Completa el formulario:
   - **Asunto**: Resumen de tu consulta
   - **Mensaje**: Describe detalladamente tu queja o sugerencia
3. Haz clic en **"Enviar"**
4. Un administrador revisará y responderá tu mensaje

## 6. 🏢 Explorar Empresas y Servicios

### Ver Empresas:
- En **"Empresas"** puedes ver todas las empresas afiliadas
- Información de contacto y servicios disponibles

### Ver Servicios:
- En **"Servicios"** encuentras todos los servicios disponibles
- Precios y descripciones detalladas
- Comentarios de otros clientes

---

# 🔧 GUÍA PARA ADMINISTRADORES

## 1. 🔐 Acceso Administrativo

### Iniciar Sesión como Admin:
1. Ve a `/logincrud/` o haz clic en **"Admin"** si está disponible
2. Usa tu cuenta con rol de **administrador**
3. Accederás al **Dashboard Administrativo**

## 2. 🏠 Dashboard Principal

### Panel de Control:
- **Resumen de estadísticas**
- **Accesos rápidos** a todas las secciones
- **Notificaciones** de nuevas reservas, quejas, etc.

## 3. 👥 Gestión de Usuarios

### Ver Usuarios:
1. Ve a **"Usuarios CRUD"**
2. Lista completa de usuarios registrados
3. Información: nombre, email, rol, fecha de registro

### Acciones Disponibles:
- **👁️ Ver**: Detalles completos del usuario
- **✏️ Editar**: Modificar información del usuario
- **🗑️ Eliminar**: Borrar usuario (cuidado: irreversible)
- **🔄 Cambiar Rol**: Convertir cliente en admin o viceversa

## 4. 🏢 Gestión de Empresas

### Crear Nueva Empresa:
1. Ve a **"Empresas CRUD"**
2. Haz clic en **"Agregar Empresa"**
3. Completa:
   - **Nombre de la Empresa**
   - **Dirección**
   - **Teléfono**
   - **Email de contacto**
4. **Asignar Servicios** que ofrece la empresa

### Gestionar Empresas Existentes:
- **Editar**: Cambiar información de contacto
- **Servicios**: Agregar o quitar servicios
- **Eliminar**: Borrar empresa (se eliminarán sus reservas)

## 5. 🔧 Gestión de Servicios

### Crear Nuevo Servicio:
1. Ve a **"Servicios CRUD"**
2. Haz clic en **"Agregar Servicio"**
3. Completa:
   - **Nombre del Servicio**: Descriptivo y único
   - **Descripción**: Detalles del servicio
   - **Precio**: En pesos colombianos

### Modificar Servicios:
- **Cambiar Precios**: Actualizar costos
- **Editar Descripción**: Mejorar información
- **Eliminar**: Borrar servicio (afectará reservas existentes)

## 6. 📅 Gestión de Citas y Reservas

### Panel de Citas:
1. Ve a **"Citas CRUD"**
2. Verás todas las reservas:
   - **Información del cliente**
   - **Servicios solicitados**
   - **Fecha y hora**
   - **Estado actual**
   - **Empresa asignada**

### Cambiar Estado de Reserva:
1. Localiza la reserva
2. Haz clic en **"Cambiar Estado"**
3. Opciones:
   - **🟡 No Completado → 🟢 Completado**
   - **🟢 Completado → 🟡 No Completado**

### Filtros Disponibles:
- **Por fecha**: Reservas de un día específico
- **Por estado**: Solo completadas o pendientes
- **Por empresa**: Reservas de una empresa específica
- **Por cliente**: Reservas de un usuario específico

## 7. 💬 Gestión de Comentarios

### Moderar Comentarios:
1. Ve a **"Comentarios CRUD"**
2. Lista de todos los comentarios:
   - **Usuario que comentó**
   - **Fecha y hora**
   - **Contenido del comentario**

### Acciones:
- **👁️ Ver**: Leer comentario completo
- **🗑️ Eliminar**: Borrar comentarios inapropiados
- **⚠️ Moderar**: Ocultar temporalmente

## 8. 📝 Gestión de Quejas

### Panel de Quejas:
1. Ve a **"Quejas CRUD"**
2. Lista de mensajes de contacto:
   - **Cliente que escribió**
   - **Fecha de envío**
   - **Estado**: Respondido/No respondido
   - **Contenido del mensaje**

### Responder Quejas:
1. Haz clic en **"Responder"** en la queja
2. Escribe tu respuesta
3. El estado cambiará a **"Respondido"**
4. El cliente verá la respuesta en su próximo contacto

### Estados de Quejas:
- **🔴 No Respondido**: Requiere atención
- **🟢 Respondido**: Ya gestionado

## 9. 📊 Reportes y Estadísticas

### Métricas Importantes:
- **Total de usuarios registrados**
- **Reservas del mes actual**
- **Servicios más solicitados**
- **Empresas con más reservas**
- **Quejas pendientes**

---

# 🛠️ SOLUCIÓN DE PROBLEMAS

## ❌ Problemas Comunes - Clientes

### No puedo registrarme:
- ✅ Verifica que el nombre de usuario no exista
- ✅ Confirma que el email no esté registrado
- ✅ Asegúrate de que las contraseñas coincidan
- ✅ Completa todos los campos obligatorios

### No puedo hacer una reserva:
- ✅ Verifica que hayas iniciado sesión
- ✅ Selecciona primero la empresa
- ✅ Elige al menos un servicio
- ✅ La fecha no puede ser anterior a hoy
- ✅ La hora debe estar disponible

### No aparece mi comentario:
- ✅ Asegúrate de haber hecho clic en "Enviar"
- ✅ Verifica tu conexión a internet
- ✅ Es posible que esté pendiente de moderación

## ⚠️ Problemas Comunes - Administradores

### No puedo acceder al panel admin:
- ✅ Verifica que tu usuario tenga rol "admin"
- ✅ Usa la URL correcta: `/logincrud/`
- ✅ Confirma que hayas iniciado sesión

### Error al cambiar estado de reserva:
- ✅ Recarga la página
- ✅ Verifica que la reserva aún exista
- ✅ Confirma tu conexión a internet

### No puedo eliminar un elemento:
- ✅ Verifica que no tenga dependencias
- ✅ Por ejemplo: una empresa con reservas activas
- ✅ Elimina primero las referencias relacionadas

---

# 📞 CONTACTO Y SOPORTE

## 🆘 ¿Necesitas Ayuda?

### Para Usuarios:
- 📧 **Email**: soporte@autonew.com
- 📞 **Teléfono**: +57 300 123 4567
- 🕐 **Horario**: Lunes a Viernes, 8:00 AM - 6:00 PM

### Para Administradores:
- 📧 **Email Técnico**: admin@autonew.com
- 🔧 **Soporte Técnico**: +57 300 987 6543
- 🚨 **Emergencias**: 24/7

## 📚 Recursos Adicionales

- 📖 **Manual Técnico**: Para desarrolladores
- 🎥 **Videos Tutorial**: Próximamente
- ❓ **FAQ**: Preguntas frecuentes
- 📋 **Changelog**: Historial de actualizaciones

---

**💡 Consejo**: Guarda este manual como referencia y no dudes en contactarnos si necesitas ayuda adicional.

*Última actualización: Junio 2025*
