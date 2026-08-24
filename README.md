# AI-Based Eye Disease Detection System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch 2.0+](https://img.shields.io/badge/PyTorch-2.0%2B-orange.svg)](https://pytorch.org/)
[![PyQt GUI](https://img.shields.io/badge/PyQt-5%2F6-green.svg)](https://riverbankcomputing.com/software/pyqt/)
[![Kaggle Dataset](https://img.shields.io/badge/Kaggle-Fundus%20Split%20Dataset-blue?style=flat&logo=kaggle)](https://www.kaggle.com/datasets/bhadakwadeutkarsha/fundus-split-dataset)
[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)

An advanced multi-architecture AI system for real-time detection and screening of ocular pathologies (Age-Related Macular Degeneration, Cataract, Dementia-related retinal biomarkers, Diabetic Retinopathy, Glaucoma, and Normal controls). Developed under **SMART** (*Sanjivani Multidisciplinary AI Research & Technology*).

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
│   ├── 📁 .exe/                  # Placeholder for compiled application binary (.exe build outputs)
│   ├── 📂 Source Code/
│   │   ├── 🐍 main.py            # Main application source files
│   │   └── 📁 Additional Files/  # Configs, assets, helper resources
│   └── 📁 ISS/                   # Inno Setup Script or installer-related files
├── 📂 Output/
│   ├── 📁 Output_Imgs/           # Generated output images & visual prediction results
│   └── 📄 README.md              # Explains output folder structure
├── 📂 Evaluation/
│   └── 🐍 inference.py           # Script to run model inference/evaluation
├── 📄 requirements.txt           # Python dependencies
├── 📄 README.md                   # Top-level project overview, setup, usage instructions
└── 📂 Documentation/
    ├── 📁 Comprehensive_Doc/     # Detailed technical documentation
    └── 📁 PPT/                   # Presentation slides
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
2. Compile `App/ISS/setup.iss` in **Inno Setup** to produce `App/.exe/VisionAI_Setup_v1.0.exe`.

---

## 📜 License & Citation

Developed by **SMARTLAB-SU** (*Sanjivani Multidisciplinary AI Research & Technology*).  
Licensed under the **MIT License**.
