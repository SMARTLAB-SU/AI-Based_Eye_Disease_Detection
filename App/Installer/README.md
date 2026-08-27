# VisionAI Standalone Windows Installer

[![Download Windows Installer](https://img.shields.io/badge/Google%20Drive-Download%20VisionAI_Setup.exe-4285F4?style=for-the-badge&logo=googledrive&logoColor=white)](https://drive.google.com/file/d/16Th-DtZp_cpYqrK4i-ykCmb9EuGfhXJ-/view?usp=drive_link)

## 📥 Direct Installer Download
You can download the pre-compiled, standalone Windows installation wizard (`VisionAI_Setup_v1.0.0.exe`) directly from Google Drive:

👉 **[Download VisionAI Setup (.exe) on Google Drive](https://drive.google.com/file/d/16Th-DtZp_cpYqrK4i-ykCmb9EuGfhXJ-/view?usp=drive_link)**

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
