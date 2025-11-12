# 🧪 Guía de Testing - AUTONEW

## 📋 Índice
- [Introducción](#introducción)
- [Estructura de Tests](#estructura-de-tests)
- [Instalación](#instalación)
- [Ejecutar Tests](#ejecutar-tests)
- [Cobertura de Tests](#cobertura-de-tests)
- [Mejores Prácticas](#mejores-prácticas)

---

## 🎯 Introducción

Esta suite de pruebas proporciona **cobertura completa** para la aplicación AUTONEW, incluyendo:
- ✅ Tests unitarios de modelos
- ✅ Tests de formularios
- ✅ Tests de vistas
- ✅ Tests de integración
- ✅ Tests de validadores

## 📁 Estructura de Tests

```
lavado_auto/
├── tests/
│   ├── __init__.py
│   ├── test_models.py          # Tests de modelos (Usuario, Empresa, Reserva, etc.)
│   ├── test_forms.py            # Tests de formularios
│   ├── test_views.py            # Tests de vistas y URLs
│   ├── test_integration.py      # Tests de flujos completos
│   └── test_validators.py       # Tests de validadores personalizados
└── tests.py                     # Archivo legacy (mantener para compatibilidad)
```

## 🔧 Instalación

### 1. Instalar dependencias de testing

```powershell
# Activar entorno virtual
.\venvautonew\Scripts\Activate.ps1

# Instalar paquetes necesarios
pip install coverage pytest pytest-django pytest-cov
```

### 2. Actualizar requirements.txt

```bash
# Agregar al final de requirements.txt
coverage>=7.0.0
pytest>=7.4.0
pytest-django>=4.5.0
pytest-cov>=4.1.0
```

## 🚀 Ejecutar Tests

### Método 1: Scripts automatizados (Recomendado)

#### En PowerShell:
```powershell
# Todos los tests
.\run_tests.ps1 all

# Solo tests de modelos
.\run_tests.ps1 models

# Solo tests de formularios
.\run_tests.ps1 forms

# Solo tests de vistas
.\run_tests.ps1 views

# Tests de integración
.\run_tests.ps1 integration

# Tests con cobertura
.\run_tests.ps1 coverage

# Tests rápidos
.\run_tests.ps1 quick
```

#### En CMD:
```cmd
run_tests.bat all
run_tests.bat models
run_tests.bat coverage
```

### Método 2: Django test runner

```powershell
# Todos los tests
python manage.py test lavado_auto

# Tests específicos
python manage.py test lavado_auto.tests.test_models
python manage.py test lavado_auto.tests.test_forms
python manage.py test lavado_auto.tests.test_views
python manage.py test lavado_auto.tests.test_integration

# Test específico de una clase
python manage.py test lavado_auto.tests.test_models.UsuarioModelTest

# Test específico de un método
python manage.py test lavado_auto.tests.test_models.UsuarioModelTest.test_crear_usuario_valido

# Con más verbosidad
python manage.py test lavado_auto --verbosity=2

# Mantener la base de datos después de los tests (para debugging)
python manage.py test lavado_auto --keepdb
```

### Método 3: Pytest (opcional)

```powershell
# Todos los tests
pytest

# Con cobertura
pytest --cov=lavado_auto

# Tests específicos
pytest lavado_auto/tests/test_models.py
pytest lavado_auto/tests/test_models.py::UsuarioModelTest
pytest lavado_auto/tests/test_models.py::UsuarioModelTest::test_crear_usuario_valido
```

## 📊 Cobertura de Tests

### Generar reporte de cobertura

```powershell
# Ejecutar tests con cobertura
coverage run --source='.' manage.py test lavado_auto

# Ver reporte en terminal
coverage report

# Generar reporte HTML
coverage html

# Abrir reporte HTML
start htmlcov/index.html  # Windows
```

### Interpretar el reporte

- **Verde (>80%)**: Excelente cobertura ✅
- **Amarillo (50-80%)**: Cobertura aceptable ⚠️
- **Rojo (<50%)**: Necesita más tests ❌

### Ejemplo de salida:

```
Name                              Stmts   Miss  Cover
-----------------------------------------------------
lavado_auto/models.py              450     45    90%
lavado_auto/views.py               320     80    75%
lavado_auto/forms.py               120     15    87%
-----------------------------------------------------
TOTAL                              890    140    84%
```

## 📝 Descripción de Tests

### 🗄️ test_models.py (Tests de Modelos)

**Cobertura**: Usuario, Empresa, Servicio, Reserva, Plan, MensajeQueja, Comentario

**Tests incluidos**:
- ✅ Creación de objetos con datos válidos
- ✅ Validación de campos únicos (correo, RUT)
- ✅ Validación de roles y estados
- ✅ Valores por defecto
- ✅ Representación en string (`__str__`)
- ✅ Asignación automática de fechas
- ✅ Relaciones entre modelos

**Ejemplo**:
```python
def test_crear_usuario_valido(self):
    """Verifica que se pueda crear un usuario con datos válidos"""
    usuario = Usuario.objects.create(**self.usuario_data)
    self.assertIsNotNone(usuario.id)
    self.assertEqual(usuario.nombre, 'Juan')
```

### 📝 test_forms.py (Tests de Formularios)

**Cobertura**: ComentarioClienteForm, CustomPasswordResetForm

**Tests incluidos**:
- ✅ Validación de formularios con datos válidos
- ✅ Validación de formularios con datos inválidos
- ✅ Campos requeridos
- ✅ Limpieza y formateo de datos
- ✅ Widgets correctos

### 👁️ test_views.py (Tests de Vistas)

**Cobertura**: HomeView, LoginView, ReservaView, EmpresaView, PerfilView

**Tests incluidos**:
- ✅ Códigos de estado HTTP
- ✅ Redirecciones
- ✅ Autenticación requerida
- ✅ Permisos por rol
- ✅ Protección CSRF
- ✅ Configuración de URLs

### 🔗 test_integration.py (Tests de Integración)

**Cobertura**: Flujos completos de negocio

**Flujos probados**:
- ✅ Flujo completo de reserva (crear → confirmar → completar → comentar)
- ✅ Flujo de suscripción
- ✅ Flujo de quejas y comentarios
- ✅ Múltiples reservas por cliente
- ✅ Verificación de empresas

**Ejemplo**:
```python
def test_flujo_reserva_completo(self):
    """Prueba el flujo completo de reserva"""
    # 1. Cliente crea reserva
    # 2. Empresa confirma
    # 3. Servicio se completa
    # 4. Cliente deja comentario
```

## ✅ Mejores Prácticas

### 1. Estructura de un test

```python
def test_nombre_descriptivo(self):
    """Docstring explicando qué se prueba"""
    # Arrange (Preparar)
    datos = {...}
    
    # Act (Actuar)
    resultado = funcion(datos)
    
    # Assert (Verificar)
    self.assertEqual(resultado, esperado)
```

### 2. Nombres descriptivos

❌ **Mal**: `test_1()`, `test_usuario()`

✅ **Bien**: `test_crear_usuario_valido()`, `test_correo_unico()`

### 3. Un concepto por test

❌ **Mal**: Test que verifica 10 cosas diferentes

✅ **Bien**: Tests separados para cada caso

### 4. Datos de prueba independientes

```python
def setUp(self):
    """Crear datos limpios para cada test"""
    self.usuario = Usuario.objects.create(...)
```

### 5. Tests aislados

- Cada test debe poder ejecutarse independientemente
- No depender del orden de ejecución
- Limpiar datos después de cada test (Django lo hace automáticamente)

## 🎯 Objetivos de Cobertura

| Componente | Objetivo | Actual |
|------------|----------|--------|
| Modelos | 90% | 🔄 Por medir |
| Formularios | 85% | 🔄 Por medir |
| Vistas | 75% | 🔄 Por medir |
| Integración | 80% | 🔄 Por medir |
| **TOTAL** | **80%** | 🔄 Por medir |

## 📈 Siguientes Pasos

### Fase 1: Implementación (✅ Completado)
- [x] Crear estructura de tests
- [x] Implementar tests de modelos
- [x] Implementar tests de formularios
- [x] Implementar tests de vistas
- [x] Implementar tests de integración

### Fase 2: Ejecución (🔄 En progreso)
- [ ] Ejecutar tests y verificar que pasen
- [ ] Medir cobertura inicial
- [ ] Identificar áreas sin cobertura
- [ ] Ajustar tests según resultados

### Fase 3: Mejora Continua
- [ ] Agregar tests para nuevas funcionalidades
- [ ] Mantener cobertura >80%
- [ ] Integrar con CI/CD
- [ ] Automatizar ejecución en commits

## 🐛 Debugging Tests

### Ver detalles de fallos

```powershell
python manage.py test lavado_auto --verbosity=2
```

### Mantener base de datos para inspección

```powershell
python manage.py test lavado_auto --keepdb
```

### Ejecutar un solo test que falla

```powershell
python manage.py test lavado_auto.tests.test_models.UsuarioModelTest.test_crear_usuario_valido --verbosity=2
```

### Ver prints durante tests

```powershell
python manage.py test lavado_auto --verbosity=2 --debug-mode
```

## 🔧 Configuración Avanzada

### Ejecutar tests en paralelo

```powershell
python manage.py test lavado_auto --parallel=4
```

### Ejecutar solo tests que fallaron

```powershell
python manage.py test lavado_auto --failfast
```

## 📚 Recursos Adicionales

- [Django Testing Documentation](https://docs.djangoproject.com/en/4.2/topics/testing/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Pytest Django Plugin](https://pytest-django.readthedocs.io/)
- [Testing Best Practices](https://testdriven.io/blog/django-test-best-practices/)

---

## 🆘 Soporte

Si encuentras problemas con los tests:

1. Verifica que el entorno virtual esté activado
2. Asegúrate de tener todas las dependencias instaladas
3. Revisa que la base de datos de pruebas pueda crearse
4. Consulta la documentación específica de cada test

**¡Felices pruebas!** 🎉
