# VisionAI Executable & Installer Deployment Guide

[![GitHub Release Download](https://img.shields.io/badge/GitHub-Download%20VisionAI_Standalone.exe-2EA043?style=for-the-badge&logo=github&logoColor=white)](https://github.com/SMARTLAB-SU/AI-Based_Eye_Disease_Detection/releases/download/v1.0.0/VisionAI_Standalone.exe)

## 📥 Distribution Formats

### 1. ⚡ Single-File Standalone Executable (`VisionAI_Standalone.exe`) - **[RECOMMENDED]**
- **File Name**: `VisionAI_Standalone.exe` (built via PyInstaller [`build_singlefile.spec`](../Source%20Code/Additional%20Files/build_singlefile.spec))
- **How it works**: Self-contained executable with `_internal` and all runtime dependencies pre-packaged inside a single `.exe` file. Unpacks into temporary memory at launch and runs instantly without installation.
- **Link**: 👉 **[Download VisionAI Standalone Executable (.exe) on GitHub](https://github.com/SMARTLAB-SU/AI-Based_Eye_Disease_Detection/releases/download/v1.0.0/VisionAI_Standalone.exe)**

### 2. 📦 Windows Installer (`VisionAI_Setup_v1.0.0.exe`)
- **File Name**: `VisionAI_Setup_v1.0.0.exe` (built via Inno Setup [`App/ISS/setup.iss`](../ISS/setup.iss))
- **Documentation & Download Folder**: [`App/Installer/README.md`](../Installer/README.md)
- **How it works**: Automatic installer wizard. Automatically unpacks `_internal/`, PyTorch, OpenCV, PyQt DLLs, and model weights into `C:\Program Files\VisionAI\`, sets up registry paths, creates Desktop shortcuts, and launches the app directly.

### 3. 📁 Portable ZIP Bundle (`VisionAI_v1.0_Portable.zip`)
- **How it works**: Unzip `VisionAI_v1.0_Portable.zip` to any location on Windows and double-click `VisionAI.exe` or `Launch_VisionAI.bat`. Ensure `_internal/`, `Models/`, and `assets/` remain in the same folder.

---

## 🛠️ Building Executables Locally

To compile the executables yourself on Windows:
```cmd
cd "App\Source Code\Additional Files"
build_windows.bat
```

This generates:
- `dist/VisionAI/` (Portable folder bundle)
- `dist/VisionAI_Standalone.exe` (Single-file executable)
- `Output/VisionAI_Setup_v1.0.0.exe` (Inno Setup Installer)
