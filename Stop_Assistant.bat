@echo off
echo Stopping the AI Assistant...
powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python' -and $_.CommandLine -match 'main_v2.py' } | Invoke-CimMethod -MethodName Terminate"
echo.
echo The AI Assistant has been completely turned off!
pause
