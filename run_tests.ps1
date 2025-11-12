# Script PowerShell para ejecutar tests
# Uso: .\run_tests.ps1 [opcion]
# Opciones: all, models, forms, views, integration, coverage

param(
    [string]$option = "all"
)

Write-Host "[TEST] Ejecutando tests de AUTONEW..." -ForegroundColor Cyan

# Activar entorno virtual
if (Test-Path ".\venvautonew\Scripts\Activate.ps1") {
    & .\venvautonew\Scripts\Activate.ps1
    Write-Host "[OK] Entorno virtual activado" -ForegroundColor Green
} else {
    Write-Host "[WARN] Entorno virtual no encontrado" -ForegroundColor Yellow
}

switch ($option) {
    "all" {
        Write-Host "`n[ALL] Ejecutando TODOS los tests..." -ForegroundColor Yellow
        python manage.py test lavado_auto --verbosity=2
    }
    "models" {
        Write-Host "`n[MODELS] Ejecutando tests de MODELOS..." -ForegroundColor Yellow
        python manage.py test lavado_auto.tests.test_models --verbosity=2
    }
    "forms" {
        Write-Host "`n[FORMS] Ejecutando tests de FORMULARIOS..." -ForegroundColor Yellow
        python manage.py test lavado_auto.tests.test_forms --verbosity=2
    }
    "views" {
        Write-Host "`n[VIEWS] Ejecutando tests de VISTAS..." -ForegroundColor Yellow
        python manage.py test lavado_auto.tests.test_views --verbosity=2
    }
    "integration" {
        Write-Host "`n[INTEGRATION] Ejecutando tests de INTEGRACION..." -ForegroundColor Yellow
        python manage.py test lavado_auto.tests.test_integration --verbosity=2
    }
    "coverage" {
        Write-Host "`n[COVERAGE] Ejecutando tests con COBERTURA..." -ForegroundColor Yellow
        coverage erase
        coverage run --source=. manage.py test lavado_auto
        Write-Host "`n[REPORT] Reporte de cobertura:" -ForegroundColor Cyan
        coverage report
        coverage html
        Write-Host "`n[OK] Reporte HTML generado en htmlcov/index.html" -ForegroundColor Green
    }
    "quick" {
        Write-Host "`n[QUICK] Ejecutando tests rapidos (sin integracion)..." -ForegroundColor Yellow
        python manage.py test lavado_auto.tests.test_models lavado_auto.tests.test_forms --verbosity=1
    }
    default {
        Write-Host "[ERROR] Opcion no valida" -ForegroundColor Red
        Write-Host "Opciones disponibles: all, models, forms, views, integration, coverage, quick"
    }
}

Write-Host "`n[OK] Tests completados!" -ForegroundColor Green
