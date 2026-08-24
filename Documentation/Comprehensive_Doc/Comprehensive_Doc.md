# Comprehensive Technical Documentation

## 1. System Architecture Overview
The VisionAI Eye Disease Detection System integrates multi-architecture deep learning backbones (EfficientNetV2, Swin Transformer, FNet, Perceiver) into a cross-platform PyQt desktop application.

## 2. Component Diagram
- **Dataset**: Preprocessing, augmentation pipelines, and EDA reports.
- **App**: Desktop UI, camera video feed integration, patient record storage, and report generator.
- **Evaluation**: Inference scripts and performance metric calculators.
- **Output**: Visual output heatmaps and diagnostic reports.

## 3. Hardware Deployment Strategies
- Optimized for Windows desktop workstations and SBC edge devices (Raspberry Pi 5) with OpenMP thread capping and FP16 inference modes.
