"""
VisionAI / HYPERLUMA - Model Inference & Evaluation Script (Version 2.0)
SMART - Sanjivani Multidisciplinary AI Research & Technology

Advanced evaluation and real-time inference engine supporting:
- Single-image inference with top-K probabilities and latency benchmarking
- Full dataset evaluation with multi-class metrics (Accuracy, Top-1/Top-3, Precision, Recall, F1, Confusion Matrix)
- Single architectures (Swin Transformer, EfficientNetV2-S, ResNeXt50, FNet, Perceiver IO)
- Weighted soft-voting ensemble models (*_ensemble.pth)
- Visual explainability / Grad-CAM class activation mapping
- Automated diagnostic quality check (illumination, contrast, blur)
"""

import os
import sys
import time
import json
import argparse
from typing import Dict, Any, List, Optional, Tuple

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

# ── Class Definitions & Constants ─────────────────────────────────
CLASSES = ["AMD", "Cataract", "Dementia", "Diabetes", "Glaucoma", "Normal"]
NUM_CLASSES = len(CLASSES)
DEFAULT_IMAGE_SIZE = 640
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


# ==================================================================
# ── Architectural Implementations (Self-Contained Fallbacks) ───────
# ==================================================================

class FNetBlock(nn.Module):
    """FNet block: 2D Fourier transform token mixing replacing self-attention."""
    def __init__(self, dim: int = 256, ff_dim: int = 1024):
        super().__init__()
        self.ln1 = nn.LayerNorm(dim)
        self.ln2 = nn.LayerNorm(dim)
        self.ff = nn.Sequential(
            nn.Linear(dim, ff_dim),
            nn.GELU(),
            nn.Linear(ff_dim, dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + torch.fft.fft(torch.fft.fft(self.ln1(x), dim=-1), dim=-2).real
        x = x + self.ff(self.ln2(x))
        return x


class FNet(nn.Module):
    """Custom FNet architecture for fundus image classification."""
    def __init__(
        self,
        img_size: int = 640,
        patch_size: int = 32,
        in_chans: int = 3,
        embed_dim: int = 256,
        ff_dim: int = 1024,
        num_blocks: int = 6,
        num_classes: int = NUM_CLASSES,
    ):
        super().__init__()
        self.patch_size = patch_size
        self.num_patches = (img_size // patch_size) ** 2
        patch_dim = in_chans * patch_size * patch_size

        self.embedding = nn.Linear(patch_dim, embed_dim)
        self.pos_embed = nn.Parameter(torch.zeros(1, self.num_patches, embed_dim))
        self.blocks = nn.Sequential(*[FNetBlock(embed_dim, ff_dim) for _ in range(num_blocks)])
        self.ln = nn.LayerNorm(embed_dim)
        self.head = nn.Linear(embed_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, C, H, W = x.shape
        p = self.patch_size
        x = x.unfold(2, p, p).unfold(3, p, p)
        x = x.contiguous().view(B, C, -1, p, p)
        x = x.permute(0, 2, 1, 3, 4).contiguous()
        x = x.view(B, -1, C * p * p)
        x = self.embedding(x) + self.pos_embed
        x = self.blocks(x)
        x = self.ln(x.mean(dim=1))
        return self.head(x)


class Perceiver(nn.Module):
    """Custom Perceiver IO with 128 latent bottleneck vectors."""
    def __init__(
        self,
        num_latents: int = 128,
        latent_dim: int = 256,
        num_heads: int = 8,
        ff_dim: int = 1024,
        num_blocks: int = 6,
        num_classes: int = NUM_CLASSES,
        patch_size: int = 32,
    ):
        super().__init__()
        self.latents = nn.Parameter(torch.randn(num_latents, latent_dim))
        self.patch_embed = nn.Conv2d(3, latent_dim, patch_size, patch_size)
        self.cross_attn = nn.ModuleList([
            nn.MultiheadAttention(latent_dim, num_heads, batch_first=True)
            for _ in range(num_blocks)
        ])
        self.ln = nn.LayerNorm(latent_dim)
        self.ff = nn.ModuleList([
            nn.Sequential(
                nn.Linear(latent_dim, ff_dim),
                nn.GELU(),
                nn.Linear(ff_dim, latent_dim),
            )
            for _ in range(num_blocks)
        ])
        self.head = nn.Linear(latent_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B = x.shape[0]
        patches = self.patch_embed(x)
        B, C, H, W = patches.shape
        byte_array = patches.flatten(2).permute(0, 2, 1)

        lat = self.latents.unsqueeze(0).expand(B, -1, -1)
        for attn, ffn in zip(self.cross_attn, self.ff):
            attn_out, _ = attn(lat, byte_array, byte_array)
            lat = lat + attn_out
            lat = lat + ffn(self.ln(lat))

        pooled = self.ln(lat.mean(dim=1))
        return self.head(pooled)


class EnsembleModel(nn.Module):
    """Weighted Soft Voting Ensemble combining two architectures."""
    def __init__(
        self,
        model_a: nn.Module,
        model_b: nn.Module,
        weight_a: float,
        model_a_name: str = "Model A",
        model_b_name: str = "Model B",
    ):
        super().__init__()
        self.model_a = model_a
        self.model_b = model_b
        self.weight_a = float(weight_a)
        self.weight_b = 1.0 - float(weight_a)
        self.model_a_name = model_a_name
        self.model_b_name = model_b_name
        self.is_ensemble = True
        self.is_probability_output = True

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out_a = self.model_a(x)
        out_b = self.model_b(x)
        p_a = out_a if getattr(self.model_a, "is_probability_output", False) else F.softmax(out_a, dim=1)
        p_b = out_b if getattr(self.model_b, "is_probability_output", False) else F.softmax(out_b, dim=1)
        return self.weight_a * p_a + self.weight_b * p_b


# ==================================================================
# ── Model Builder & Weight Loader ─────────────────────────────────
# ==================================================================

def infer_architecture_from_filename(weight_path: str) -> str:
    """Infers architecture identifier from weight filename."""
    base = os.path.basename(weight_path).lower()
    if "_ensemble" in base:
        return "ensemble"
    elif "swin" in base:
        return "swin_tiny_patch4_window7_224"
    elif "effnet" in base or "efficientnet" in base:
        return "tf_efficientnetv2_s"
    elif "resnext" in base:
        return "resnext50_32x4d"
    elif "fnet" in base:
        return "fnet"
    elif "perceiver" in base:
        return "perceiver"
    return "swin_tiny_patch4_window7_224"


def clean_state_dict(state_dict: dict) -> dict:
    """Removes 'module.' prefixes and unifies key patterns."""
    return {k.replace("module.", ""): v for k, v in state_dict.items()}


def build_single_model(arch: str, img_size: int = DEFAULT_IMAGE_SIZE) -> nn.Module:
    """Builds a single model given its architecture name."""
    if arch == "fnet":
        return FNet(img_size=img_size, num_classes=NUM_CLASSES)
    if arch == "perceiver":
        return Perceiver(num_classes=NUM_CLASSES)

    try:
        import timm
        supported_img_size = {"swin_tiny_patch4_window7_224", "tf_efficientnetv2_s", "resnext50_32x4d", "resnet50"}
        if arch in supported_img_size:
            try:
                return timm.create_model(arch, pretrained=False, num_classes=NUM_CLASSES, img_size=img_size)
            except (TypeError, ValueError):
                pass
        return timm.create_model(arch, pretrained=False, num_classes=NUM_CLASSES)
    except ImportError:
        raise ImportError("Package 'timm' is required to instantiate Swin/EfficientNet/ResNeXt. Please run: pip install timm")


def load_model_weights(weight_path: str, arch: Optional[str] = None, device: Optional[torch.device] = None) -> nn.Module:
    """
    Robust loader supporting both single-network weights and dual-model ensemble checkpoints.
    """
    if not os.path.exists(weight_path):
        raise FileNotFoundError(f"Model weight file not found at: {weight_path}")

    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if arch is None or arch == "auto":
        arch = infer_architecture_from_filename(weight_path)

    # Load raw checkpoint
    checkpoint = torch.load(weight_path, map_location=device, weights_only=False)

    # 1. Ensemble Checkpoint Handling
    if arch == "ensemble" or (isinstance(checkpoint, dict) and any(k.endswith("_state_dict") for k in checkpoint.keys())):
        state_keys = [k for k in checkpoint.keys() if k.endswith("_state_dict")]
        weight_keys = [k for k in checkpoint.keys() if k.startswith("w_")]

        if len(state_keys) >= 2:
            key_a, key_b = state_keys[0], state_keys[1]
            arch_a = infer_architecture_from_filename(key_a)
            arch_b = infer_architecture_from_filename(key_b)

            model_a = build_single_model(arch_a).to(device)
            model_b = build_single_model(arch_b).to(device)

            model_a.load_state_dict(clean_state_dict(checkpoint[key_a]), strict=False)
            model_b.load_state_dict(clean_state_dict(checkpoint[key_b]), strict=False)

            w_a = float(checkpoint[weight_keys[0]]) if weight_keys else 0.5
            ensemble = EnsembleModel(model_a, model_b, weight_a=w_a, model_a_name=arch_a, model_b_name=arch_b)
            ensemble.to(device).eval()
            return ensemble

    # 2. Single Model Handling
    model = build_single_model(arch).to(device)
    if isinstance(checkpoint, dict):
        if "model_state_dict" in checkpoint:
            state_dict = checkpoint["model_state_dict"]
        elif "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
        else:
            state_dict = checkpoint
        state_dict = clean_state_dict(state_dict)
        model.load_state_dict(state_dict, strict=False)
    else:
        model = checkpoint

    model.to(device).eval()
    return model


# ==================================================================
# ── Preprocessing & Image Quality Utilities ────────────────────────
# ==================================================================

def check_image_quality(image_bgr: np.ndarray) -> Dict[str, Any]:
    """Evaluates image lighting, contrast, and Laplacian blur score."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    is_valid = True
    notes = []
    if brightness < 30:
        is_valid = False
        notes.append("Under-exposed / dark")
    elif brightness > 240:
        is_valid = False
        notes.append("Over-exposed / washed out")
    if contrast < 10:
        is_valid = False
        notes.append("Low contrast")
    if blur_score < 50:
        notes.append("Potential motion blur")

    return {
        "is_valid": is_valid,
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "blur_score": round(blur_score, 2),
        "notes": "; ".join(notes) if notes else "Optimal diagnostic clarity"
    }


def preprocess_frame(
    frame_bgr: np.ndarray,
    img_size: int = DEFAULT_IMAGE_SIZE,
    apply_clahe: bool = False,
    center_crop_ratio: Optional[float] = None
) -> torch.Tensor:
    """Preprocesses OpenCV BGR frame into a normalized PyTorch tensor."""
    img = frame_bgr.copy()

    # Center crop if requested (strip borders)
    if center_crop_ratio and 0.0 < center_crop_ratio < 1.0:
        h, w = img.shape[:2]
        ch, cw = int(h * center_crop_ratio), int(w * center_crop_ratio)
        sy, sx = (h - ch) // 2, (w - cw) // 2
        img = img[sy:sy + ch, sx:sx + cw]

    # Optional CLAHE on Luminance channel
    if apply_clahe:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        img = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)

    transform = transforms.Compose([
        transforms.Resize((img_size, img_size), interpolation=transforms.InterpolationMode.LANCZOS),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])
    return transform(pil_img).unsqueeze(0)


# ==================================================================
# ── Explainability & Attention Heatmap (Grad-CAM Fallback) ────────
# ==================================================================

def generate_attention_overlay(
    model: nn.Module,
    input_tensor: torch.Tensor,
    original_bgr: np.ndarray,
    target_class_idx: int,
    alpha: float = 0.45
) -> np.ndarray:
    """
    Generates class-activation attention heatmap overlay for model prediction.
    Works seamlessly across CNNs, Transformers, and custom architectures.
    """
    model.eval()
    input_tensor = input_tensor.clone().requires_grad_(True)

    outputs = model(input_tensor)
    if getattr(model, "is_probability_output", False) or getattr(model, "is_ensemble", False):
        score = outputs[0, target_class_idx]
    else:
        probs = F.softmax(outputs, dim=1)
        score = probs[0, target_class_idx]

    model.zero_grad()
    score.backward(retain_graph=False)

    gradients = input_tensor.grad
    if gradients is not None:
        # Saliency / Gradient-based attention
        saliency = torch.max(torch.abs(gradients), dim=1)[0].squeeze().cpu().numpy()
        saliency = cv2.GaussianBlur(saliency, (15, 15), 0)
        saliency = (saliency - saliency.min()) / (saliency.max() - saliency.min() + 1e-8)
        heatmap = (saliency * 255).astype(np.uint8)
    else:
        # Fallback synthetic spatial activation
        h, w = input_tensor.shape[2:]
        heatmap = np.zeros((h, w), dtype=np.uint8)

    heatmap_resized = cv2.resize(heatmap, (original_bgr.shape[1], original_bgr.shape[0]))
    colored_heatmap = cv2.applyColorMap(heatmap_resized, cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(original_bgr, 1.0 - alpha, colored_heatmap, alpha, 0)
    return overlay


# ==================================================================
# ── Core Inference Engine (Single Image) ──────────────────────────
# ==================================================================

def predict_single_image(
    image_path: str,
    model: nn.Module,
    device: torch.device,
    top_k: int = 3,
    explain: bool = False,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """Runs high-performance inference on a single fundus image."""
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Input image not found: {image_path}")

    frame_bgr = cv2.imread(image_path)
    if frame_bgr is None:
        raise ValueError(f"OpenCV failed to decode image: {image_path}")

    quality = check_image_quality(frame_bgr)
    tensor = preprocess_frame(frame_bgr).to(device)

    # Benchmarking latency
    start_t = time.perf_counter()
    with torch.no_grad():
        outputs = model(tensor)
        if getattr(model, "is_probability_output", False) or getattr(model, "is_ensemble", False):
            probabilities = outputs
        else:
            probabilities = F.softmax(outputs, dim=1)

    inference_ms = (time.perf_counter() - start_t) * 1000.0
    probs_np = probabilities.squeeze().cpu().numpy().flatten()

    # Sort Top-K
    top_indices = np.argsort(probs_np)[::-1][:min(top_k, len(CLASSES))]
    predictions = []
    for idx in top_indices:
        predictions.append({
            "class": CLASSES[idx],
            "confidence": round(float(probs_np[idx] * 100), 2),
            "index": int(idx)
        })

    top_pred = predictions[0]

    # Save output visualization
    viz_path = None
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(image_path))[0]

        if explain:
            overlay = generate_attention_overlay(model, tensor, frame_bgr, top_pred["index"])
            viz_path = os.path.join(output_dir, f"{base_name}_explainability.png")
            cv2.imwrite(viz_path, overlay)
        else:
            # Annotated image with diagnostic banner
            annotated = frame_bgr.copy()
            label = f"{top_pred['class']} ({top_pred['confidence']}%) | {inference_ms:.1f}ms"
            cv2.rectangle(annotated, (0, 0), (annotated.shape[1], 40), (20, 20, 20), -1)
            cv2.putText(annotated, label, (15, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 128), 2)
            viz_path = os.path.join(output_dir, f"{base_name}_prediction.png")
            cv2.imwrite(viz_path, annotated)

    return {
        "status": "success",
        "image_path": image_path,
        "predicted_class": top_pred["class"],
        "confidence": top_pred["confidence"],
        "latency_ms": round(inference_ms, 2),
        "top_k": predictions,
        "quality": quality,
        "visualization_path": viz_path
    }


# ==================================================================
# ── Comprehensive Dataset Evaluation Mode ─────────────────────────
# ==================================================================

def evaluate_dataset(
    dataset_dir: str,
    model: nn.Module,
    device: torch.device,
    output_dir: str = "Output/Evaluation_Results"
) -> Dict[str, Any]:
    """
    Evaluates a full test dataset with standard class folder layout:
    dataset_dir/<CLASS_NAME>/<images>.jpg
    Computes Accuracy, Top-3, Precision, Recall, F1, and Confusion Matrix.
    """
    os.makedirs(output_dir, exist_ok=True)
    class_to_idx = {c.lower(): i for i, c in enumerate(CLASSES)}

    # Gather images
    samples = []
    for root, _, files in os.walk(dataset_dir):
        # Ignore nested redundant folders
        if "split_output" in root:
            continue
        folder_name = os.path.basename(root).lower()
        if folder_name in class_to_idx:
            c_idx = class_to_idx[folder_name]
            for f in files:
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                    samples.append((os.path.join(root, f), c_idx))

    if not samples:
        raise ValueError(f"No valid labeled images found in: {dataset_dir}")

    print(f"\n🚀 Running Evaluation v2 on {len(samples)} test images...")
    print(f"Dataset root: {dataset_dir}\n")

    y_true = []
    y_pred = []
    top3_correct = 0
    latencies = []

    for idx, (img_path, true_label) in enumerate(samples, 1):
        try:
            res = predict_single_image(img_path, model, device, top_k=3)
            pred_idx = res["top_k"][0]["index"]
            pred_top3_indices = [p["index"] for p in res["top_k"]]

            y_true.append(true_label)
            y_pred.append(pred_idx)
            latencies.append(res["latency_ms"])

            if true_label in pred_top3_indices:
                top3_correct += 1

            if idx % 25 == 0 or idx == len(samples):
                print(f"[{idx}/{len(samples)}] Progress: {(idx/len(samples)*100):.1f}% | Avg Latency: {np.mean(latencies):.1f}ms")
        except Exception as e:
            print(f"Error evaluating {img_path}: {e}")

    # Calculate metrics
    y_true_np = np.array(y_true)
    y_pred_np = np.array(y_pred)
    total = len(y_true_np)

    accuracy = float(np.mean(y_true_np == y_pred_np) * 100.0)
    top3_acc = float((top3_correct / total) * 100.0)

    # Confusion matrix
    conf_matrix = np.zeros((NUM_CLASSES, NUM_CLASSES), dtype=int)
    for t, p in zip(y_true_np, y_pred_np):
        conf_matrix[t, p] += 1

    # Per-class metrics
    per_class = {}
    f1_list = []
    for c_i, c_name in enumerate(CLASSES):
        tp = conf_matrix[c_i, c_i]
        fp = np.sum(conf_matrix[:, c_i]) - tp
        fn = np.sum(conf_matrix[c_i, :]) - tp
        support = int(np.sum(conf_matrix[c_i, :]))

        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        f1_list.append(f1)

        per_class[c_name] = {
            "precision": round(precision * 100, 2),
            "recall": round(recall * 100, 2),
            "f1_score": round(f1 * 100, 2),
            "support": support
        }

    macro_f1 = float(np.mean(f1_list) * 100.0)

    results = {
        "total_samples": total,
        "overall_accuracy": round(accuracy, 2),
        "top3_accuracy": round(top3_acc, 2),
        "macro_f1": round(macro_f1, 2),
        "mean_latency_ms": round(float(np.mean(latencies)), 2),
        "p95_latency_ms": round(float(np.percentile(latencies, 95)), 2),
        "per_class": per_class,
        "confusion_matrix": conf_matrix.tolist(),
        "classes": CLASSES
    }

    # Save summary report
    summary_txt = os.path.join(output_dir, "evaluation_report.txt")
    with open(summary_txt, "w") as f:
        f.write("=================================================================\n")
        f.write("      VisionAI / HYPERLUMA - Benchmark Evaluation Report v2.0    \n")
        f.write("=================================================================\n\n")
        f.write(f"Total Test Samples : {total}\n")
        f.write(f"Overall Accuracy   : {accuracy:.2f}%\n")
        f.write(f"Top-3 Accuracy     : {top3_acc:.2f}%\n")
        f.write(f"Macro F1-Score     : {macro_f1:.2f}%\n")
        f.write(f"Mean Latency (ms)  : {results['mean_latency_ms']} ms\n\n")
        f.write("PER-CLASS CLASSIFICATION REPORT:\n")
        f.write("-----------------------------------------------------------------\n")
        f.write(f"{'Class':<20} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<8}\n")
        f.write("-----------------------------------------------------------------\n")
        for c_name, m in per_class.items():
            f.write(f"{c_name:<20} {m['precision']:<12.2f} {m['recall']:<12.2f} {m['f1_score']:<12.2f} {m['support']:<8}\n")
        f.write("-----------------------------------------------------------------\n\n")
        f.write("CONFUSION MATRIX (Rows: True, Columns: Pred):\n")
        for row in conf_matrix:
            f.write("  " + "  ".join(f"{val:>5}" for val in row) + "\n")

    summary_json = os.path.join(output_dir, "evaluation_summary.json")
    with open(summary_json, "w") as f:
        json.dump(results, f, indent=4)

    print("\n" + "=" * 65)
    print(f"📊 Evaluation Complete!")
    print(f"  • Overall Accuracy : {accuracy:.2f}%")
    print(f"  • Top-3 Accuracy   : {top3_acc:.2f}%")
    print(f"  • Macro F1-Score   : {macro_f1:.2f}%")
    print(f"  • Mean Latency     : {results['mean_latency_ms']} ms")
    print(f"  • Report Saved     : {summary_txt}")
    print("=" * 65 + "\n")

    return results


# ==================================================================
# ── CLI Interface ─────────────────────────────────────────────────
# ==================================================================

def main():
    parser = argparse.ArgumentParser(
        description="VisionAI / HYPERLUMA - Inference & Evaluation Engine v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single-image prediction:
  python Evaluation/inference_v2.py --image sample.jpg --model Models/swin_scratch_best.pth

  # Single-image with Grad-CAM explainability heatmap:
  python Evaluation/inference_v2.py --image sample.jpg --model Models/swin_scratch_best.pth --explain

  # Ensemble model evaluation:
  python Evaluation/inference_v2.py --image sample.jpg --model Models/effnet_swin_ensemble.pth

  # Quantitative benchmark on a test dataset:
  python Evaluation/inference_v2.py --dataset path/to/test_folder --model Models/swin_scratch_best.pth
        """
    )
    parser.add_argument("--image", type=str, default=None, help="Path to input fundus image for inference")
    parser.add_argument("--dataset", type=str, default=None, help="Path to test dataset root for quantitative evaluation")
    parser.add_argument("--model", type=str, default="Models/swin_scratch_best.pth", help="Path to model weights (.pth)")
    parser.add_argument("--arch", type=str, default="auto", help="Architecture name (auto, swin, efficientnet, resnext, fnet, perceiver, ensemble)")
    parser.add_argument("--output", type=str, default="Output/Output_Imgs", help="Output directory for predictions and evaluation artifacts")
    parser.add_argument("--device", type=str, default="auto", choices=["auto", "cuda", "cpu"], help="Inference device")
    parser.add_argument("--explain", action="store_true", help="Generate attention / Grad-CAM explainability heatmap overlay")
    parser.add_argument("--top-k", type=int, default=3, help="Number of top predictions to report")
    parser.add_argument("--clahe", action="store_true", help="Apply CLAHE enhancement on input")

    args = parser.parse_args()

    # Determine device
    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)

    print(f"VisionAI Evaluation Engine v2.0 | Device: {device}")

    # Fallback weights resolution if relative path given
    model_path = args.model
    if not os.path.exists(model_path):
        candidates = [
            os.path.join("Models", os.path.basename(model_path)),
            os.path.join("..", "Models", os.path.basename(model_path)),
            os.path.join(os.path.dirname(__file__), "..", "Models", os.path.basename(model_path)),
        ]
        for c in candidates:
            if os.path.exists(c):
                model_path = c
                break

    if not os.path.exists(model_path):
        print(f"⚠️  Warning: Model weights file not found at '{args.model}'.")
        print("Please provide a valid path via --model <path_to_pth>.")
        sys.exit(1)

    print(f"Loading Model Weights: {model_path}")
    model = load_model_weights(model_path, arch=args.arch, device=device)

    # 1. Dataset Evaluation Mode
    if args.dataset:
        evaluate_dataset(args.dataset, model, device, output_dir=args.output)

    # 2. Single Image Inference Mode
    elif args.image:
        results = predict_single_image(
            args.image,
            model,
            device,
            top_k=args.top_k,
            explain=args.explain,
            output_dir=args.output
        )

        print("\n" + "=" * 55)
        print("🔍 INFERENCE RESULTS (Version 2.0):")
        print("=" * 55)
        print(f"Target Image   : {results['image_path']}")
        print(f"Top Prediction : {results['predicted_class']} ({results['confidence']}%)")
        print(f"Inference Time : {results['latency_ms']} ms")
        print(f"Image Quality  : {results['quality']['notes']}")
        print("\nTop-K Predictions:")
        for idx, pred in enumerate(results["top_k"], 1):
            bar = "█" * int(pred["confidence"] // 5)
            print(f"  {idx}. {pred['class']:<10} {pred['confidence']:>6.2f}%  | {bar}")
        if results.get("visualization_path"):
            print(f"\nArtifact Saved : {results['visualization_path']}")
        print("=" * 55 + "\n")

    else:
        print("No --image or --dataset specified. Running self-test on random fundus tensor...")
        dummy_frame = np.random.randint(50, 200, (640, 640, 3), dtype=np.uint8)
        dummy_path = os.path.join(args.output, "selftest_dummy.png")
        os.makedirs(args.output, exist_ok=True)
        cv2.imwrite(dummy_path, dummy_frame)
        res = predict_single_image(dummy_path, model, device, top_k=args.top_k, explain=args.explain, output_dir=args.output)
        print("Self-test succeeded:", res["predicted_class"], f"({res['confidence']}%) in", res["latency_ms"], "ms")


if __name__ == "__main__":
    main()
