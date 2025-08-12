@echo off
REM Script para marcar automáticamente las reservas como completadas
REM Este script debe ejecutarse cada hora o según la frecuencia deseada

cd /d "c:\Users\du28f\Downloads\PROJECT DJANGO\AUTONEW-DJANGO"

REM Activar el entorno virtual si existe
if exist "venvautonew\Scripts\activate.bat" (
    call venvautonew\Scripts\activate.bat
)

REM Ejecutar el comando de Django
echo [%date% %time%] Ejecutando comando para marcar reservas completadas...
python manage.py marcar_completadas --horas=4

REM Log de la ejecución
echo [%date% %time%] Comando ejecutado >> logs\auto_completar_reservas.log

pause
