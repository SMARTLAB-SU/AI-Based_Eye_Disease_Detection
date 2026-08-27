# VisionAI Standalone Windows Installer

[![Download Windows Installer](https://img.shields.io/badge/GitHub-Download%20VisionAI_Setup.exe-2EA043?style=for-the-badge&logo=github&logoColor=white)](https://github.com/SMARTLAB-SU/AI-Based_Eye_Disease_Detection/releases/download/v1.0.0/VisionAI_Setup_v1.0.0.exe)

## 📥 Direct Installer Download
You can download the pre-compiled, standalone Windows installation wizard (`VisionAI_Setup_v1.0.0.exe`) directly from GitHub Releases:

👉 **[Download VisionAI Setup (.exe) on GitHub](https://github.com/SMARTLAB-SU/AI-Based_Eye_Disease_Detection/releases/download/v1.0.0/VisionAI_Setup_v1.0.0.exe)**

---

## ⚡ What Happens When You Run The Installer
1. **Automated Setup**: Double-clicking `VisionAI_Setup_v1.0.0.exe` launches the step-by-step setup wizard.
2. **Complete Dependency & `_internal/` Bundling**: Automatically installs all required PyTorch C++ binaries (`c10.dll`), Python runtime libraries, OpenCV vision drivers, PyQt6 GUI plugins, model weights (`Models/`), and assets into `{autopf}\VisionAI` (including the required `_internal/` subfolder).
3. **Dual Launch Shortcuts**: Automatically creates Desktop & Start Menu shortcuts:
   - 🚀 **`VisionAI App`**: Launches the VisionAI application directly.
   - 📂 **`VisionAI (Open Folder & App)`**: Opens the installation folder in Windows File Explorer and launches the app simultaneously.

---

## 🛠️ How to Compile the Installer Script (.iss)
The installer compilation script is available at [`App/ISS/setup.iss`](../ISS/setup.iss). To compile it locally using Inno Setup:
```cmd
cd "App\Source Code\Additional Files"
build_windows.bat
```
This will compile the folder bundle via PyInstaller and pack it into `Output/VisionAI_Setup_v1.0.0.exe`.
