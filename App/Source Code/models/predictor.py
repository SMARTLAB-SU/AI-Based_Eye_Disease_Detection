# ============================================================
# VisionAI - Eye Disease Detection System
# SMART - Sanjivani Multidisciplinary AI Research & Technology
# models/predictor.py - AI Inference Engine
# ============================================================

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2
from PIL import Image
from torchvision import transforms
from loguru import logger

# ── Disease Classes ────────────────────────────────────────
CLASSES = ["AMD", "Cataract", "Dementia", "Diabetes", "Glaucoma", "Normal"]

# ── Image Preprocessing ────────────────────────────────────
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]
IMAGE_SIZE    = 640

# ── Confidence Threshold ───────────────────────────────────
# Minimum confidence (0–100 scale) to consider prediction confident.
# Default set to 0.0 to ensure top prediction is always available for display.
CONFIDENCE_THRESHOLD = 0.0


class Predictor:
    """
    Runs AI inference on fundus images for eye disease detection.
    Supports single images, video frames, and live camera feeds.
    Returns top-3 predictions with confidence scores.
    """

    def __init__(self, model: nn.Module):
        """
        Initialise predictor with a loaded model.

        Args:
            model: Loaded PyTorch model already in eval() mode
        """
        self.model  = model
        self.device = next(model.parameters()).device
        self.transform = self._build_transform()
        logger.info(f"Predictor initialised on {self.device}")

    # ── Transform Pipeline ─────────────────────────────────
    def _build_transform(self) -> transforms.Compose:
        """
        Build image preprocessing pipeline.
        Resize → ToTensor → Normalize with ImageNet stats.
        """
        return transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])

    # ── Main Predict ───────────────────────────────────────
    def predict(self, frame: np.ndarray) -> list:
        """
        Run inference on a single BGR frame. Handles None frames safely.

        Args:
            frame: OpenCV BGR numpy array (H × W × 3) or None

        Returns:
            List of up to 3 predictions:
            [
                {"class": "AMD",      "confidence": 95.3, "index": 0},
                {"class": "Glaucoma", "confidence": 3.1,  "index": 4},
            ]
        """
        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
            return []

        try:
            tensor = self._preprocess(frame)

            with torch.no_grad():
                outputs       = self.model(tensor)
                probabilities = F.softmax(outputs, dim=1)

            probs   = np.atleast_1d(probabilities.squeeze().cpu().numpy())
            results = self._get_top_predictions(probs)
            return results

        except Exception as e:
            logger.error(f"Inference error: {e}")
            return []

    # ── Preprocess ─────────────────────────────────────────
    def _preprocess(self, frame: np.ndarray) -> torch.Tensor:
        if frame.ndim == 2:
            rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        elif frame.shape[2] == 4:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
        else:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb)
        tensor    = self.transform(pil_image)
        tensor    = tensor.unsqueeze(0).to(self.device)
        return tensor

    # ── Top Predictions ────────────────────────────────────
    def _get_top_predictions(self, probs: np.ndarray) -> list:
        probs = np.atleast_1d(probs)
        if probs.ndim > 1:
            probs = probs.flatten()
        
        num_items = min(len(CLASSES), len(probs))
        top_indices = np.argsort(probs)[::-1][:num_items]

        results = []
        for idx in top_indices:
            if idx < len(CLASSES):
                confidence = float(probs[idx] * 100)
                if confidence >= CONFIDENCE_THRESHOLD:
                    results.append({
                        "class":      CLASSES[idx],
                        "confidence": confidence,
                        "index":      int(idx),
                    })

        return results

    # ── Convenience Methods ────────────────────────────────
    def predict_image_path(self, image_path: str) -> list:
        if not image_path or not isinstance(image_path, str):
            return []
        frame = cv2.imread(image_path)
        if frame is None:
            logger.error(f"Cannot read image: {image_path}")
            return []
        return self.predict(frame)

    def is_confident(self, results: list, threshold: float = 50.0) -> bool:
        if not results:
            return False
        return results[0].get("confidence", 0.0) >= threshold

    def get_top_prediction(self, results: list) -> dict:
        if not results:
            return {"class": "Unknown", "confidence": 0.0, "index": -1}
        return results[0]