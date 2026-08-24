# VisionAI Presentation Deck Slides & Script Outline

**Project Title:** VisionAI — AI-Based Multi-Class Eye Disease Detection System  
**Presenter:** Utkarsha Sandip Bhadakwade  
**Affiliation:** SMART (Sanjivani Multidisciplinary AI Research & Technology) Lab, Sanjivani College of Engineering, BTech CSE  

---

## 📽️ Slide Overview & Content Breakdown

### Slide 1: Title & Team Information
- **Title**: VisionAI — AI-Based Multi-Class Eye Disease Detection System
- **Presenter**: Prepared by Utkarsha Sandip Bhadakwade
- **Research Lab**: SMART (Sanjivani Multidisciplinary AI Research & Technology) Lab
- **Institution**: Sanjivani College of Engineering, BTech Computer Science & Engineering

---

### Slide 2: Problem Statement & Clinical Motivation
**Headline**: Early ocular screening prevents blindness but faces regional access bottlenecks.

- **Clinical Problem**:
  - Retinal diseases represent the leading cause of preventable vision loss globally.
  - Early detection of glaucoma, diabetic retinopathy, and macular degeneration allows clinicians to intervene prior to permanent optical nerve damage.
  - Conventional screening requires direct evaluation by trained ophthalmologists, creating severe bottlenecks in rural or resource-constrained facilities.
- **VisionAI Solution**:
  - VisionAI automates fundus photography classification into six discrete clinical classes.
  - **Core Technical Novelty**: Enhances weak visual cues by preprocessing fundus images across dual RGB + HSI (Hue-Saturation-Intensity) color spaces.
- **Workflow Comparison**:
  - **Traditional Clinical Path**: Requires specialized on-site doctors $\rightarrow$ Slower turnaround times $\rightarrow$ Inaccessible in remote/rural locations.
  - **VisionAI Automated Screening**: Automated computer-vision diagnosis $\rightarrow$ Edge deployment via local hardware $\rightarrow$ Point-of-care results in seconds.

---

### Slide 3: Dataset Curation & Class Balancing
**Headline**: Balanced dataset curates 974 fundus images across six disease classes.

- **Dataset Curation Strategy**:
  - Raw data: 1,086 clinical fundus images across six diagnostic categories.
  - Pruned redundant frames using SSIM (Structural Similarity Index Measure) in overrepresented classes.
  - Balanced underrepresented classes (e.g., Diabetic Retinopathy) using careful image augmentation.
  - Final model-ready dataset: 974 high-resolution annotated images.
  - Stratified split: 70% Training, 15% Validation, and 15% Testing partitions.
  - Fully trained and preprocessed utilizing Kaggle and Google Colab accelerators.
- **Raw Class Breakdown**:
  - Dementia: 397 images (majority class, pruned via SSIM)
  - Cataract: 333 images (majority class, pruned via SSIM)
  - AMD (Age-related Macular Degeneration): 112 images
  - Glaucoma: 105 images
  - Normal Retinal Fundus: 76 images
  - Diabetic Retinopathy (DR): 63 images (augmented)

---

### Slide 4: Model Architectural Search & Benchmark Results
**Headline**: Swin Transformer outperforms convolutional networks at 99.33% accuracy.

- **Architectural Benchmark Strategy**:
  - Conducted architecture search across 7 DL families: Convolutional (ResNet, ConvNeXt), Attention (ViT, Perceiver IO), MLP-mixers (gMLP, WaveMLP), and Fourier-mixing (FNet).
  - Carried forward 5 finalist models for comprehensive end-to-end training and downstream application integration.
  - Each finalist architecture was trained to convergence on clean stratified sets.
  - Swin Transformer achieved state-of-the-art results, recording 99.33% test accuracy.
  - Hierarchical self-attention in Swin Transformer captures highly complex, multi-scale retinal textures.

- **Model Evaluation Matrix**:

| Architecture | Test Accuracy | Parameters | Notes |
| :--- | :--- | :--- | :--- |
| **Swin Transformer** | **99.33%** | **28M** | Hierarchical Vision Transformer (Best Performing) |
| **EfficientNetV2-S** | **94.63%** | Lightweight | Fast Convolutional Backbone |
| **ResNeXt50** | **87.92%** | Standard | Grouped Convolution Baseline |
| **FNet** | Exported `.pth` | Ultra-fast | Fourier-mixing zero-parameter token mixer |
| **Perceiver IO** | Exported `.pth` | Latent Bottleneck | Cross-attention latent bottleneck |

*\* FNet and Perceiver IO architectures were also successfully exported as runnable `.pth` files to the application for evaluation versatility.*

---

### Slide 5: PyQt6 Desktop Application & Multi-Threaded GUI
**Headline**: Responsive PyQt6 application houses all five trained models for clinical screening.

- **Application Highlights**:
  - A working clinical desktop application was successfully implemented using the PyQt6 framework.
  - Designed a multi-threaded architecture: deep learning inference runs in the background, keeping camera previews and UI responsive.
  - Integrated dropdown enables immediate, hot-swapping between all 5 trained `.pth` models during active screening.
  - Interactive UI displays general classifications alongside 5 independent per-class disease detection probability bars.
  - Clinicians can input Patient IDs and save logs containing inference images and detection metadata.
- **Graphic Interface Layout**:
  - Header: VisionAI — Multi-Class Retinal Diagnostic Interface v1.0
  - Left Panel: Live Fundus Camera Preview (Multi-threaded Feed)
  - Right Panel: Diagnosis Output (Swin Transformer $\rightarrow$ Cataract: 99%, Glaucoma: 0%, Normal: 1%)
  - Action Controls: `[ Start Camera ]` `[ Load Video ]` `[ CAPTURE ]` `[ SAVE LOG ]`

---

### Slide 6: Edge Hardware Deployment (Raspberry Pi 5)
**Headline**: Lightweight software runs natively on budget edge hardware at the point-of-need.

- **Edge Implementation Details**:
  - Optimized PyTorch inference allows model execution on low-cost single-board computers.
  - Natively runs on a Raspberry Pi 5 hardware platform with zero external GPU dependencies.
  - Integrated with a compact, clinical 7-inch display to form a highly portable diagnostic terminal.
  - Enables completely offline screening with zero reliance on stable internet connections, cloud APIs, or specialized remote servers.
  - Drastically reduces setup expenses, allowing underserved healthcare centers to conduct instant retinal scans.
- **Portable Edge Terminal Architecture**:
  - **Raspberry Pi 5** (Core Processor, Offline Inference, Lightweight OS) $+$ **7-inch LCD Monitor** (Responsive GUI, Dropdown Model Select, Live Feed Overlay).
  - **Clinical Advantage**: Fully offline screening. Brings automated ocular diagnostics directly to points of care lacking permanent ophthalmologists.

---

### Slide 7: Future Scope & Conclusion
**Headline**: Future developments target clinical testing and broader pipeline refinement.

- **Summary of Achievements**:
  - Successfully established a complete pipeline: curated and balanced clinical data, conducted architecture search, and built responsive software.
  - Primary social mission is extending preventative care to communities lacking direct access to retinal specialists.
  - Integrated the high-performance Swin Transformer alongside 4 fallback architectures inside a portable framework.
- **Roadmap Milestones**:
  1. **Preprocessing**: Dual RGB + HSI representations optimize contrast.
  2. **Benchmark**: Swin Transformer records 99.33% accuracy.
  3. **Edge System**: Fully deployable on Raspberry Pi 5 / PyQt6.
  4. **Social Mission**: Closes diagnostic gaps in rural medical zones.
  - Ongoing optimizations will further reduce inference latency and overall file sizes on edge processors.
  - Future roadmaps plan for multi-clinic field testing to gather clinical feedback and refine interface designs.
