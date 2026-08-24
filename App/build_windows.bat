@echo off
rem ============================================================
rem VisionAI - Eye Disease Detection System
rem SMART - Sanjivani Multidisciplinary AI Research & Technology
rem build_windows.bat - Compiles PyInstaller and Inno Setup
rem ============================================================

echo ============================================================
echo           Building VisionAI Windows Executable
echo ============================================================

rem 1. Check Python and install PyInstaller if missing
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller is not installed. Installing via pip...
    pip install pyinstaller
)

rem 2. Run PyInstaller
echo Cleaning old build artifacts...
rmdir /s /q "build" 2>nul
rmdir /s /q "dist" 2>nul
echo Running PyInstaller with build.spec...
python -m PyInstaller -y --clean --workpath "%LOCALAPPDATA%\Temp\VisionAI_build" build.spec
if %errorlevel% neq 0 (
    echo Error: PyInstaller build failed!
    exit /b %errorlevel%
)
echo PyInstaller build completed successfully.

echo Copying weight files to build directory...
xcopy /e /i /y "weights" "dist\VisionAI\weights"

echo Copying VisionAI to Desktop...
if exist "%USERPROFILE%\OneDrive\Desktop" (
    rmdir /s /q "%USERPROFILE%\OneDrive\Desktop\VisionAI" 2>nul
    xcopy /e /i /y "dist\VisionAI" "%USERPROFILE%\OneDrive\Desktop\VisionAI"
    echo Desktop copy ready: %USERPROFILE%\OneDrive\Desktop\VisionAI\VisionAI.exe
)
if exist "%USERPROFILE%\Desktop" (
    rmdir /s /q "%USERPROFILE%\Desktop\VisionAI" 2>nul
    xcopy /e /i /y "dist\VisionAI" "%USERPROFILE%\Desktop\VisionAI"
    echo Desktop copy ready: %USERPROFILE%\Desktop\VisionAI\VisionAI.exe
)

rem 3. Build Inno Setup Installer
echo Locating Inno Setup Compiler (ISCC.exe)...
set "ISCC_PATH="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"

if defined ISCC_PATH (
    echo Found Inno Setup at: "%ISCC_PATH%"
    echo Compiling installer package...
    "%ISCC_PATH%" setup.iss
) else (
    echo WARNING: Inno Setup compiler ISCC.exe not found.
    echo Standalone executable is available at: dist\VisionAI\VisionAI.exe
)

echo ============================================================
echo Build successful!
echo Standalone folder: dist\VisionAI\
echo ============================================================
