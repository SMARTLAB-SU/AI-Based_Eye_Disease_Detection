# ChatGPT Generated Technical Documentation & Architecture Analysis

## 1. Project Background
This document consolidates architectural recommendations, prompt design records, model comparison strategies, and hardware optimization blueprints generated during technical discussions for the **AI-Based Eye Disease Detection System**.

---

## 2. Clinical Scope & Pathology Definitions
The system is designed to perform screening and diagnostic support across six distinct ocular & systemic biomarker categories:

1. **AMD (Age-Related Macular Degeneration)**: Detects drusen, geographic atrophy, and choroidal neovascularization in the macular region.
2. **Cataract**: Analyzes lens opacity and light scattering effects captured via fundus retroillumination.
3. **Dementia**: Evaluates retinal microvascular changes (arteriolar narrowing, venular dilation, vessel tortuosity) that correlate with cerebral microvascular health.
4. **Diabetic Retinopathy (Diabetes)**: Screens for microaneurysms, hemorrhages, hard exudates, and neovascularization.
5. **Glaucoma**: Measures optic disc optic cup ratio (CDR), neuroretinal rim thinning, and retinal nerve fiber layer (RNFL) loss.
6. **Normal Baseline**: Healthy control fundus image without detectable pathology.

---

## 3. Deep Learning Model Architectural Trade-Offs

| Model Family | Key Mechanism | Strengths | Memory / Compute |
| :--- | :--- | :--- | :--- |
| **EfficientNetV2-S** | Fused-MBConv & Neural Architecture Search | Outstanding parameter efficiency, fast CPU inference | ~21M params, low RAM footprint |
| **Swin Transformer** | Shifted Window Self-Attention | Captures global contextual relations across retinal structures | ~28M params, medium VRAM |
| **Custom FNet** | 2D Fast Fourier Transform (FFT) | Zero-parameter token mixing, ultra-fast latency | ~6M params, minimal VRAM |
| **Perceiver** | Latent Cross-Attention Array | Fixed memory footprint regardless of input resolution | ~12M params, medium RAM |
| **ResNeXt50** | Grouped Convolutions (Cardinality) | Strong baseline generalization for clinical features | ~25M params, balanced |

---

## 4. Raspberry Pi 5 & Windows SBC Optimization
- **Thread Count Capping**: Restricting OpenMP, MKL, OpenBLAS threads (`OMP_NUM_THREADS=2`) prevents thermal throttling during long continuous operation.
- **DPI Scaling Overrides**: Enforcing 1:1 metric scale factors eliminates UI distortive stretching across embedded touchscreens.
- **PyQt Cross-Platform Bridge**: Abstracted import fallback supporting both PyQt5 and PyQt6 environments cleanly.
