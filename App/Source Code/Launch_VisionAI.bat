@echo off
rem ============================================================
rem VisionAI - Eye Disease Detection System Launcher
rem Opens the installation directory in File Explorer and launches VisionAI
rem ============================================================

echo Opening VisionAI folder...
start "" explorer.exe "%~dp0"

echo Launching VisionAI application...
if exist "%~dp0VisionAI.exe" (
    start "" "%~dp0VisionAI.exe"
) else if exist "%~dp0VisionAI_Standalone.exe" (
    start "" "%~dp0VisionAI_Standalone.exe"
) else if exist "%~dp0dist\VisionAI\VisionAI.exe" (
    start "" "%~dp0dist\VisionAI\VisionAI.exe"
) else (
    python "%~dp0main.py"
)
