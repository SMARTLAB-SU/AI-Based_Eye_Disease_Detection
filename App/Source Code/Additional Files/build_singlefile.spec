# ============================================================
# VisionAI - Eye Disease Detection System
# SMART - Sanjivani Multidisciplinary AI Research & Technology
# build_singlefile.spec - Single Standalone Executable (.exe)
# ============================================================

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# ── Project Root (App/Source Code) ────────────────────────
SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
ROOT = os.path.abspath(os.path.join(SPEC_DIR, "..")) if os.path.basename(SPEC_DIR) == "Additional Files" else SPEC_DIR

# ── Collect timm and torch data ────────────────────────────
timm_datas   = collect_data_files("timm")
torch_datas  = collect_data_files("torch")

# ── Hidden Imports ─────────────────────────────────────────
hidden_imports = [
    # PyQt6 / PyQt5
    "PyQt6",
    "PyQt6.QtWidgets",
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt5",
    "PyQt5.QtWidgets",
    "PyQt5.QtCore",
    "PyQt5.QtGui",

    # PyTorch
    "torch",
    "torch.nn",
    "torch.nn.functional",
    "torchvision",
    "torchvision.transforms",
    "sympy",
    "mpmath",

    # timm
    "timm",
    "timm.models",
    "timm.models.swin_transformer",
    "timm.models.efficientnet",
    "timm.models.resnet",
    "timm.models.resnext",
    "timm.data",

    # OpenCV & PIL
    "cv2",
    "PIL",
    "PIL.Image",

    # Utilities
    "numpy",
    "loguru",
    "ui",
    "ui.main_window",
    "ui.styles",
    "models",
    "models.model_loader",
    "models.predictor",
    "utils",
    "utils.preprocessing",
    "utils.save_manager",
    "utils.report_generator",
    "utils.camera_capture",
    "unittest",
]

hidden_imports += collect_submodules("timm")
hidden_imports += collect_submodules("torch")

# ── Data Files ─────────────────────────────────────────────
datas = [
    (os.path.join(ROOT, "assets"), "assets"),
]
datas += timm_datas
datas += torch_datas

# ── Analysis ───────────────────────────────────────────────
a = Analysis(
    [os.path.join(ROOT, "main.py")],
    pathex=[ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib",
        "scipy",
        "pandas",
        "sklearn",
        "notebook",
        "IPython",
        "tkinter",
        "torchaudio",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtQml",
        "PyQt6.QtQuick",
        "PyQt6.QtPdf",
        "PyQt6.QtMultimedia",
        "PyQt6.QtDesigner",
        "pydoc",
        "doctest",
        "test",
        "setuptools",
        "pip",
        "wheel",
        "distutils",
        "pygments",
        "curses",
        "xmlrpc",
        "triton",
    ],
    noarchive=False,
)

# ── Filter Out Unnecessary Development Binaries ───────────
exclude_words = [
    "cuda", "cudnn", "nvrtc", "cublas", "cudart", "caffe2", "nvjitlink", 
    "cusolver", "cufft", "cusparse", "curand", "nvjpeg", "dnnl", "triton", 
    "llvm", "qt6webengine", "qt6qml", "qt6quick", "qt6pdf", "qt6multimedia"
]

skip_exts = (".lib", ".a", ".h", ".hpp", ".cu", ".cuh", ".cmake", ".pyi")

a.binaries = [x for x in a.binaries if not (
    any(w in x[0].lower() or w in x[1].lower() for w in exclude_words)
    or any(x[0].lower().endswith(ext) or x[1].lower().endswith(ext) for ext in skip_exts)
)]

a.datas = [x for x in a.datas if not (
    any(w in x[0].lower() or w in x[1].lower() for w in exclude_words)
    or any(x[0].lower().endswith(ext) or x[1].lower().endswith(ext) for ext in skip_exts)
)]

# ── PYZ Archive ────────────────────────────────────────────
pyz = PYZ(a.pure)

# ── Single-File Standalone Executable (.exe) ───────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="VisionAI_Standalone",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT, "assets", "smartlab_logo.ico"),
)
