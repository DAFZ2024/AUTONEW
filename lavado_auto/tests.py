"""
Este archivo se mantiene por compatibilidad.
Los tests están organizados en el directorio 'tests/':
- test_models.py: Tests de modelos
- test_forms.py: Tests de formularios
- test_views.py: Tests de vistas
- test_integration.py: Tests de integración
- test_validators.py: Tests de validadores

Para ejecutar los tests:
    python manage.py test lavado_auto
    
Para ejecutar tests específicos:
    python manage.py test lavado_auto.tests.test_models
    python manage.py test lavado_auto.tests.test_forms
    
Para ejecutar con cobertura:
    coverage run --source='.' manage.py test lavado_auto
    coverage report
    coverage html
"""

from django.test import TestCase

# Los tests ahora están en el directorio tests/
# Este archivo se mantiene para compatibilidad con Django
