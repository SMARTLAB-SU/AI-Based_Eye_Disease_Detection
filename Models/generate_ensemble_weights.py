# ============================================================
# VisionAI - Ensemble Model Weights Generator
# Creates .pth ensemble checkpoints matching the .ipynb notebooks
# ============================================================

import os
import torch

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))
CLASSES = ["AMD", "Cataract", "Dementia", "Diabetes", "Glaucoma", "Normal"]

ENSEMBLE_CONFIGS = [
    {
        "output_file": "swin_fnet_ensemble.pth",
        "model_a_file": "swin_scratch_best.pth",
        "model_b_file": "fnet_scratch_best.pth",
        "key_a": "swin_state_dict",
        "key_b": "fnet_state_dict",
        "weight_key": "w_swin",
        "weight_val": 0.75,
        "name": "Swin Transformer + FNet Ensemble",
    },
    {
        "output_file": "effnet_fnet_ensemble.pth",
        "model_a_file": "efficientnetv2s_scratch_best.pth",
        "model_b_file": "fnet_scratch_best.pth",
        "key_a": "effnet_state_dict",
        "key_b": "fnet_state_dict",
        "weight_key": "w_eff",
        "weight_val": 0.80,
        "name": "EfficientNetV2-S + FNet Ensemble",
    },
    {
        "output_file": "effnet_perceiver_ensemble.pth",
        "model_a_file": "efficientnetv2s_scratch_best.pth",
        "model_b_file": "perceiver_scratch_best.pth",
        "key_a": "effnet_state_dict",
        "key_b": "perceiver_state_dict",
        "weight_key": "w_eff",
        "weight_val": 0.95,
        "name": "EfficientNetV2-S + Perceiver IO Ensemble",
    },
    {
        "output_file": "effnet_swin_ensemble.pth",
        "model_a_file": "efficientnetv2s_scratch_best.pth",
        "model_b_file": "swin_scratch_best.pth",
        "key_a": "effnet_state_dict",
        "key_b": "swin_state_dict",
        "weight_key": "w_eff",
        "weight_val": 0.10,
        "name": "EfficientNetV2-S + Swin Transformer Ensemble",
    },
    {
        "output_file": "resnext_perceiver_ensemble.pth",
        "model_a_file": "resnext50_scratch_best.pth",
        "model_b_file": "perceiver_scratch_best.pth",
        "key_a": "resnext_state_dict",
        "key_b": "perceiver_state_dict",
        "weight_key": "w_resnext",
        "weight_val": 0.25,
        "name": "ResNeXt50 + Perceiver IO Ensemble",
    },
]


def extract_state_dict(checkpoint_or_model):
    if isinstance(checkpoint_or_model, dict):
        if "model_state_dict" in checkpoint_or_model:
            return checkpoint_or_model["model_state_dict"]
        elif "state_dict" in checkpoint_or_model:
            return checkpoint_or_model["state_dict"]
        return checkpoint_or_model
    elif hasattr(checkpoint_or_model, "state_dict"):
        return checkpoint_or_model.state_dict()
    return checkpoint_or_model


def generate_ensembles():
    print(f"Generating ensemble model weights in: {MODELS_DIR}")
    for cfg in ENSEMBLE_CONFIGS:
        out_path = os.path.join(MODELS_DIR, cfg["output_file"])
        path_a = os.path.join(MODELS_DIR, cfg["model_a_file"])
        path_b = os.path.join(MODELS_DIR, cfg["model_b_file"])

        if not os.path.exists(path_a) or not os.path.exists(path_b):
            print(f"[-] Missing input weights for {cfg['name']}")
            continue

        print(f"[+] Creating {cfg['name']} -> {cfg['output_file']}")
        ckpt_a = torch.load(path_a, map_location="cpu", weights_only=False)
        ckpt_b = torch.load(path_b, map_location="cpu", weights_only=False)

        state_dict_a = extract_state_dict(ckpt_a)
        state_dict_b = extract_state_dict(ckpt_b)

        ensemble_checkpoint = {
            cfg["key_a"]: state_dict_a,
            cfg["key_b"]: state_dict_b,
            cfg["weight_key"]: cfg["weight_val"],
            "classes": CLASSES,
            "name": cfg["name"],
        }

        torch.save(ensemble_checkpoint, out_path)
        size_mb = os.path.getsize(out_path) / (1024 * 1024)
        print(f"    Saved {cfg['output_file']} ({size_mb:.2f} MB)")

    print("\nAll ensemble weights generated successfully!")


if __name__ == "__main__":
    generate_ensembles()
