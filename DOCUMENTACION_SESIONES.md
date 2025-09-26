# Configuración de Sesiones - AutoNew

## Configuración de Tiempo de Sesión

Se ha configurado el sistema para que las sesiones de usuario expiren automáticamente después de **4 horas** de inactividad.

### Configuraciones Aplicadas

En el archivo `autonew/settings.py` se han establecido las siguientes configuraciones:

```python
# Configuración de seguridad para cookies de sesión
SESSION_COOKIE_AGE = 14400  # 4 horas en segundos (4 * 60 * 60)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # La sesión expira según SESSION_COOKIE_AGE
SESSION_SAVE_EVERY_REQUEST = True  # Actualiza la sesión en cada request (reinicia el timer de 4 horas)
SESSION_COOKIE_SECURE = not DEBUG  # Solo HTTPS en producción
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

### Comportamiento del Sistema

1. **Duración de Sesión**: Cada sesión dura exactamente 4 horas desde el último login o actividad.

2. **Renovación Automática**: Con `SESSION_SAVE_EVERY_REQUEST = True`, cada vez que el usuario realiza una acción en el sitio, el timer de 4 horas se reinicia.

3. **Expiración Automática**: Después de 4 horas de inactividad, la sesión expira automáticamente y el usuario debe iniciar sesión nuevamente.

4. **Seguridad**: Las cookies están configuradas con medidas de seguridad apropiadas:
   - `SESSION_COOKIE_HTTPONLY = True`: Previene acceso via JavaScript
   - `SESSION_COOKIE_SAMESITE = 'Lax'`: Protección contra ataques CSRF
   - `SESSION_COOKIE_SECURE`: Solo HTTPS en producción

### Middleware de Apoyo

El sistema cuenta con un middleware adicional (`ActiveUserMiddleware`) que:
- Verifica que los usuarios autenticados estén activos
- Cierra automáticamente sesiones de usuarios desactivados
- No interfiere con el sistema de expiración de sesiones

### Pruebas

Para verificar la configuración, ejecuta:
```bash
python test_session_config.py
```

Este script mostrará la configuración actual y calculará los tiempos de expiración.

### Casos de Uso

- **Usuario Activo**: Si el usuario está navegando el sitio, su sesión se renueva automáticamente cada 4 horas.
- **Usuario Inactivo**: Si el usuario deja el sitio abierto sin usarlo por 4 horas, será desconectado automáticamente.
- **Cierre de Navegador**: Con `SESSION_EXPIRE_AT_BROWSER_CLOSE = False`, la sesión puede persistir entre cierres de navegador hasta cumplir las 4 horas.

### Beneficios de Seguridad

1. **Reducción de Riesgo**: Limita el tiempo de exposición en caso de que alguien acceda a una sesión abandonada.
2. **Cumplimiento**: Ayuda a cumplir con buenas prácticas de seguridad web.
3. **Balance**: 4 horas es un tiempo razonable que equilibra seguridad y experiencia de usuario.

---

**Nota**: Esta configuración se aplica inmediatamente a todas las nuevas sesiones. Los usuarios que ya tienen sesiones activas mantendrán su configuración anterior hasta que inicien sesión nuevamente.
