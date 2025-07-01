# Script para iniciar el desarrollo con Tailwind CSS en modo watch
Write-Host "🚀 Iniciando desarrollo con Tailwind CSS..." -ForegroundColor Green

# Verificar que Node.js esté instalado
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js encontrado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Node.js no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "Por favor instala Node.js desde: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Cambiar al directorio del tema
Set-Location "C:\Users\du28f\Downloads\AUTONEW-DJANGO\theme"

# Verificar que las dependencias estén instaladas
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Instalando dependencias de Node.js..." -ForegroundColor Yellow
    npm install
}

# Ejecutar Tailwind en modo watch en segundo plano
Write-Host "👀 Iniciando Tailwind CSS en modo watch..." -ForegroundColor Cyan
Start-Process -FilePath "npm" -ArgumentList "run", "build-dev" -WindowStyle Minimized

# Esperar un momento para que se inicie
Start-Sleep -Seconds 2

# Cambiar al directorio raíz del proyecto
Set-Location "C:\Users\du28f\Downloads\AUTONEW-DJANGO"

# Mostrar mensajes informativos
Write-Host ""
Write-Host "✅ Tailwind CSS está ejecutándose en modo watch (ventana minimizada)" -ForegroundColor Green
Write-Host "📝 Los cambios en tus templates se compilarán automáticamente" -ForegroundColor Cyan
Write-Host ""
Write-Host "▶️  Iniciando servidor Django..." -ForegroundColor Yellow

# Iniciar el servidor Django
python manage.py runserver
