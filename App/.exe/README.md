# VisionAI Executable & Installer Deployment Guide

[![Google Drive Download](https://img.shields.io/badge/Google%20Drive-Download%20VisionAI.exe-4285F4?style=for-the-badge&logo=googledrive&logoColor=white)](https://drive.google.com/file/d/16Th-DtZp_cpYqrK4i-ykCmb9EuGfhXJ-/view?usp=drive_link)

## ⚠️ Why standard `VisionAI.exe` might not open on direct download
If you download **only** `VisionAI.exe` without its accompanying dependency folders (`.dll` files, `Qt6` runtime, PyTorch C++ binaries, and `assets/`), the application will fail to launch due to missing runtime libraries.

To resolve this, we provide three build and distribution formats:

---

## 📥 Distribution Formats

### 1. 📦 Windows Installer (`VisionAI_Setup_v1.0.0.exe`) - **[RECOMMENDED]**
- **File Name**: `VisionAI_Setup_v1.0.0.exe` (built via Inno Setup [`App/ISS/setup.iss`](../ISS/setup.iss))
- **Documentation & Download Folder**: [`App/Installer/README.md`](../Installer/README.md)
- **How it works**: Automatic installer wizard. Installs all required PyTorch, OpenCV, and PyQt DLLs, sets up registry paths, creates Desktop & Start Menu shortcuts, and launches the app directly.
- **Link**: 👉 **[Download VisionAI Setup (.exe) on Google Drive](https://drive.google.com/file/d/16Th-DtZp_cpYqrK4i-ykCmb9EuGfhXJ-/view?usp=drive_link)**

### 2. ⚡ Single-File Standalone Executable (`VisionAI_Standalone.exe`)
- **File Name**: `VisionAI_Standalone.exe` (built via PyInstaller [`build_singlefile.spec`](../Source%20Code/Additional%20Files/build_singlefile.spec))
- **How it works**: Self-contained executable with all DLLs and runtime dependencies bundled inside one single file. Unpacks into temporary memory at launch and runs instantly without installation.

### 3. 📁 Portable ZIP Bundle (`VisionAI_v1.0_Portable.zip`)
- **How it works**: Unzip the folder to any location on Windows and double-click `dist/VisionAI/VisionAI.exe`. Keep all `.dll` files and subfolders in the same directory.

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
