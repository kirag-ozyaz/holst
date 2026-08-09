# PowerShell script to update Canvas.vue
$targetFile = "X:/Проект/Холст/frontend/src/components/Canvas.vue"
$backupFile = "X:/Проект/Холст/frontend/src/components/Canvas.vue.backup"

# Copy original to backup
Copy-Item $targetFile $backupFile -Force

Write-Host "Backup created at: $backupFile"
