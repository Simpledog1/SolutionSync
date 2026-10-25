# Registers (or updates) the daily "SolutionSync Daily" task for the current user.
# Safe to run again: it replaces the existing task instead of creating a duplicate.
# Usage:  powershell -ExecutionPolicy Bypass -File scripts\install_task.ps1 [-Time 06:00]
param([string]$Time = "06:00")
$ErrorActionPreference = "Stop"

$TaskName = "SolutionSync Daily"
$Root = Split-Path -Parent $PSScriptRoot

# A stable interpreter path (not a temporary terminal setting). pythonw = no console window.
$Python = & py -3 -c "import sys; print(sys.executable)"
$PythonW = Join-Path (Split-Path $Python) "pythonw.exe"
if (Test-Path $PythonW) { $Python = $PythonW }
if (-not (Test-Path $Python)) { throw "Python was not found." }

# Task Scheduler uses this PC's clock. The app counts quota in Manila time on its own,
# but the start time only means "Manila time" if the PC is on UTC+08:00.
$tz = Get-TimeZone
if ($tz.BaseUtcOffset -ne [TimeSpan]::FromHours(8) -or $tz.SupportsDaylightSavingTime) {
    Write-Warning "PC time zone is $($tz.Id); $Time will be PC time, not Manila time."
}

$action = New-ScheduledTaskAction -Execute $Python -Argument "-m solsync run" -WorkingDirectory $Root
$user = "$env:USERDOMAIN\$env:USERNAME"
# Daily at $Time, plus 5 minutes after you sign in or unlock the PC. The extra starts catch
# runs missed or cut off by sleep/shutdown; once the day's limit is used they exit at once.
$daily = New-ScheduledTaskTrigger -Daily -At $Time
$logon = New-ScheduledTaskTrigger -AtLogOn -User $user
$logon.Delay = "PT5M"
$unlockClass = Get-CimClass -Namespace ROOT\Microsoft\Windows\TaskScheduler -ClassName MSFT_TaskSessionStateChangeTrigger
$unlock = New-CimInstance -CimClass $unlockClass -ClientOnly
$unlock.StateChange = 8   # 8 = session unlock
$unlock.UserId = $user
$unlock.Delay = "PT5M"
$unlock.Enabled = $true
$trigger = @($daily, $logon, $unlock)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
# Runs as you, only while you are signed in, without admin rights. That is what lets it
# use your saved Git and Exercism credentials. No password is stored in the task.
$principal = New-ScheduledTaskPrincipal -UserId $user `
    -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings `
    -Principal $principal -Force `
    -Description "Uploads up to the daily limit of completed HackerRank/Exercism solutions per day. See $Root\README.md" | Out-Null

$t = Get-ScheduledTask -TaskName $TaskName
$info = Get-ScheduledTaskInfo -TaskName $TaskName
Write-Output "Task:        $($t.TaskName) ($($t.State))"
Write-Output "Runs:        $($t.Actions[0].Execute) $($t.Actions[0].Arguments)"
Write-Output "In folder:   $($t.Actions[0].WorkingDirectory)"
Write-Output "Daily at:    $Time (PC time zone $($tz.Id)), plus 5 min after sign-in and unlock"
Write-Output "Triggers:    $(($t.Triggers | ForEach-Object { $_.CimClass.CimClassName -replace 'MSFT_Task|Trigger','' }) -join ', ')"
Write-Output "Next run:    $($info.NextRunTime)"
Write-Output "Catch-up:    $($t.Settings.StartWhenAvailable)  Overlap: $($t.Settings.MultipleInstances)"
Write-Output "Run level:   $($t.Principal.RunLevel)  Logon: $($t.Principal.LogonType)"
