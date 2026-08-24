# VisionAI: AI-Based Multi-Class Eye Disease Detection System
## Comprehensive Technical Document and User Manual

**Prepared by:** Utkarsha Sandip Bhadakwade  
**Affiliation:** BTech Computer Science Engineering, Sanjivani College of Engineering  

👉 **[Open Comprehensive Technical Document on Google Docs](https://docs.google.com/document/d/13xjcRQC-q0_Zfn4Xj0LLe38xXv7sa58B/edit?usp=drive_link&ouid=101955352870722335883&rtpof=true&sd=true)**

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Dataset and Preprocessing](#2-dataset-and-preprocessing)
3. [Model Architecture and Training](#3-model-architecture-and-training)
4. [Application Architecture](#4-application-architecture)
5. [Edge Deployment](#5-edge-deployment)
6. [User Manual](#6-user-manual)
   - [6.1 System Requirements](#61-system-requirements)
   - [6.2 Installation](#62-installation)
   - [6.3 Running a Screening](#63-running-a-screening)
   - [6.4 Interpreting Results](#64-interpreting-results)
   - [6.5 Troubleshooting](#65-troubleshooting)
7. [Repository Structure](#7-repository-structure)
8. [Conclusion](#8-conclusion)

---

## 1. Project Overview

Retinal disease is a leading cause of preventable vision loss, and early detection through fundus photography is one of the most effective ways to catch conditions such as glaucoma and diabetic retinopathy before irreversible damage occurs. In practice, this kind of screening depends on the availability of a trained ophthalmologist to read each image, which is not always feasible in rural or resource-limited settings where specialist access is scarce. VisionAI was developed to address this gap by automating fundus image classification, giving frontline health workers a tool that can flag likely disease categories without requiring a specialist to be physically present.

The system is built around a curated and balanced fundus image dataset, a comparative study across seven deep learning architectures, and a fully functional desktop application designed for practical, real-world use. It classifies fundus images into six categories: Age-related Macular Degeneration (AMD), Cataract, Dementia-related retinal changes, Diabetic Retinopathy, Glaucoma, and Normal (healthy) retina. A dual-channel RGB and Hue-Saturation-Intensity (HSI) preprocessing approach gives the models richer color and texture information than RGB alone, which is one of the project's core technical contributions alongside the multi-architecture comparison itself.

---

## 2. Dataset and Preprocessing

The dataset originated from a raw collection of 1,086 fundus images distributed unevenly across six disease classes. Raw class-wise counts were as follows: Cataract (333 images) and Dementia (397 images) were well represented, while Diabetic Retinopathy (63 images), Glaucoma (105 images), AMD (112 images), and Normal (76 images) were comparatively underrepresented. This imbalance was addressed through a combination of data augmentation for minority classes and Structural Similarity Index (SSIM)-based pruning to remove near-duplicate images from overrepresented classes, producing a final balanced dataset of 974 images.

Each image in the final dataset was split using a stratified 70/15/15 ratio across training, validation, and test sets, ensuring that class proportions were preserved across all three splits. A defining preprocessing step is the dual-channel pipeline: every fundus image is represented in both RGB and HSI color spaces, and both representations are supplied to the models during training. The HSI channel, in particular, tends to preserve vascular and lesion contrast that can be muted in RGB, giving the downstream classifiers additional discriminative signal. All heavy training and preprocessing work was carried out on Kaggle and Google Colab, which provided the GPU resources needed for repeated experimentation across seven candidate architectures.

### Raw Dataset Class Metrics

| Class | Raw Image Count |
| :--- | :--- |
| **AMD** | 112 |
| **Cataract** | 333 |
| **Dementia** | 397 |
| **Diabetic Retinopathy** | 63 |
| **Glaucoma** | 105 |
| **Normal** | 76 |

---

## 3. Model Architecture and Training

A broad architectural search preceded the final model selection. Candidates explored included ResNet, Vision Transformer (ViT), ConvNeXt, Perceiver IO, gMLP, FNet, and WaveMLP, representing convolutional, attention-based, and MLP-mixer design families respectively. This breadth of comparison was intended to identify which inductive biases best suited fundus image classification given the dataset's relatively modest size. From this search, five architectures were carried forward for full training and evaluation, each trained independently to convergence with its own weights exported as a separate `.pth` file.

| Architecture | Family | Test Accuracy | Parameters |
| :--- | :--- | :--- | :--- |
| **Swin Transformer** | Transformer (hierarchical) | **99.33%** | **28M** |
| **EfficientNetV2-S** | Convolutional | **94.63%** | — |
| **ResNeXt50** | Convolutional | **87.92%** | — |
| **FNet** | Fourier-mixing | — | — |
| **Perceiver IO** | Attention-based, latent bottleneck | — | — |

Swin Transformer is the best-performing model, reaching 99.33% test accuracy with 28M parameters, and is labeled as such in the application. EfficientNetV2-S follows at 94.63%, and ResNeXt50 at 87.92%. The application lets the user select which of the five trained models to run via a model dropdown, rather than locking the interface to a single fixed architecture.

---

## 4. Application Architecture

The user-facing component of VisionAI is a desktop application, titled "VisionAI — Eye Disease Detection System", built from scratch in PyQt6. The application loads all five trained `.pth` model weight files at startup, and the interface includes a "Select AI Model" dropdown that lets the user choose which of the five architectures runs the detection, with the currently selected model's accuracy and parameter count shown alongside it.

The main window is split into two live panels: a camera or uploaded-image feed on the left, and a "Disease Detection AI" output panel on the right, alongside five per-class detection status boxes below them. Controls include Start Camera and Load Video for bringing in footage, Capture and Pause for controlling the feed, and Save for storing results, together with a Patient ID field for associating a screening with a specific patient. A processing-progress bar and a "Model Ready" status indicator keep the user informed of the pipeline's state. Model inference runs on a background thread separate from the UI thread, keeping the interface responsive instead of freezing while predictions are generated.

---

## 5. Edge Deployment

To support low-cost, portable screening scenarios, VisionAI is designed to run on a Raspberry Pi 5 paired with a 7-inch display. This gives the system a compact, self-contained form factor suitable for deployment in resource-limited clinical settings, without requiring a full desktop or laptop setup on site.

---

## 6. User Manual

### 6.1 System Requirements
- A Windows desktop for the packaged application, or a Raspberry Pi 5 with a 7-inch display for the edge deployment
- The five trained `.pth` model weight files, present alongside the application's source code
- A camera feed, video file, or fundus image to screen

### 6.2 Installation
1. Copy the VisionAI application folder (containing the executable, source code, and the five `.pth` model weight files) to the target machine.
2. Ensure all five model weight files are present in the `Additional Files` directory alongside the source code — the application will not start correctly if any are missing.
3. Install the dependencies listed in `requirements.txt`, or run the packaged `.exe` directly on Windows.
4. Launch the application by running the executable, or by running the main PyQt6 entry-point script from the `Source Code` directory.

### 6.3 Running a Screening
1. Open the VisionAI application and wait for the status indicator to show **"Model Ready"**.
2. Use the **"Select AI Model"** dropdown to choose which of the five trained architectures should run the detection.
3. Enter the **Patient ID** for the person being screened.
4. Bring in the image source using **Start Camera** for a live feed or **Load Video** for a recorded file, then use **Capture** to grab the frame to analyze (**Pause** stops the feed at any point).
5. Review the prediction in the **Disease Detection AI** panel and the five per-class detection boxes below it, and check the **Processing Progress** bar for completion status.
6. Use **Save** to store the result against the entered Patient ID.

### 6.4 Interpreting Results
The application reports one of six classes for each screened image: AMD, Cataract, Dementia, Diabetic Retinopathy, Glaucoma, or Normal, with the five per-class boxes reflecting the detection status for each category. As with any AI-assisted screening tool, results should be treated as decision support rather than a definitive diagnosis, and should be reviewed by a qualified ophthalmologist before any clinical action is taken.

### 6.5 Troubleshooting
- **Application fails to start**: verify that all five `.pth` model files are present and unmodified in the expected directory.
- **Interface freezes during inference**: confirm the background inference thread is enabled; this should not occur under normal operation, as inference is designed to run off the main UI thread.
- **Unexpected or low-confidence predictions**: confirm the input image is a genuine fundus photograph, in focus, and consistent in framing with the training dataset.

---

## 7. Repository Structure

The project repository is organized to separate data, application code, evaluation tooling, and documentation into clearly delineated folders. `Dataset` holds the raw and processed fundus images along with dataset-level documentation. `App` contains the packaged executable, the PyQt6 source code, and additional resources including the five model weight files. `Output` stores generated inference images and results. `Evaluation` contains the inference script used to run and assess the models. `Document` holds this comprehensive document and the accompanying presentation.

---

## 8. Conclusion

VisionAI demonstrates a complete pipeline from imbalanced raw medical image data through to a deployable diagnostic support tool, combining careful dataset curation, a comparative architecture study across seven model families, and a responsive desktop application suitable for both conventional and edge deployment on the Raspberry Pi 5. The project's core aim, extending fundus screening access to settings without a readily available specialist, continues to guide ongoing refinement of the models and the application ahead of broader field testing.
