# ============================================================
# VisionAI - Eye Disease Detection System
# SMART - Sanjivani Multidisciplinary AI Research & Technology
# utils/preprocessing.py - Image Preprocessing Utilities
# ============================================================

import cv2
import numpy as np
from PIL import Image, ImageEnhance
from loguru import logger

# ── Constants ──────────────────────────────────────────────
IMAGE_SIZE    = 640
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]


class ImagePreprocessor:
    """
    Handles all image preprocessing for fundus images.
    Includes resizing, normalization, enhancement,
    and quality checks.
    """

    def __init__(self, target_size: int = IMAGE_SIZE):
        """
        Initialize preprocessor.

        Args:
            target_size: target image size (default 640x640)
        """
        self.target_size = target_size
        logger.info(f"ImagePreprocessor initialized — target size: {target_size}x{target_size}")

    # ── Main Preprocess ────────────────────────────────────
    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """
        Full preprocessing pipeline for a fundus image frame.

        Steps:
        1. Validate input
        2. Resize to target size
        3. Enhance contrast
        4. Normalize

        Args:
            frame: OpenCV BGR numpy array

        Returns:
            Preprocessed numpy array
        """
        if frame is None:
            raise ValueError("Input frame is None")

        # Validate
        frame = self._validate_frame(frame)

        # Resize
        frame = self._resize(frame)

        # Enhance
        frame = self._enhance(frame)

        return frame

    # ── Validate ───────────────────────────────────────────
    def _validate_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Validate and fix frame dimensions.

        Args:
            frame: input numpy array

        Returns:
            Valid numpy array
        """
        # Ensure 3 channels
        if len(frame.shape) == 2:
            # Grayscale to BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            logger.debug("Converted grayscale to BGR")

        elif frame.shape[2] == 4:
            # BGRA to BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            logger.debug("Converted BGRA to BGR")

        return frame

    # ── Resize ─────────────────────────────────────────────
    def _resize(self, frame: np.ndarray) -> np.ndarray:
        """
        Resize frame to target size using high quality interpolation.

        Args:
            frame: input BGR numpy array

        Returns:
            Resized numpy array
        """
        h, w = frame.shape[:2]
        if h != self.target_size or w != self.target_size:
            frame = cv2.resize(
                frame,
                (self.target_size, self.target_size),
                interpolation=cv2.INTER_LANCZOS4
            )
        return frame

    # ── Enhance ────────────────────────────────────────────
    def _enhance(self, frame: np.ndarray) -> np.ndarray:
        """
        Enhance fundus image quality using CLAHE
        (Contrast Limited Adaptive Histogram Equalization).
        Improves visibility of retinal features.

        Args:
            frame: BGR numpy array

        Returns:
            Enhanced BGR numpy array
        """
        try:
            # Convert to LAB color space
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)

            # Apply CLAHE to L channel only
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l_enhanced = clahe.apply(l)

            # Merge back
            lab_enhanced = cv2.merge([l_enhanced, a, b])
            enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
            return enhanced

        except Exception as e:
            logger.warning(f"Enhancement failed: {e} — using original")
            return frame

    # ── Quality Check ──────────────────────────────────────
    def check_quality(self, frame: np.ndarray) -> dict:
        """
        Check image quality for fundus detection suitability.

        Args:
            frame: BGR numpy array

        Returns:
            Dict with quality metrics:
            {
                "is_valid": True/False,
                "brightness": 0-255,
                "contrast": float,
                "message": str
            }
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Brightness (mean pixel value)
        brightness = float(np.mean(gray))

        # Contrast (standard deviation)
        contrast = float(np.std(gray))

        # Blur detection (Laplacian variance)
        blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        is_valid = True
        message = "Image quality: Good"

        if brightness < 30:
            is_valid = False
            message = "Image too dark — improve lighting"
        elif brightness > 240:
            is_valid = False
            message = "Image too bright — reduce exposure"
        elif contrast < 10:
            is_valid = False
            message = "Low contrast — check image quality"
        elif blur_score < 50:
            message = "Image slightly blurry — results may vary"

        return {
            "is_valid":   is_valid,
            "brightness": brightness,
            "contrast":   contrast,
            "blur_score": blur_score,
            "message":    message
        }

    # ── Crop Center ────────────────────────────────────────
    def crop_center(self, frame: np.ndarray, crop_ratio: float = 0.9) -> np.ndarray:
        """
        Crop center region of fundus image to remove black borders.

        Args:
            frame:      BGR numpy array
            crop_ratio: ratio of center to keep (default 0.9)

        Returns:
            Center-cropped numpy array
        """
        h, w = frame.shape[:2]
        new_h = int(h * crop_ratio)
        new_w = int(w * crop_ratio)
        start_y = (h - new_h) // 2
        start_x = (w - new_w) // 2
        return frame[start_y:start_y + new_h, start_x:start_x + new_w]

    # ── BGR to RGB ─────────────────────────────────────────
    def bgr_to_rgb(self, frame: np.ndarray) -> np.ndarray:
        """Convert OpenCV BGR to RGB."""
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # ── Frame to PIL ───────────────────────────────────────
    def frame_to_pil(self, frame: np.ndarray) -> Image.Image:
        """
        Convert OpenCV BGR frame to PIL Image.

        Args:
            frame: BGR numpy array

        Returns:
            PIL RGB Image
        """
        rgb = self.bgr_to_rgb(frame)
        return Image.fromarray(rgb)

    # ── Denormalize ────────────────────────────────────────
    def denormalize(self, tensor_np: np.ndarray) -> np.ndarray:
        """
        Reverse ImageNet normalization for visualization.

        Args:
            tensor_np: normalized numpy array (C x H x W)

        Returns:
            Denormalized numpy array (H x W x C) in 0-255 range
        """
        mean = np.array(IMAGENET_MEAN)
        std  = np.array(IMAGENET_STD)

        # Transpose from (C, H, W) to (H, W, C)
        img = tensor_np.transpose(1, 2, 0)

        # Denormalize
        img = img * std + mean
        img = np.clip(img * 255, 0, 255).astype(np.uint8)
        return img