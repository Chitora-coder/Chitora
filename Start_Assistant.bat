@echo off
cd /d "%~dp0"
powershell -Command "Start-Process -FilePath '.\venv\Scripts\python.exe' -ArgumentList 'main_v2.py' -WindowStyle Hidden"
