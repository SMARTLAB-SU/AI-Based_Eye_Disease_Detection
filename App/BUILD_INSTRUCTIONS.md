# App Build Instructions (.exe, .iss, .py)

## Overview
This folder contains the main application scripts (`.py`), installer setup configuration (`.iss`), and executable build specifications (`.exe`).

---

## 📁 App Components

- `main.py`: Main entry point for launching the PyQt interface.
- `setup.iss`: Inno Setup compilation script for packaging into a Windows desktop installer executable (`VisionAI_Setup_v1.0.exe`).
- `build_windows.bat`: One-click Windows build script invoking PyInstaller.
- `build.spec`: PyInstaller specification file detailing frozen dependencies and binary hooks.
- `requirements.txt`: Python package requirements.
- `models/`: PyTorch neural network architectures and model loader engines.
- `ui/`: GUI components and modern stylesheet system.
- `utils/`: Camera capture, image preprocessing, report generator, and patient save manager.

---

## 🛠️ Building Standalone Windows Executable (.exe)

### Step 1: Install PyInstaller & Dependencies
```bash
pip install -r requirements.txt
pip install pyinstaller
```

### Step 2: Run One-Click Build Script
```cmd
build_windows.bat
```
Alternatively, compile via PyInstaller manually:
```bash
pyinstaller build.spec
```

### Step 3: Build Installer Executable (.exe) via Inno Setup
1. Download and install [Inno Setup 6](https://jrsoftware.org/isinfo.php).
2. Open `setup.iss` in Inno Setup Compiler.
3. Click **Compile** (`Ctrl + F9`).
4. The generated installer `VisionAI_Setup_v1.0.exe` will be saved in `Output/`.
