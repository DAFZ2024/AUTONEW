@echo off
REM Script para ejecutar tests en Windows (CMD)
REM Uso: run_tests.bat [opcion]

echo.
echo ========================================
echo    AUTONEW - Suite de Pruebas
echo ========================================
echo.

if "%1"=="" goto all
if "%1"=="all" goto all
if "%1"=="models" goto models
if "%1"=="forms" goto forms
if "%1"=="views" goto views
if "%1"=="integration" goto integration
if "%1"=="coverage" goto coverage
goto invalid

:all
echo Ejecutando TODOS los tests...
python manage.py test lavado_auto --verbosity=2
goto end

:models
echo Ejecutando tests de MODELOS...
python manage.py test lavado_auto.tests.test_models --verbosity=2
goto end

:forms
echo Ejecutando tests de FORMULARIOS...
python manage.py test lavado_auto.tests.test_forms --verbosity=2
goto end

:views
echo Ejecutando tests de VISTAS...
python manage.py test lavado_auto.tests.test_views --verbosity=2
goto end

:integration
echo Ejecutando tests de INTEGRACION...
python manage.py test lavado_auto.tests.test_integration --verbosity=2
goto end

:coverage
echo Ejecutando tests con COBERTURA...
coverage erase
coverage run --source=. manage.py test lavado_auto
echo.
echo Generando reporte...
coverage report
coverage html
echo.
echo Reporte HTML generado en htmlcov\index.html
goto end

:invalid
echo Opcion no valida!
echo Opciones: all, models, forms, views, integration, coverage
goto end

:end
echo.
echo ========================================
echo Tests completados!
echo ========================================
pause
