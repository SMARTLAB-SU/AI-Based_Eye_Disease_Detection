# AI-Based Eye Disease Detection System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch 2.0+](https://img.shields.io/badge/PyTorch-2.0%2B-orange.svg)](https://pytorch.org/)
[![PyQt GUI](https://img.shields.io/badge/PyQt-5%2F6-green.svg)](https://riverbankcomputing.com/software/pyqt/)
[![Kaggle Dataset](https://img.shields.io/badge/Kaggle-Fundus%20Split%20Dataset-blue?style=flat&logo=kaggle)](https://www.kaggle.com/datasets/bhadakwadeutkarsha/fundus-split-dataset)
[![Download .exe](https://img.shields.io/badge/Download-Standalone%20.exe-green?style=flat&logo=google-drive)](https://drive.google.com/file/d/1xaMlOsWCdlhos-P2b06rGy90uYbtYsTp/view?usp=drive_link)
[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)

An advanced multi-architecture AI system for real-time detection and screening of ocular pathologies (Age-Related Macular Degeneration, Cataract, Dementia-related retinal biomarkers, Diabetic Retinopathy, Glaucoma, and Normal controls). Developed under **SMART** (*Sanjivani Multidisciplinary AI Research & Technology*).

---

## 💾 Download Standalone Executable (.exe)
You can download the pre-compiled standalone Windows application (`VisionAI.exe`) directly from Google Drive:  
👉 **[Download VisionAI Executable (.exe) on Google Drive](https://drive.google.com/file/d/1xaMlOsWCdlhos-P2b06rGy90uYbtYsTp/view?usp=drive_link)**

---

## 📊 Dataset & Benchmark
The model training and evaluation rely on the preprocessed **Fundus Split Dataset** available on Kaggle:  
👉 **[Kaggle Fundus Split Dataset by Bhadakwade Utkarsha](https://www.kaggle.com/datasets/bhadakwadeutkarsha/fundus-split-dataset)**

For comprehensive dataset details, class distribution tables, augmentation details, and cleanup scripts, see **[Dataset/README.md](file:///c:/Users/Asus/OneDrive/Documents/VisionAI/Dataset/README.md)**.

---

## 📁 Repository Structure

```
project-root/
├── 📂 Dataset/
│   ├── 📄 README.md              # Detailed Fundus Split Dataset specs, class distribution, & Kaggle link
│   └── 📁 Report/                # Subfolder for dataset analysis reports
├── 📂 App/
│   ├── 📁 .exe/                  # Contains compiled application binary (VisionAI.exe)
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

## 🛠️ Building Standalone Installer (.exe)

1. Package the source code with PyInstaller:
   ```cmd
   pyinstaller --onefile "App/Source Code/main.py"
   ```
2. Compile `App/ISS/setup.iss` in **Inno Setup** to produce `VisionAI_Setup_v1.0.exe`.

---

## 📜 License & Citation

Developed by **SMARTLAB-SU** (*Sanjivani Multidisciplinary AI Research & Technology*).  
Licensed under the **MIT License**.
