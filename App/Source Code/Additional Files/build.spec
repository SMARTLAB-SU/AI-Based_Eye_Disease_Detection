# ============================================================
# VisionAI - Eye Disease Detection System
# SMART - Sanjivani Multidisciplinary AI Research & Technology
# build.spec - PyInstaller Single-File Build Configuration (<500MB)
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
    # PyQt6
    "PyQt6",
    "PyQt6.QtWidgets",
    "PyQt6.QtCore",
    "PyQt6.QtGui",

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

    # OpenCV
    "cv2",

    # PIL
    "PIL",
    "PIL.Image",

    # Numpy
    "numpy",

    # Loguru
    "loguru",

    # App modules
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
        "PyQt5",
        "PySide6",
        "PySide2",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtQml",
        "PyQt6.QtQuick",
        "PyQt6.QtPdf",
        "PyQt6.QtMultimedia",
        "PyQt6.QtDesigner",
        "PyQt6.QtVirtualKeyboard",
        "PyQt6.QtSql",
        "PyQt6.QtTest",
        "PyQt6.QtBluetooth",
        "PyQt6.QtNfc",
        "PyQt6.QtPositioning",
        "PyQt6.QtSensors",
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

# ── Filter Out Heavy Development Binaries and Unused Data ──
exclude_words = [
    "cuda", "cudnn", "nvrtc", "cublas", "cudart", "caffe2", "nvjitlink", 
    "cusolver", "cufft", "cusparse", "curand", "nvjpeg", "dnnl", "triton", 
    "llvm", "qt6webengine", "qt6qml", "qt6quick", "qt6pdf", "qt6multimedia",
    "qt6designer", "qt6virtualkeyboard", "qt6sql", "qt6bluetooth",
    "qt6nfc", "qt6positioning", "qt6sensors", "qt6serialport", "qt6remoteobjects",
    "qt6websockets"
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

# ── Executable & Folder Bundle (Instant Startup) ──────────
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VisionAI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT, "assets", "smartlab_logo.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="VisionAI",
)
