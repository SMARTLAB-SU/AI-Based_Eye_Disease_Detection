# AI-Based Eye Disease Detection System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch 2.0+](https://img.shields.io/badge/PyTorch-2.0%2B-orange.svg)](https://pytorch.org/)
[![PyQt GUI](https://img.shields.io/badge/PyQt-5%2F6-green.svg)](https://riverbankcomputing.com/software/pyqt/)
[![Google Drive Dataset](https://img.shields.io/badge/Google%20Drive-Fundus%20Split%20Dataset-blue?style=flat&logo=google-drive)](https://drive.google.com/file/d/1wyRIKuoaXqGL9TvGiex1dO16UHqbs7F1/view?usp=sharing)
[![Download .exe](https://img.shields.io/badge/Download-Standalone%20.exe-green?style=flat&logo=github)](https://github.com/SMARTLAB-SU/AI-Based_Eye_Disease_Detection/releases/download/v1.0.0/VisionAI_Standalone.exe)
[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)

An advanced multi-architecture AI system for real-time detection and screening of ocular pathologies (Age-Related Macular Degeneration, Cataract, Dementia-related retinal biomarkers, Diabetic Retinopathy, Glaucoma, and Normal controls). Developed under **SMART** (*Sanjivani Multidisciplinary AI Research & Technology*).

---

## 💾 Download Standalone Executable & Windows Setup Installer (.exe)
Choose between the step-by-step setup installer wizard or the instant portable executable:

1. 📦 **Windows Setup Installer Wizard (`VisionAI_Setup_v1.0.0.exe`)**  
   - 👉 **[Download Setup Installer (.exe) on GitHub](https://github.com/SMARTLAB-SU/AI-Based_Eye_Disease_Detection/releases/download/v1.0.0/VisionAI_Setup_v1.0.0.exe)**  
   - Launches interactive setup wizard, installs VisionAI to PC, and creates Desktop Shortcuts.  
   - Documentation & Setup Guide: **[`App/Installer/README.md`](App/Installer/README.md)**

2. ⚡ **Standalone Portable Executable (`VisionAI_Standalone.exe`)**  
   - 👉 **[Download Standalone Executable (.exe) on GitHub](https://github.com/SMARTLAB-SU/AI-Based_Eye_Disease_Detection/releases/download/v1.0.0/VisionAI_Standalone.exe)**  
   - Single-file portable package. Unpacks into memory and runs instantly without installation steps.  
   - Documentation & Build Specifications: **[`App/.exe/README.md`](App/.exe/README.md)**

---

## 📊 Dataset & Benchmark
The model training and evaluation rely on the preprocessed **Fundus Split Dataset** available on Google Drive:  
👉 **[Download Fundus Split Dataset on Google Drive](https://drive.google.com/file/d/1wyRIKuoaXqGL9TvGiex1dO16UHqbs7F1/view?usp=sharing)**

For comprehensive dataset details, class distribution tables, augmentation details, and cleanup scripts, see **[Dataset/Report/README.md](Dataset/Report/README.md)**.

---

## 🎥 Output & Demonstration Video
Watch the official real-time screening demonstration video of the **VisionAI Eye Disease Detection System**:  
👉 **[Watch VisionAI Output Video Demonstration on Google Drive](https://drive.google.com/file/d/1i_NHpuDHJY7bcHjHUrK5iOLCYtxX1rgb/view?usp=drive_link)**  
*(For detailed output screenshots and diagnostic visualizations, see **[Output/README.md](Output/README.md)**)*

---

## ⚙️ Inno Setup Installer Script (.iss)
The standalone Windows installer compilation script (`setup.iss`) is available in the repository:  
👉 **[Inno Setup Installer Script (App/ISS/setup.iss)](App/ISS/setup.iss)** *(GitHub link: [App/ISS/setup.iss on GitHub](https://github.com/SMARTLAB-SU/AI-Based_Eye_Disease_Detection/blob/main/App/ISS/setup.iss))*

---

## 📁 Repository Structure

```
project-root/
├── 📂 Dataset/
│   ├── 📄 README.md              # Detailed Fundus Split Dataset specs, class distribution, & Google Drive link
│   └── 📁 Report/                # Subfolder for dataset analysis reports
├── 📂 Models/                 # Trained neural network model weights (.pth files)
│   ├── 🧠 swin_scratch_best.pth            # Swin Transformer weights (99.33% acc)
│   ├── 🧠 efficientnetv2s_scratch_best.pth  # EfficientNetV2-S weights (94.63% acc)
│   ├── 🧠 resnext50_scratch_best.pth        # ResNeXt50 weights (87.92% acc)
│   ├── 🧠 fnet_scratch_best.pth             # FNet weights
│   └── 🧠 perceiver_scratch_best.pth        # Perceiver IO weights
├── 📂 App/
│   ├── 📁 .exe/                  # Standalone executable download & PyInstaller specs
│   ├── 📁 Installer/             # Standalone Windows installer download & setup guide
│   ├── 📂 Source Code/
│   │   ├── 🐍 main.py            # Main application source code
│   │   ├── 📁 models/            # Neural network architectures & inference predictor
│   │   ├── 📁 ui/                # Desktop GUI components & stylesheet theme
│   │   ├── 📁 utils/             # Camera capture, image preprocessing, report generator
│   │   ├── 📁 assets/            # App icons, logos, and UI resources
│   │   └── 📁 Additional Files/  # Configs (config.json), build scripts, and specs
│   └── 📁 ISS/                   # Inno Setup installer script (setup.iss)
├── 📂 Output/
│   ├── 📁 Output_Imgs/           # Generated output images & visual prediction results
│   └── 📄 README.md              # Explains output folder structure
├── 📂 Evaluation/
│   └── 🐍 inference.py           # Script to run model inference/evaluation
├── 📄 requirements.txt           # Python dependencies
├── 📄 README.md                   # Top-level project overview, setup, usage instructions
└── 📂 Document/
    ├── 📁 Comprehensive_Doc/     # Comprehensive Technical Document & User Manual
    └── 📁 PPT/                   # Presentation slides deck & slide outline
```

---

## 🚀 Quick Start & Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/SMARTLAB-SU/AI-Based_Eye_Disease_Detection.git
cd AI-Based_Eye_Disease_Detection
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Model Evaluation / Inference
```bash
python Evaluation/inference.py --image sample.jpg --model weights/model.pth
```

### 5. Launch Main Application
```bash
python "App/Source Code/main.py"
```



---

## 📜 License & Citation

Developed by **SMARTLAB-SU** (*Sanjivani Multidisciplinary AI Research & Technology*).  
Licensed under the **MIT License**.
