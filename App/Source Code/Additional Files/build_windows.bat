@echo off
rem ============================================================
rem VisionAI - Eye Disease Detection System
rem SMART - Sanjivani Multidisciplinary AI Research & Technology
rem build_windows.bat - Compiles PyInstaller and Inno Setup
rem ============================================================

echo ============================================================
echo           Building VisionAI Windows Executables
echo ============================================================

rem 1. Check Python and install PyInstaller if missing
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller is not installed. Installing via pip...
    pip install pyinstaller
)

rem 2. Run PyInstaller for Folder Bundle (contains _internal folder)
echo Cleaning old build artifacts...
rmdir /s /q "build" 2>nul
rmdir /s /q "dist" 2>nul
echo Running PyInstaller with build.spec...
python -m PyInstaller -y --clean --workpath "%LOCALAPPDATA%\Temp\VisionAI_build" "%~dp0build.spec"
if %errorlevel% neq 0 (
    echo Error: PyInstaller folder build failed!
    exit /b %errorlevel%
)
echo PyInstaller folder build completed successfully.

rem 3. Run PyInstaller for Single-File Standalone Executable (bundles _internal inside .exe)
echo Running PyInstaller with build_singlefile.spec...
python -m PyInstaller -y --clean --workpath "%LOCALAPPDATA%\Temp\VisionAI_single_build" "%~dp0build_singlefile.spec"
if %errorlevel% neq 0 (
    echo Warning: Single-file build encountered an issue. Folder build remains available.
) else (
    echo PyInstaller single-file build completed successfully (dist\VisionAI_Standalone.exe).
)

echo Copying weight files to build directories...
if exist "..\..\Models" (
    xcopy /e /i /y "..\..\Models" "dist\VisionAI\Models"
    xcopy /e /i /y "..\..\Models" "dist\VisionAI\_internal\Models"
)

echo Copying launcher batch script...
if exist "..\Launch_VisionAI.bat" (
    copy /y "..\Launch_VisionAI.bat" "dist\VisionAI\Launch_VisionAI.bat"
)

echo Creating Portable ZIP Archive with _internal folder...
powershell -Command "Compress-Archive -Path 'dist\VisionAI\*' -DestinationPath 'dist\VisionAI_v1.0_Portable.zip' -Force"

echo Copying VisionAI folder to Desktop...
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

rem 4. Build Inno Setup Installer (packs _internal into setup.exe)
echo Locating Inno Setup Compiler (ISCC.exe)...
set "ISCC_PATH="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"

if defined ISCC_PATH (
    echo Found Inno Setup at: "%ISCC_PATH%"
    echo Compiling installer package...
    "%ISCC_PATH%" "%~dp0..\ISS\setup.iss"
) else (
    echo WARNING: Inno Setup compiler ISCC.exe not found.
    echo Portable folder bundle (with _internal): dist\VisionAI\
    echo Portable ZIP archive: dist\VisionAI_v1.0_Portable.zip
    echo Single-file standalone executable: dist\VisionAI_Standalone.exe
)

echo ============================================================
echo Build successful!
echo Portable folder: dist\VisionAI\ (Must keep _internal folder!)
echo Portable ZIP archive: dist\VisionAI_v1.0_Portable.zip
echo Single-file standalone: dist\VisionAI_Standalone.exe
echo ============================================================
