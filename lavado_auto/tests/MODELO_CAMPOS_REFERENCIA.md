# Referencia de Campos de Modelos para Tests

## Usuario (AbstractBaseUser personalizado)
- **Crear con**: `Usuario.objects.create_user()`
- **Campos requeridos**:
  - `nombre_usuario` (único, usado como USERNAME_FIELD)
  - `correo` (único, EmailField)
  - `password` (se encripta automáticamente con create_user)
  - `nombre_completo`
  - `telefono`
  - `rol` (choices: 'cliente', 'empresa', 'admin')

## Empresa
- **Crear con**: `Empresa.objects.create()`
- **Campos**:
  - `nombre_empresa` (NO 'nombre')
  - `direccion`
  - `telefono`
  - `email` (NO 'correo')
  - `contrasena` (tiene default)
  - `verificada` (default=False)
  - `latitud`, `longitud` (opcionales)
  - **NO tiene**: campo `usuario`, `descripcion`

## Plan
- **Crear con**: `Plan.objects.create()`
- **Campos requeridos**:
  - `nombre`
  - `tipo` (choices: 'basico', 'premium', 'completo')
  - `descripcion`
  - `precio_mensual` (NO 'precio')
  - `cantidad_servicios_mes`
  - **NO tiene**: campo `duracion_dias`

## Servicio
- **Crear con**: `Servicio.objects.create()`
- **Campos**:
  - `nombre_servicio` (NO 'nombre', único)
  - `descripcion`
  - `precio` (FloatField)

## Reserva
- **Crear con**: `Reserva.objects.create()`
- **Campos requeridos**:
  - `usuario` (FK a Usuario, NO 'cliente')
  - `empresa` (FK a Empresa)
  - `fecha` (DateField, NO 'fecha_reserva')
  - `hora` (TimeField)
  - `placa_vehiculo` (NO 'patente', opcional)
  - `tipo_vehiculo` (NO 'modelo_vehiculo', choices: sedan, suv, etc.)
  - `estado` (default='pendiente')

## EmpresaServicio (relación many-to-many)
- **Crear con**: `EmpresaServicio.objects.create()`
- **Campos**:
  - `empresa` (FK)
  - `servicio` (FK)
  - `precio` (Decimal)

## SuscripcionUsuario
- **Crear con**: `SuscripcionUsuario.objects.create()`
- **Campos**:
  - `usuario` (FK)
  - `plan` (FK)
  - `fecha_inicio` (default=timezone.now)
  - `fecha_fin` (se calcula automáticamente si no se proporciona)
  - `estado` (NO 'activa', choices: 'activa', 'pausada', 'cancelada', 'vencida', default='activa')

## Comentario
- **Crear con**: `Comentario.objects.create()`
- **Campos**:
  - `cliente` (FK a Usuario)
  - `empresa` (FK a Empresa)
  - `calificacion` (IntegerField, rango 1-5)
  - `comentario` (TextField)

## MensajeQueja
- **Crear con**: `MensajeQueja.objects.create()`
- **Campos**:
  - `cliente` (FK a Usuario)
  - `empresa` (FK a Empresa)
  - `tipo` (choices: 'mensaje', 'queja')
  - `asunto`
  - `descripcion`
