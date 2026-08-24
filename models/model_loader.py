# ============================================================
# VisionAI - Eye Disease Detection System
# SMART - Sanjivani Multidisciplinary AI Research & Technology
# models/model_loader.py - Load Trained .pth Models
# ============================================================

import torch
import torch.nn as nn
import timm
import os
from loguru import logger
from models.custom_models import build_fnet, build_perceiver

# ── Disease Classes ────────────────────────────────────────
CLASSES     = ["AMD", "Cataract", "Dementia", "Diabetes", "Glaucoma", "Normal"]
NUM_CLASSES = len(CLASSES)
IMAGE_SIZE  = 640

CUSTOM_ARCHITECTURES = {"fnet", "perceiver"}


class ModelLoader:

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Device: {self.device}")

    def load_model(self, architecture: str, weight_path: str) -> nn.Module:
        if not os.path.exists(weight_path):
            raise FileNotFoundError(f"Weight file not found: {weight_path}")
        logger.info(f"Loading architecture : {architecture}")
        logger.info(f"Weight file          : {weight_path}")
        model = self._build_model(architecture)
        model = self._load_weights(model, weight_path)
        model = model.to(self.device)
        model.eval()
        logger.info(f"Model ready on {self.device}")
        return model

    def _build_model(self, architecture: str) -> nn.Module:
        if architecture == "fnet":
            model = build_fnet(num_classes=NUM_CLASSES)
            logger.info("Built custom FNet architecture")
            return model

        if architecture == "perceiver":
            model = build_perceiver(num_classes=NUM_CLASSES)
            logger.info("Built custom Perceiver architecture")
            return model

        available = timm.list_models()
        if architecture not in available:
            raise ValueError(
                f"Architecture '{architecture}' is not a valid timm model "
                f"and is not a supported custom architecture."
            )

        img_size_supported = {
            "swin_tiny_patch4_window7_224",
            "tf_efficientnetv2_s",
            "resnext50_32x4d",
            "resnet50",
        }

        if architecture in img_size_supported:
            try:
                model = timm.create_model(
                    architecture, pretrained=False,
                    num_classes=NUM_CLASSES, img_size=IMAGE_SIZE,
                )
                logger.info(f"Built {architecture} with img_size={IMAGE_SIZE}")
                return model
            except TypeError:
                logger.warning(f"{architecture} does not accept img_size — building without it.")

        model = timm.create_model(architecture, pretrained=False, num_classes=NUM_CLASSES)
        logger.info(f"Built {architecture} (no img_size)")
        return model

    def _load_weights(self, model: nn.Module, weight_path: str) -> nn.Module:
        try:
            checkpoint = torch.load(weight_path, map_location=self.device, weights_only=True)
        except Exception as e:
            logger.warning(f"weights_only=True failed ({e}). Retrying with weights_only=False.")
            try:
                checkpoint = torch.load(weight_path, map_location=self.device, weights_only=False)
            except Exception as e2:
                logger.error(f"Weight loading error: {e2}")
                raise RuntimeError(f"Failed to load weights: {e2}") from e2

        if isinstance(checkpoint, dict):
            if "model_state_dict" in checkpoint:
                state_dict = checkpoint["model_state_dict"]
            elif "state_dict" in checkpoint:
                state_dict = checkpoint["state_dict"]
            else:
                state_dict = checkpoint
            state_dict          = self._clean_state_dict(state_dict)
            missing, unexpected = model.load_state_dict(state_dict, strict=False)
            if missing:   logger.warning(f"Missing keys   : {len(missing)}")
            if unexpected: logger.warning(f"Unexpected keys: {len(unexpected)}")
        else:
            model = checkpoint

        logger.info(f"Weights loaded: {os.path.basename(weight_path)}")
        return model

    def _clean_state_dict(self, state_dict: dict) -> dict:
        return {k.replace("module.", ""): v for k, v in state_dict.items()}

    def get_device(self):  return self.device
    def get_classes(self): return CLASSES