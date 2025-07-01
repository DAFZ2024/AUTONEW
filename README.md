# 🚗 AutoNew - Sistema de Gestión para Lavado de Autos

## 📋 Descripción del Proyecto

**AutoNew** es una aplicación web desarrollada en Django que gestiona servicios de lavado de automóviles. El sistema permite a los usuarios registrarse, realizar reservas de servicios, ver empresas disponibles, y a los administradores gestionar todo el contenido mediante un panel CRUD completo.

## ✨ Características Principales

### 👥 Para Usuarios Clientes:
- ✅ Registro e inicio de sesión seguro
- 🔐 Perfil de usuario personalizable con foto
- 📅 Sistema de reservas con selección de fecha, hora y servicios
- 💬 Sistema de comentarios y reseñas
- 📝 Envío de quejas y sugerencias
- 🏢 Visualización de empresas y servicios disponibles
- 📱 Interfaz responsive con Tailwind CSS

### 🔧 Para Administradores:
- 🛡️ Panel administrativo completo (CRUD)
- 👤 Gestión de usuarios
- 🏢 Gestión de empresas y servicios
- 📅 Gestión de citas y reservas
- 💬 Gestión de comentarios
- 📝 Gestión de quejas
- 📊 Control de estados de reservas

## 🛠️ Tecnologías Utilizadas

### Backend:
- **Django 5.2.3** - Framework web principal
- **SQLite3** - Base de datos
- **Pillow** - Manejo de imágenes
- **Python 3.12+** - Lenguaje de programación

### Frontend:
- **Tailwind CSS 4.0.1** - Framework de estilos
- **HTML5/CSS3** - Estructura y estilos
- **JavaScript** - Interactividad
- **Django Templates** - Sistema de plantillas

### Desarrollo:
- **django-browser-reload** - Recarga automática en desarrollo
- **django-tailwind** - Integración de Tailwind con Django

## 📁 Estructura del Proyecto

```
AUTONEW-DJANGO/
├── 📁 autonew/                    # Configuración principal del proyecto
│   ├── __init__.py
│   ├── settings.py               # Configuraciones
│   ├── urls.py                   # URLs principales
│   ├── wsgi.py                   # Configuración WSGI
│   └── asgi.py                   # Configuración ASGI
│
├── 📁 lavado_auto/               # Aplicación principal
│   ├── models.py                 # Modelos de datos
│   ├── views.py                  # Lógica de vistas
│   ├── forms.py                  # Formularios
│   ├── admin.py                  # Configuración admin
│   ├── middleware.py             # Middleware personalizado
│   ├── 📁 templates/             # Plantillas HTML
│   ├── 📁 static/                # Archivos estáticos
│   └── 📁 migrations/            # Migraciones de BD
│
├── 📁 theme/                     # Configuración Tailwind
│   ├── package.json
│   ├── tailwind.config.js
│   └── 📁 static_src/
│
├── 📁 media/                     # Archivos subidos
├── manage.py                     # Comandos Django
├── requirements.txt              # Dependencias Python
├── start-dev.ps1                 # Script de desarrollo
└── db.sqlite3                    # Base de datos
```

## 🗃️ Modelos de Datos

### 👤 Usuario (CustomUser)
```python
- id_usuario (PK)
- nombre_completo
- nombre_usuario (único)
- correo (único)
- telefono
- direccion
- profile_picture (imagen)
- rol (cliente/admin)
- token_reset
```

### 🏢 Empresa
```python
- id_empresa (PK)
- nombre_empresa
- direccion
- telefono
- email
- servicios (ManyToMany)
```

### 🔧 Servicio
```python
- id_servicio (PK)
- nombre_servicio (único)
- descripcion
- precio
```

### 📅 Reserva
```python
- id_reserva (PK)
- fecha
- hora
- estado (completado/no_completado)
- usuario (FK)
- empresa (FK)
- servicios (ManyToMany)
```

### 💬 Comentario
```python
- id_comentario (PK)
- comentario
- fecha
- usuario (FK)
```

### 📝 MensajeQueja
```python
- id_mensaje (PK)
- contenido
- fecha_envio
- estado
- respuesta
- usuario (FK)
```

## 🚀 Instalación y Configuración

### 📋 Prerrequisitos
- Python 3.12 o superior
- Node.js 16+ (para Tailwind CSS)
- Git

### 🔽 Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/autonew-django.git
cd autonew-django
```

2. **Crear entorno virtual**
```bash
python -m venv venvautonew
# Windows:
venvautonew\Scripts\activate
# Linux/Mac:
source venvautonew/bin/activate
```

3. **Instalar dependencias Python**
```bash
pip install -r requirements.txt
```

4. **Configurar Tailwind CSS**
```bash
cd theme
npm install
```

5. **Configurar base de datos**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Crear superusuario**
```bash
python manage.py createsuperuser
```

## 🏃‍♂️ Ejecución

### Desarrollo (Modo Automático)
```powershell
# Windows PowerShell
.\start-dev.ps1
```

### Desarrollo (Modo Manual)
```bash
# Terminal 1 - Tailwind CSS (modo watch)
cd theme
npm run build-dev

# Terminal 2 - Servidor Django
python manage.py runserver
```

### Producción
```bash
# Compilar CSS para producción
cd theme
npm run build

# Ejecutar servidor
python manage.py runserver --settings=autonew.settings_production
```

## 🌐 URLs y Navegación

### 🏠 URLs Públicas:
- `/` - Página de inicio
- `/login/` - Inicio de sesión/registro
- `/nosotros/` - Acerca de nosotros
- `/servicios/` - Servicios disponibles
- `/empresas/` - Empresas afiliadas
- `/reservas/` - Sistema de reservas
- `/contacto/` - Formulario de contacto
- `/perfil/` - Perfil de usuario

### 🔐 URLs Administrativas (requieren rol admin):
- `/logincrud/` - Login administrativo
- `/homecrud/` - Dashboard admin
- `/usuarioscrud/` - Gestión de usuarios
- `/empresascrud/` - Gestión de empresas
- `/servicioscrud/` - Gestión de servicios
- `/citascrud/` - Gestión de citas
- `/comentarioscrud/` - Gestión de comentarios
- `/quejascrud/` - Gestión de quejas

## 🔒 Sistema de Autenticación

### Características:
- ✅ Autenticación basada en nombre de usuario
- 🔐 Contraseñas hasheadas con Django
- 👥 Sistema de roles (cliente/admin)
- 🛡️ Middleware de protección para rutas admin
- 🔄 Sistema de reset de contraseña
- 📱 Perfil personalizable con imagen

### Decorador de Seguridad:
```python
@admin_required
def vista_admin(request):
    # Solo accesible para usuarios con rol 'admin'
    pass
```

## 🎨 Interfaz de Usuario

### Diseño:
- 📱 **Responsive Design** con Tailwind CSS
- 🎨 **Interfaz Moderna** y profesional
- ⚡ **Carga Rápida** con CSS optimizado
- 🔄 **Recarga Automática** en desarrollo
- 📊 **Dashboard Administrativo** completo

### Características de UX:
- 💬 Mensajes de feedback al usuario
- ⚠️ Validación de formularios en tiempo real
- 🔄 Estados de carga y confirmación
- 📱 Navegación intuitiva

## 📊 Funcionalidades Destacadas

### 🎯 Sistema de Reservas Inteligente:
- Selección de empresa y servicios
- Calendario interactivo
- Verificación de disponibilidad horaria
- Cálculo automático de precios

### 💼 Panel Administrativo:
- CRUD completo para todas las entidades
- Cambio de estados de reservas
- Gestión de usuarios y permisos
- Estadísticas y reportes

### 🔐 Seguridad:
- Validación de datos en backend
- Protección CSRF
- Sanitización de inputs
- Control de acceso por roles

## 🐛 Desarrollo y Debug

### Comandos Útiles:
```bash
# Hacer migraciones
python manage.py makemigrations

# Aplicar migraciones  
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic

# Shell de Django
python manage.py shell

# Verificar proyecto
python manage.py check
```

### Variables de Entorno:
```python
# En settings.py
DEBUG = True  # Solo en desarrollo
SECRET_KEY = 'tu-clave-secreta'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

## 🚀 Despliegue en Producción

### Consideraciones:
1. ⚠️ Cambiar `DEBUG = False`
2. 🔐 Usar una `SECRET_KEY` segura
3. 🌐 Configurar `ALLOWED_HOSTS`
4. 🗃️ Usar PostgreSQL en lugar de SQLite
5. 📁 Configurar servidor de archivos estáticos
6. 🔒 Usar HTTPS

### Ejemplo de configuración:
```python
# settings_production.py
DEBUG = False
ALLOWED_HOSTS = ['tu-dominio.com']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # ... configuración PostgreSQL
    }
}
```

## 🤝 Contribuciones

### Para contribuir:
1. 🍴 Fork el proyecto
2. 🌿 Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push a la rama (`git push origin feature/AmazingFeature`)
5. 🔄 Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para detalles.

## 👥 Equipo de Desarrollo

- **Desarrollador Principal**: [Tu Nombre]
- **Email**: tu-email@ejemplo.com
- **GitHub**: [@tu-usuario](https://github.com/tu-usuario)

## 📞 Soporte

¿Tienes preguntas o necesitas ayuda?
- 📧 Email: soporte@autonew.com
- 🐛 Issues: [GitHub Issues](https://github.com/tu-usuario/autonew-django/issues)
- 📖 Wiki: [Documentación Completa](https://github.com/tu-usuario/autonew-django/wiki)

---

⭐ **¡No olvides dar una estrella al proyecto si te fue útil!** ⭐

Desarrollado con ❤️ usando Django y Tailwind CSS
