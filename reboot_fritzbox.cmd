@echo off
REM Double-click launcher for reboot_fritzbox.ps1
REM Runs the PowerShell script bypassing the execution policy, then waits.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0reboot_fritzbox.ps1"
echo.
pause
