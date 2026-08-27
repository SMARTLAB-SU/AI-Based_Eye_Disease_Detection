# Output Directory Structure & Diagnostic Visualizations

[![Google Drive Video](https://img.shields.io/badge/Google%20Drive-Watch%20Demo%20Video-red?style=for-the-badge&logo=googledrive&logoColor=white)](https://drive.google.com/file/d/1i_NHpuDHJY7bcHjHUrK5iOLCYtxX1rgb/view?usp=drive_link)

This directory contains generated diagnostic output images, model prediction heatmaps, real-time camera feed results, video demonstrations, and clinical report previews produced by the **VisionAI Eye Disease Detection System**.

---

## 🎥 Output Demonstration Video

Watch the complete real-time application demonstration, live fundus detection, and multi-model screening video:  
👉 **[Watch VisionAI Output Demo Video on Google Drive](https://drive.google.com/file/d/1i_NHpuDHJY7bcHjHUrK5iOLCYtxX1rgb/view?usp=drive_link)**

---

## 📁 Output Folder Structure

```
Output/
├── 📂 Output_Imgs/                      # Generated visual prediction outputs & GUI screenshots
│   ├── 🖼️ visionai_interface_idle.png  # Main desktop interface in ready state
│   └── 🖼️ visionai_detection_result.png# Live AI fundus diagnosis result (Cataract 90.1%)
└── 📄 README.md                         # Documentation of output formats & results
```

---

## 🖼️ Application Interface & Detection Results

### 1. Main Application Desktop Interface (Idle / Initializing State)
The primary clinical GUI featuring multi-model architecture selection (Swin Transformer, EfficientNetV2, FNet, Perceiver), dual-pane feed (Live Camera / Input vs. Disease Detection AI), patient ID entry, and action controls (Save, Load Video, Start Camera, Pause, Capture).

![VisionAI Interface Idle](Output_Imgs/visionai_interface_idle.png)

---

### 2. Live Fundus AI Pathology Detection Result
Demonstration of real-time fundus photograph analysis. The AI system segments retinal features and computes multi-class probability scores (e.g., **Cataract 90.1%** confidence), updating the patient record and status panel dynamically.

![VisionAI Detection Result](Output_Imgs/visionai_detection_result.png)

---

## 📋 Generated Output Formats

1. **Output Images (`Output_Imgs/*.png`)**:
   - High-resolution annotated fundus scans with diagnostic overlays.
   - Screenshots of diagnostic runs for patient records.
2. **Patient Records & Reports**:
   - Text reports summarizing top-3 class confidences and diagnostic metrics.
   - Structured JSON records (`result_YYYY-MM-DD.json`) for clinical EHR integration.

