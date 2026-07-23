# Script de Respaldo para Happy Vision
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm"
$backupDir = "$PSScriptRoot\Backups"
$backupName = "HappyVision_Backup_$fecha.zip"
$destPath = Join-Path $backupDir $backupName

if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

Write-Host "Iniciando respaldo de Happy Vision..." -ForegroundColor Cyan

try {
    # Lista de carpetas/archivos a ignorar
    $exclude = @("Backups", "node_modules", ".git", "__pycache__", ".venv", ".gemini")

    # Obtenemos los elementos de la carpeta actual (no recursivo aquí para filtrar fácil)
    $items = Get-ChildItem -Path $PSScriptRoot | Where-Object { $exclude -notcontains $_.Name }

    # Comprimir
    Compress-Archive -Path $items.FullName -DestinationPath $destPath -Force
    
    Write-Host "Respaldo completado con exito en: $destPath" -ForegroundColor Green
} catch {
    Write-Host "Error en el respaldo: $($_.Exception.Message)" -ForegroundColor Red
}
