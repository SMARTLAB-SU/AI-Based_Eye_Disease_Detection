# VisionAI Executable & Installer Deployment Guide

[![Google Drive Download](https://img.shields.io/badge/Google%20Drive-Download%20VisionAI.exe-4285F4?style=for-the-badge&logo=googledrive&logoColor=white)](https://drive.google.com/file/d/16Th-DtZp_cpYqrK4i-ykCmb9EuGfhXJ-/view?usp=drive_link)

## ⚠️ Critical Requirement: The `_internal` Folder
In modern PyInstaller builds (PyInstaller 6.0+), **all required Python libraries (`python3xx.dll`), PyTorch C++ binaries (`torch_python.dll`, `c10.dll`), OpenCV drivers (`cv2`), PyQt6 GUI plugins, and model weights are stored inside the `_internal/` subfolder**.

- ❌ **If you move or copy `VisionAI.exe` without the adjacent `_internal/` folder**, the application will immediately fail to open with missing DLL / library errors.
- ✅ **If using the folder version**, keep `VisionAI.exe` and `_internal/` in the same directory, or run `Launch_VisionAI.bat`.
- ✅ **If distributing a single file**, download the **[Windows Installer (`VisionAI_Setup_v1.0.0.exe`)](https://drive.google.com/file/d/16Th-DtZp_cpYqrK4i-ykCmb9EuGfhXJ-/view?usp=drive_link)** or **Single-File Standalone Executable (`VisionAI_Standalone.exe`)** where `_internal` is pre-packaged inside.

---

## 📥 Distribution Formats

### 1. 📦 Windows Installer (`VisionAI_Setup_v1.0.0.exe`) - **[RECOMMENDED]**
- **File Name**: `VisionAI_Setup_v1.0.0.exe` (built via Inno Setup [`App/ISS/setup.iss`](../ISS/setup.iss))
- **Documentation & Download Folder**: [`App/Installer/README.md`](../Installer/README.md)
- **How it works**: Automatic installer wizard. Automatically unpacks `_internal/`, PyTorch, OpenCV, PyQt DLLs, and model weights into `C:\Program Files\VisionAI\`, sets up registry paths, creates Desktop shortcuts, and launches the app directly.
- **Link**: 👉 **[Download VisionAI Setup (.exe) on Google Drive](https://drive.google.com/file/d/16Th-DtZp_cpYqrK4i-ykCmb9EuGfhXJ-/view?usp=drive_link)**

### 2. ⚡ Single-File Standalone Executable (`VisionAI_Standalone.exe`)
- **File Name**: `VisionAI_Standalone.exe` (built via PyInstaller [`build_singlefile.spec`](../Source%20Code/Additional%20Files/build_singlefile.spec))
- **How it works**: Self-contained executable with `_internal` and all runtime dependencies pre-packaged inside a single `.exe` file. Unpacks into temporary memory at launch and runs instantly without installation.

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
