# Registers a daily Windows Scheduled Task (default 8:00 AM local).
# Run PowerShell as your user (not necessarily admin).

param(
    [string]$TaskName = "LinkedInJobCrawler",
    [string]$Time = "08:00"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$runScript = Join-Path $ProjectRoot "scripts\run_daily.ps1"

if (-not (Test-Path $runScript)) {
    Write-Error "Missing run script: $runScript"
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runScript`""
$trigger = New-ScheduledTaskTrigger -Daily -At $Time
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
Write-Host "Registered scheduled task '$TaskName' daily at $Time"
Write-Host "Runner: $runScript"
