# 🚀 Guía de Instalación - AutoNew

## 📋 Tabla de Contenidos

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación Paso a Paso](#instalación-paso-a-paso)
3. [Configuración Inicial](#configuración-inicial)
4. [Primer Inicio](#primer-inicio)
5. [Verificación de la Instalación](#verificación-de-la-instalación)
6. [Solución de Problemas](#solución-de-problemas)
7. [Configuración Adicional](#configuración-adicional)

---

# 💻 Requisitos del Sistema

## Requisitos Mínimos

### 🖥️ Sistema Operativo
- ✅ **Windows 10/11** (recomendado)
- ✅ **macOS 10.15+**
- ✅ **Linux Ubuntu 20.04+**

### 🐍 Python
- **Versión requerida**: Python 3.12 o superior
- **Instalación**: [python.org](https://www.python.org/downloads/)

### 🟢 Node.js (para Tailwind CSS)
- **Versión requerida**: Node.js 16.0 o superior
- **Instalación**: [nodejs.org](https://nodejs.org/)

### 💾 Espacio en Disco
- **Mínimo**: 500 MB libres
- **Recomendado**: 2 GB libres

### 🧠 Memoria RAM
- **Mínimo**: 4 GB RAM
- **Recomendado**: 8 GB RAM

---

# 🔽 Instalación Paso a Paso

## Paso 1: Verificar Requisitos

### Verificar Python
```bash
python --version
# Debe mostrar: Python 3.12.x o superior
```

### Verificar Node.js
```bash
node --version
# Debe mostrar: v16.x.x o superior

npm --version
# Debe mostrar: 8.x.x o superior
```

### Verificar Git (opcional pero recomendado)
```bash
git --version
# Debe mostrar: git version 2.x.x
```

## Paso 2: Descargar el Proyecto

### Opción A: Clonar desde Git (recomendado)
```bash
git clone https://github.com/tu-usuario/autonew-django.git
cd autonew-django
```

### Opción B: Descargar ZIP
1. Descargar el archivo ZIP del proyecto
2. Extraer en la carpeta deseada
3. Abrir terminal en la carpeta extraída

## Paso 3: Crear Entorno Virtual

### En Windows (PowerShell/CMD)
```powershell
# Crear entorno virtual
python -m venv venvautonew

# Activar entorno virtual
venvautonew\Scripts\activate

# Verificar activación (debe aparecer (venvautonew) al inicio)
```

### En macOS/Linux
```bash
# Crear entorno virtual
python3 -m venv venvautonew

# Activar entorno virtual
source venvautonew/bin/activate

# Verificar activación (debe aparecer (venvautonew) al inicio)
```

## Paso 4: Instalar Dependencias Python

```bash
# Con el entorno virtual activado
pip install --upgrade pip
pip install -r requirements.txt
```

### ✅ Verificar instalación de paquetes:
```bash
pip list
```

Deberías ver paquetes como:
- Django==5.2.3
- Pillow==11.2.1
- django-tailwind==4.0.1
- etc.

## Paso 5: Configurar Tailwind CSS

```bash
# Navegar a la carpeta theme
cd theme

# Instalar dependencias de Node.js
npm install

# Verificar instalación
npm list --depth=0
```

## Paso 6: Configurar Base de Datos

```bash
# Volver a la carpeta raíz del proyecto
cd ..

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate
```

### ✅ Salida esperada:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, lavado_auto, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  ...
```

---

# ⚙️ Configuración Inicial

## Crear Superusuario

```bash
python manage.py createsuperuser
```

### Información requerida:
- **Nombre de usuario**: admin (o el que prefieras)
- **Correo electrónico**: tu-email@ejemplo.com
- **Contraseña**: (mínimo 8 caracteres, segura)

## Configurar Variables de Entorno (Opcional)

### Crear archivo .env
```bash
# En la raíz del proyecto
touch .env  # Linux/Mac
# O crear archivo .env manualmente en Windows
```

### Contenido del archivo .env:
```env
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Configurar Archivos Media

```bash
# Crear carpeta media si no existe
mkdir media
mkdir media/profile_pictures
```

---

# 🚀 Primer Inicio

## Método 1: Script Automático (Recomendado para Windows)

```powershell
# Ejecutar script de desarrollo
.\start-dev.ps1
```

Este script:
1. ✅ Verifica Node.js
2. 🔧 Instala dependencias npm si no existen
3. 👀 Inicia Tailwind en modo watch
4. 🚀 Inicia el servidor Django

## Método 2: Inicio Manual

### Terminal 1 - Tailwind CSS (modo watch)
```bash
cd theme
npm run build-dev
```

### Terminal 2 - Servidor Django
```bash
# Activar entorno virtual si no está activo
# Windows:
venvautonew\Scripts\activate
# macOS/Linux:
source venvautonew/bin/activate

# Iniciar servidor
python manage.py runserver
```

## Acceder a la Aplicación

### 🌐 URLs Principales:
- **Página Principal**: http://127.0.0.1:8000/
- **Admin Django**: http://127.0.0.1:8000/admin/
- **Panel CRUD Admin**: http://127.0.0.1:8000/logincrud/

---

# ✅ Verificación de la Instalación

## Checklist de Verificación

### ✅ Servidor Django
1. Abrir http://127.0.0.1:8000/
2. Debe cargar la página principal de AutoNew
3. No debe haber errores 500 o 404

### ✅ Tailwind CSS
1. La página debe tener estilos aplicados
2. Los botones deben tener colores y efectos
3. El diseño debe ser responsive

### ✅ Base de Datos
1. Acceder a http://127.0.0.1:8000/admin/
2. Iniciar sesión con el superusuario creado
3. Debe mostrar el panel de administración

### ✅ Autenticación
1. Ir a http://127.0.0.1:8000/login/
2. Registrar un nuevo usuario
3. Iniciar sesión correctamente

### ✅ Funcionalidades Principales
1. **Registro**: Crear cuenta nueva ✅
2. **Login**: Iniciar sesión ✅
3. **Perfil**: Editar perfil de usuario ✅
4. **Comentarios**: Publicar comentario ✅
5. **Reservas**: Hacer una reserva ✅

## Datos de Prueba (Opcional)

### Crear Empresa de Prueba
```bash
python manage.py shell
```

```python
from lavado_auto.models import Empresa, Servicio, EmpresaServicio

# Crear empresa
empresa = Empresa.objects.create(
    nombre_empresa="AutoLavado Express",
    direccion="Calle 123 #45-67",
    telefono="3001234567",
    email="info@autolavado.com"
)

# Crear servicios
servicio1 = Servicio.objects.create(
    nombre_servicio="Lavado Básico",
    descripcion="Lavado exterior completo",
    precio=15000
)

servicio2 = Servicio.objects.create(
    nombre_servicio="Lavado Premium",
    descripcion="Lavado exterior + interior + encerado",
    precio=35000
)

# Asociar servicios a empresa
EmpresaServicio.objects.create(empresa=empresa, servicio=servicio1)
EmpresaServicio.objects.create(empresa=empresa, servicio=servicio2)

print("Datos de prueba creados exitosamente!")
exit()
```

---

# 🚨 Solución de Problemas

## Problemas Comunes

### ❌ Error: "Python no reconocido"
**Solución:**
1. Verificar que Python esté instalado
2. Agregar Python al PATH del sistema
3. Reiniciar terminal/PowerShell

### ❌ Error: "No module named 'django'"
**Solución:**
```bash
# Verificar que el entorno virtual esté activado
# Windows:
venvautonew\Scripts\activate
# Mac/Linux:
source venvautonew/bin/activate

# Reinstalar requirements
pip install -r requirements.txt
```

### ❌ Error: "Node.js no reconocido"
**Solución:**
1. Instalar Node.js desde nodejs.org
2. Reiniciar terminal
3. Verificar con `node --version`

### ❌ Error: "Port already in use"
**Solución:**
```bash
# Usar otro puerto
python manage.py runserver 8001
```

### ❌ Error de CSS (sin estilos)
**Solución:**
```bash
cd theme
npm install
npm run build-dev
```

### ❌ Error de Base de Datos
**Solución:**
```bash
# Eliminar base de datos y empezar de nuevo
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### ❌ Error de Permisos (Windows)
**Solución:**
```powershell
# Cambiar política de ejecución
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Logs de Debug

### Ver logs detallados:
```bash
python manage.py runserver --verbosity=2
```

### Verificar configuración:
```bash
python manage.py check
```

### Ver configuración actual:
```bash
python manage.py diffsettings
```

---

# 🔧 Configuración Adicional

## Configurar Email (Opcional)

### En settings.py:
```python
# Para desarrollo - email en consola
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Para producción - Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-app-password'
```

## Configurar Diferentes Puertos

### Django en puerto personalizado:
```bash
python manage.py runserver 8080
```

### Tailwind con puerto personalizado:
```bash
# En theme/package.json, modificar scripts:
"build-dev": "tailwindcss -i ./static_src/src/input.css -o ./static/css/dist/styles.css --watch"
```

## Configurar IDE

### VS Code Extensions Recomendadas:
- Python
- Django
- Tailwind CSS IntelliSense
- HTML CSS Support
- GitLens

### PyCharm Configuration:
1. Abrir proyecto
2. Configurar intérprete Python (venv)
3. Marcar `lavado_auto` como Sources Root

---

# 📚 Próximos Pasos

## Después de la Instalación

1. **📖 Leer el Manual de Usuario**: [MANUAL_USUARIO.md](MANUAL_USUARIO.md)
2. **🔧 Revisar Documentación Técnica**: [DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md)
3. **🎨 Personalizar Tailwind**: Modificar `theme/tailwind.config.js`
4. **🗃️ Configurar Base de Datos Producción**: PostgreSQL o MySQL
5. **🚀 Preparar para Despliegue**: Seguir guía de despliegue

## Recursos de Ayuda

- 📧 **Soporte**: soporte@autonew.com
- 🐛 **Reportar Bugs**: GitHub Issues
- 📖 **Documentación**: README.md
- 💬 **Comunidad**: Discord/Slack

---

# ✅ Checklist Final

Antes de comenzar a usar AutoNew, verifica que:

- [ ] ✅ Python 3.12+ instalado y funcionando
- [ ] ✅ Node.js 16+ instalado y funcionando
- [ ] ✅ Entorno virtual creado y activado
- [ ] ✅ Dependencias Python instaladas
- [ ] ✅ Dependencias npm instaladas
- [ ] ✅ Base de datos migrada
- [ ] ✅ Superusuario creado
- [ ] ✅ Servidor Django iniciado correctamente
- [ ] ✅ Tailwind CSS compilando en modo watch
- [ ] ✅ Página principal carga sin errores
- [ ] ✅ Panel admin accesible
- [ ] ✅ Registro de usuarios funciona
- [ ] ✅ Sistema de login funciona

**🎉 ¡Felicitaciones! AutoNew está listo para usar.**

---

*Guía de instalación para AutoNew v1.0*  
*Última actualización: Junio 2025*

**💡 Tip**: Guarda esta guía como referencia para futuras instalaciones o para ayudar a otros desarrolladores.
