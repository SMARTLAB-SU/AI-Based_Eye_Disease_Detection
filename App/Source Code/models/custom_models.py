# ============================================================
# VisionAI - Eye Disease Detection System
# SMART - Sanjivani Multidisciplinary AI Research & Technology
# models/custom_models.py - Custom FNet and Perceiver Models
# ============================================================
# These are custom architectures built from scratch during
# training. They are NOT timm models. Architecture is reverse-
# engineered from the saved weight shapes.
#
# FNet:
#   - Patch embedding (3072 -> 256)
#   - Positional embedding (1, 400, 256)
#   - 6 FNet blocks (Fourier mixing + FF)
#   - Final LayerNorm + head (256 -> 6)
#
# Perceiver:
#   - Patch embedding conv (3x32x32 -> 256)
#   - 128 latent vectors (128, 256)
#   - 6 cross-attention layers
#   - 6 FF layers
#   - Final LayerNorm + head (256 -> 6)
# ============================================================

import torch
import torch.nn as nn
import torch.nn.functional as F


# ── FNet Block ─────────────────────────────────────────────
class FNetBlock(nn.Module):
    """
    FNet block: Fourier mixing replaces self-attention.
    Structure from weights:
        ln1, ln2: LayerNorm(256)
        ff: Linear(256->1024) -> GELU -> Linear(1024->256)
    """
    def __init__(self, dim: int = 256, ff_dim: int = 1024):
        super().__init__()
        self.ln1 = nn.LayerNorm(dim)
        self.ln2 = nn.LayerNorm(dim)
        self.ff  = nn.Sequential(
            nn.Linear(dim, ff_dim),
            nn.GELU(),
            nn.Linear(ff_dim, dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Fourier mixing (no learnable params)
        x = x + torch.fft.fft(torch.fft.fft(
            self.ln1(x), dim=-1
        ), dim=-2).real
        # Feed-forward
        x = x + self.ff(self.ln2(x))
        return x


# ── FNet Model ─────────────────────────────────────────────
class FNet(nn.Module):
    """
    FNet for image classification.
    Matches weight shapes exactly:
        pos_embed:        (1, 400, 256)
        embedding.weight: (256, 3072)   — Linear(3072, 256)
        embedding.bias:   (256,)
        blocks.0-5:       6 x FNetBlock
        ln:               LayerNorm(256)
        head:             Linear(256, 6)

    Input: (B, 3, H, W) — resized to 640x640 upstream
    Patch size: 32x32 → 20x20 = 400 patches
    Patch dim:  3 * 32 * 32 = 3072
    """
    def __init__(
        self,
        img_size:   int = 640,
        patch_size: int = 32,
        in_chans:   int = 3,
        embed_dim:  int = 256,
        ff_dim:     int = 1024,
        num_blocks: int = 6,
        num_classes:int = 6,
    ):
        super().__init__()
        self.patch_size  = patch_size
        self.num_patches = (img_size // patch_size) ** 2   # 400
        patch_dim        = in_chans * patch_size * patch_size  # 3072

        self.embedding = nn.Linear(patch_dim, embed_dim)
        self.pos_embed = nn.Parameter(
            torch.zeros(1, self.num_patches, embed_dim)
        )
        self.blocks = nn.Sequential(
            *[FNetBlock(embed_dim, ff_dim) for _ in range(num_blocks)]
        )
        self.ln   = nn.LayerNorm(embed_dim)
        self.head = nn.Linear(embed_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, C, H, W = x.shape
        p = self.patch_size

        # Extract patches: (B, num_patches, patch_dim)
        x = x.unfold(2, p, p).unfold(3, p, p)
        x = x.contiguous().view(B, C, -1, p, p)
        x = x.permute(0, 2, 1, 3, 4).contiguous()
        x = x.view(B, -1, C * p * p)

        # Embed + positional encoding
        x = self.embedding(x) + self.pos_embed

        # FNet blocks
        x = self.blocks(x)

        # Global average pool + classify
        x = self.ln(x.mean(dim=1))
        return self.head(x)


# ── Perceiver Model ────────────────────────────────────────
class Perceiver(nn.Module):
    """
    Perceiver for image classification.
    Matches weight shapes exactly:
        latents:              (128, 256)
        patch_embed.weight:   (256, 3, 32, 32) — Conv2d
        patch_embed.bias:     (256,)
        cross_attn.0-5:       6 x MultiheadAttention(256, 8)
        ln:                   LayerNorm(256)
        ff.0-5:               6 x Sequential(Linear, GELU, Linear)
        head:                 Linear(256, 6)

    Input: (B, 3, H, W)
    """
    def __init__(
        self,
        num_latents: int = 128,
        latent_dim:  int = 256,
        num_heads:   int = 8,
        ff_dim:      int = 1024,
        num_blocks:  int = 6,
        num_classes: int = 6,
        patch_size:  int = 32,
    ):
        super().__init__()
        self.latents    = nn.Parameter(torch.randn(num_latents, latent_dim))
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

        # Patch embed: (B, dim, H', W') -> (B, N, dim)
        x = self.patch_embed(x)
        x = x.flatten(2).transpose(1, 2)

        # Expand latents for batch
        latents = self.latents.unsqueeze(0).expand(B, -1, -1)

        # Cross-attention + FF blocks
        for attn, ff in zip(self.cross_attn, self.ff):
            latents, _ = attn(latents, x, x)
            latents    = latents + ff(latents)

        # Global average pool + classify
        out = self.ln(latents.mean(dim=1))
        return self.head(out)


# ── Factory Functions ──────────────────────────────────────
def build_fnet(num_classes: int = 6) -> FNet:
    """Build FNet matching trained weight shapes."""
    return FNet(
        img_size    = 640,
        patch_size  = 32,
        in_chans    = 3,
        embed_dim   = 256,
        ff_dim      = 1024,
        num_blocks  = 6,
        num_classes = num_classes,
    )


def build_perceiver(num_classes: int = 6) -> Perceiver:
    """Build Perceiver matching trained weight shapes."""
    return Perceiver(
        num_latents = 128,
        latent_dim  = 256,
        num_heads   = 8,
        ff_dim      = 1024,
        num_blocks  = 6,
        num_classes = num_classes,
        patch_size  = 32,
    )