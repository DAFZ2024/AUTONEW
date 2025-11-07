# Informe de arquitectura — Proyecto AUTONEW

Fecha: 20 de octubre de 2025

Este documento describe la arquitectura global del proyecto AUTONEW, sus componentes principales, responsabilidades, puntos fuertes y recomendaciones prácticas.

## Resumen ejecutivo
- Patrón arquitectónico: Django MVT (Model-View-Template).
- App principal: `lavado_auto` (modelo de dominio, vistas, forms, middleware, lógica de negocio).
- Frontend moderno con Tailwind (`theme` + `django-tailwind`) y recarga en desarrollo (`django_browser_reload`).
- Base de datos por defecto: SQLite (configurada en `autonew/settings.py`).
- Autenticación: `AUTH_USER_MODEL = 'lavado_auto.Usuario'` (modelo de usuario personalizado).
- Funcionalidades destacadas: reservas, planes y suscripciones (usuario y empresarial), gestión de pagos/periodos de liquidación, sistema de PQRS, control de intentos fallidos y bloqueo de cuentas.

---

## Componentes y su rol

### 1. Proyecto y apps
- `autonew` (proyecto): contiene `settings.py`, `urls.py`, `wsgi.py`, configuración general.
- `lavado_auto` (app principal): contiene los modelos de dominio, vistas, middleware, formularios y lógica de negocio principal.
- `theme`: app creada para Tailwind (frontend styles).

### 2. Capas principales
- Modelos (domain + persistence)
  - Archivo principal: `lavado_auto/models.py`.
  - Modelos clave: `Usuario` (user model personalizado), `Empresa`, `Servicio`, `Reserva`, `ReservaServicio`, `Pago`, `Plan`, `SuscripcionUsuario`, `PlanEmpresarial`, `SuscripcionEmpresarial`, `PeriodoLiquidacion`, `DetalleLiquidacion`, `MensajeQueja`, `SolicitudContactoPlan`, entre otros.
  - Lógica implementada: generación de números de reserva, cálculo de precios y descuentos, manejo de intentos fallidos/login lockout, cálculo de liquidaciones y comisiones.

- Vistas (controladores en MVT)
  - Archivo principal: `lavado_auto/views.py`.
  - Funcionalidad: páginas públicas (`home`, `servicios`, `planes`), autenticación/registro, gestión de reservas (creación/edición/eliminación), endpoints AJAX para horas/servicios/empresas, correo de confirmación, vistas de administración restringidas.
  - Decoradores personalizados: `usuario_required`, `empresa_required`, `admin_required`.

- Templates y static
  - Templates referenciados en `TEMPLATES['DIRS']`: `lavado_auto/templates`.
  - Tailwind integrado con `theme/static` y `theme/static_src`.

- Middleware
  - Middleware personalizados registrados en `MIDDLEWARE`:
    - `lavado_auto.middleware_cookies.CookieConsentMiddleware` — gestión de consentimiento de cookies.
    - `lavado_auto.middleware_active_user.ActiveUserMiddleware` — verificación de usuarios activos.
    - `lavado_auto.middleware.AdminCRUDMiddleware` — protección de rutas CRUD a administradores.
    - `lavado_auto.middleware_cookies.CookiePolicyMiddleware` — política de cookies.

- Context processors
  - `lavado_auto.context_processors.cookie_context` incluido en `TEMPLATES`.

### 3. Infraestructura y servicios
- Correo SMTP (configurado en `settings.py` con Gmail SMTP). Actualmente las credenciales aparecen en `settings.py` (migrar a variables de entorno).
- Archivos/media: `MEDIA_ROOT` configurado y `ImageField` usado en `Usuario`.
- Dependencias principales (ver `requirements.txt`): Django 5.x, django-tailwind, django-browser-reload, pillow, requests, qrcode, etc.

### 4. Lógica de negocio relevante
- Reservas: creación con validaciones (disponibilidad por hora/fecha), separación servicios incluidos/en adicionales, manejo de suscripciones y límites mensuales, notificaciones por correo.
- Suscripciones: planes individuales y empresariales con descuentos, contador de servicios por mes, auto-renovación.
- Pagos y liquidaciones: modelos para registrar pagos y períodos de liquidación quincenales; cálculo de comisiones y totales netos a pagar a las empresas.
- Seguridad de cuentas: bloqueo temporal tras 3 intentos fallidos, desactivación tras repetidos intentos, emails de alerta y desactivación.

---

## Observaciones sobre calidad de código y arquitectura
- Muchas responsabilidades están implementadas directamente dentro de vistas y modelos (envío de emails, cálculos financieros, validaciones complejas). Esto es funcional, pero dificulta pruebas unitarias y la separación de responsabilidades.
- Logging: hay uso de `print()` y `logging` en distintos puntos; conviene unificar con `logging` configurado en `LOGGING` del `settings.py`.
- Seguridad: credenciales en `settings.py` (mover a variables de entorno). `DEBUG = True` requiere cambiarse para producción.
- Rendimiento: algunas vistas usan queries optimizadas (`prefetch_related`), pero se deben revisar puntos donde puedan aparecer N+1 queries en listados pesados.

---

## Recomendaciones prácticas (priorizadas)
1. Mover secretos a variables de entorno (usar `python-decouple` o `django-environ`) y eliminar credenciales del repositorio.
2. Extraer lógica de negocio compleja (reservas, liquidaciones, pagos) a servicios en `lavado_auto/services/` para facilitar pruebas y mantenimiento.
3. Añadir pruebas unitarias automáticas para las rutas críticas: registro/login, bloqueo de cuentas, creación de reservas, cálculo de liquidación.
4. Preparar settings por entorno: `settings/base.py`, `settings/dev.py`, `settings/prod.py`.
5. Implementar integración con una pasarela de pagos real si se requiere automatizar cobros (Stripe, MercadoPago, PayU), usando adaptadores y webhooks.
6. Reemplazar `print()` por `logging` en todo el proyecto y centralizar niveles de log.
7. Revisar y endurecer la configuración de seguridad (CSP, HSTS, HTTPS, `SESSION_COOKIE_SECURE`) para producción.

---

## Archivos clave localizados
- `autonew/settings.py` — configuración general.
- `requirements.txt` — dependencias.
- `lavado_auto/models.py` — modelos y lógica persistente (extenso).
- `lavado_auto/views.py` — vista y lógica de control (extenso).
- `lavado_auto/middleware.py` — middlewares personalizados.
- `theme/` — Tailwind frontend.

---

## Próximos pasos sugeridos (puedo implementarlos)
- Crear `DOCUMENTACION_ARQUITECTURA.md` (este archivo). ✅
- (Opcional) Refactor: mover lógica de reservas a `lavado_auto/services/reservas.py` y agregar tests.
- (Opcional) Añadir `.env` support y actualizar `settings.py` para leer secretos desde variables de entorno.
- (Opcional) Añadir tests unitarios básicos y ejecutar la suite.

---

Si quieres que realice alguna de las tareas sugeridas (por ejemplo agregar `.env` support, extraer la lógica de reservas a un servicio con tests, o crear pruebas unitarias), dime cuál y la implemento. También puedo generar un diagrama simple (MER y flujo de reserva) si lo necesitas.
