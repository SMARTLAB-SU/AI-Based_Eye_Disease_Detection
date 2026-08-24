# ============================================================
# VisionAI - Eye Disease Detection System
# ui/styles.py - Application Styles and Theme
# Light Medical Theme - White + Soft Blue
# ============================================================

# ── Main Application Style ─────────────────────────────────
MAIN_STYLE = """
QMainWindow {
    background-color: #F0F4F8;
}

QWidget {
    background-color: #F0F4F8;
    color: #1A2B4A;
    font-family: 'Segoe UI';
    font-size: 10pt;
}

/* ── Scroll Bars ── */
QScrollBar:vertical {
    border: none;
    background: #E8EDF2;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #2A7BDE;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

QScrollBar:horizontal {
    border: none;
    background: #E8EDF2;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #2A7BDE;
    border-radius: 4px;
    min-width: 20px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
}

/* ── Tool Tips ── */
QToolTip {
    background-color: #1A2B4A;
    color: white;
    border: none;
    padding: 5px;
    border-radius: 4px;
    font-size: 9pt;
}
"""

# ── Title Bar Style ────────────────────────────────────────
TITLE_STYLE = """
QLabel {
    background-color: #1A2B4A;
    color: white;
    font-size: 22pt;
    font-weight: bold;
    font-family: 'Segoe UI';
    padding: 10px;
    letter-spacing: 2px;
}
"""

SUBTITLE_STYLE = """
QLabel {
    background-color: #1A2B4A;
    color: #7EB3F5;
    font-size: 9pt;
    font-family: 'Segoe UI';
    padding-bottom: 8px;
    letter-spacing: 1px;
}
"""

# ── Header Panel Style ─────────────────────────────────────
HEADER_STYLE = """
QWidget {
    background-color: #1A2B4A;
}
"""

# ── Dropdown Style ─────────────────────────────────────────
DROPDOWN_STYLE = """
QComboBox {
    background-color: white;
    color: #1A2B4A;
    border: 2px solid #2A7BDE;
    border-radius: 8px;
    padding: 4px 28px 4px 10px;
    font-size: 10pt;
    font-weight: bold;
}
QComboBox:hover {
    border: 2px solid #1A5CB5;
    background-color: #EEF4FF;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
    border-left-width: 0px;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #2A7BDE;
    margin-right: 6px;
}
QComboBox QAbstractItemView {
    background-color: white;
    color: #1A2B4A;
    border: 2px solid #2A7BDE;
    border-radius: 8px;
    selection-background-color: #2A7BDE;
    selection-color: white;
    padding: 4px;
    font-size: 10pt;
    outline: none;
}
QComboBox QAbstractItemView::item {
    min-height: 28px;
    padding: 4px 8px;
}
"""

# ── Display Panel Style ────────────────────────────────────
DISPLAY_PANEL_STYLE = """
QLabel {
    background-color: #1A2B4A;
    color: #7EB3F5;
    border-radius: 12px;
    font-size: 11pt;
    font-weight: bold;
}
"""

PANEL_TITLE_STYLE = """
QLabel {
    background-color: #2A7BDE;
    color: white;
    font-size: 10pt;
    font-weight: bold;
    padding: 6px 10px;
    border-radius: 6px;
}
"""

# ── Button Styles ──────────────────────────────────────────
CAMERA_BUTTON_STYLE = """
QPushButton {
    background-color: #2A7BDE;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 20px;
    font-size: 11pt;
    font-weight: bold;
    min-width: 150px;
    min-height: 45px;
}
QPushButton:hover {
    background-color: #1A5CB5;
}
QPushButton:pressed {
    background-color: #0D3D7A;
}
QPushButton:disabled {
    background-color: #A0B4C8;
    color: #E0E8F0;
}
"""

UPLOAD_BUTTON_STYLE = """
QPushButton {
    background-color: white;
    color: #2A7BDE;
    border: 2px solid #2A7BDE;
    border-radius: 10px;
    padding: 12px 20px;
    font-size: 11pt;
    font-weight: bold;
    min-width: 150px;
    min-height: 45px;
}
QPushButton:hover {
    background-color: #EEF4FF;
    border-color: #1A5CB5;
}
QPushButton:pressed {
    background-color: #D0E4FF;
}
QPushButton:disabled {
    background-color: #F0F4F8;
    color: #A0B4C8;
    border-color: #A0B4C8;
}
"""

STOP_BUTTON_STYLE = """
QPushButton {
    background-color: #E53E3E;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 20px;
    font-size: 11pt;
    font-weight: bold;
    min-width: 150px;
    min-height: 45px;
}
QPushButton:hover {
    background-color: #C53030;
}
QPushButton:pressed {
    background-color: #9B2C2C;
}
"""

SAVE_BUTTON_STYLE = """
QPushButton {
    background-color: #38A169;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 20px;
    font-size: 11pt;
    font-weight: bold;
    min-width: 150px;
    min-height: 45px;
}
QPushButton:hover {
    background-color: #2F855A;
}
QPushButton:pressed {
    background-color: #276749;
}
QPushButton:disabled {
    background-color: #A0B4C8;
    color: #E0E8F0;
}
"""

# ── Patient ID Input Style ─────────────────────────────────
PATIENT_INPUT_STYLE = """
QLineEdit {
    background-color: white;
    color: #1A2B4A;
    border: 2px solid #CBD5E0;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 10pt;
    min-height: 35px;
}
QLineEdit:focus {
    border: 2px solid #2A7BDE;
}
QLineEdit:hover {
    border: 2px solid #90B8E8;
}
"""

PATIENT_LABEL_STYLE = """
QLabel {
    color: #1A2B4A;
    font-size: 10pt;
    font-weight: bold;
    background-color: transparent;
}
"""

# ── Progress Bar Style ─────────────────────────────────────
PROGRESS_BAR_STYLE = """
QProgressBar {
    background-color: #E2E8F0;
    border-radius: 6px;
    height: 12px;
    text-align: center;
    font-size: 8pt;
    color: #1A2B4A;
    border: none;
}
QProgressBar::chunk {
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #2A7BDE,
        stop:1 #63B3ED
    );
    border-radius: 6px;
}
"""

# ── Status Bar Style ───────────────────────────────────────
STATUS_BAR_STYLE = """
QStatusBar {
    background-color: #1A2B4A;
    color: #7EB3F5;
    font-size: 9pt;
    padding: 4px;
}
QStatusBar::item {
    border: none;
}
"""

# ── Snapshot Panel Style ───────────────────────────────────
SNAPSHOT_PANEL_STYLE = """
QWidget {
    background-color: white;
    border-radius: 10px;
    border: 1px solid #E2E8F0;
}
"""

SNAPSHOT_LABEL_STYLE = """
QLabel {
    background-color: #1A2B4A;
    color: white;
    border-radius: 6px;
    font-size: 8pt;
    padding: 3px;
}
"""

# ── Disease Info Panel Style ───────────────────────────────
DISEASE_INFO_STYLE = """
QTextEdit {
    background-color: white;
    color: #1A2B4A;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 10px;
    font-size: 10pt;
    line-height: 1.5;
}
"""

# ── Card Panel Style ───────────────────────────────────────
CARD_STYLE = """
QWidget {
    background-color: white;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
}
"""

# ── Section Label Style ────────────────────────────────────
SECTION_LABEL_STYLE = """
QLabel {
    color: #2A7BDE;
    font-size: 9pt;
    font-weight: bold;
    background-color: transparent;
    letter-spacing: 1px;
}
"""

# ── Result Label Style ─────────────────────────────────────
RESULT_NORMAL_STYLE = """
QLabel {
    color: #38A169;
    font-size: 13pt;
    font-weight: bold;
    background-color: transparent;
}
"""

RESULT_DISEASE_STYLE = """
QLabel {
    color: #E53E3E;
    font-size: 13pt;
    font-weight: bold;
    background-color: transparent;
}
"""

CONFIDENCE_LABEL_STYLE = """
QLabel {
    color: #718096;
    font-size: 10pt;
    background-color: transparent;
}
"""

# ── Bottom Bar Style ───────────────────────────────────────
BOTTOM_BAR_STYLE = """
QWidget {
    background-color: white;
    border-top: 2px solid #E2E8F0;
}
"""

LOGO_LABEL_STYLE = """
QLabel {
    background-color: #1A2B4A;
    border-radius: 10px;
    padding: 5px;
}
"""

# ── Disease Colors ─────────────────────────────────────────
DISEASE_COLORS = {
    "AMD":      "#E53E3E",   # Red
    "Cataract": "#DD6B20",   # Orange
    "Dementia": "#805AD5",   # Purple
    "Diabetes": "#D69E2E",   # Yellow
    "Glaucoma": "#3182CE",   # Blue
    "Normal":   "#38A169",   # Green
}

# ── Disease Information ────────────────────────────────────
DISEASE_INFO = {
    "AMD": {
        "full_name": "Age-related Macular Degeneration",
        "description": (
            "Age-related Macular Degeneration (AMD) is a progressive eye disease "
            "that affects the macula — the central part of the retina responsible "
            "for sharp, central vision. It is the leading cause of vision loss in "
            "people over 50. AMD causes blurring of central vision, making it "
            "difficult to read, drive, or recognize faces. There are two types: "
            "Dry AMD (most common) and Wet AMD (more severe). Early detection and "
            "treatment can slow progression."
        ),
        "symptoms": "Blurred central vision, dark spots, distorted lines",
        "treatment": "Anti-VEGF injections, laser therapy, vitamins",
        "severity": "High",
    },
    "Cataract": {
        "full_name": "Cataract",
        "description": (
            "A cataract is a clouding of the eye's natural lens, which lies behind "
            "the iris and pupil. Cataracts are the leading cause of blindness worldwide. "
            "They develop slowly and can affect one or both eyes. Symptoms include "
            "cloudy or blurry vision, faded colors, glare, poor night vision, and "
            "double vision. Cataracts are most commonly caused by aging but can also "
            "result from injury, medications, or medical conditions. Surgery is the "
            "only effective treatment."
        ),
        "symptoms": "Cloudy vision, glare, faded colors, poor night vision",
        "treatment": "Cataract surgery with intraocular lens implant",
        "severity": "Moderate",
    },
    "Dementia": {
        "full_name": "Dementia-related Retinal Changes",
        "description": (
            "Dementia causes significant changes in the retina that can be detected "
            "through fundus imaging. The retina is considered a window to the brain, "
            "and retinal thinning, reduced blood vessel density, and other changes "
            "have been linked to cognitive decline and dementia. Early retinal changes "
            "may appear years before clinical dementia symptoms. Detection of these "
            "changes allows for early intervention and monitoring of neurological health."
        ),
        "symptoms": "Retinal thinning, reduced vessel density, optic nerve changes",
        "treatment": "Neurological evaluation, cognitive therapy, monitoring",
        "severity": "High",
    },
    "Diabetes": {
        "full_name": "Diabetic Retinopathy",
        "description": (
            "Diabetic Retinopathy is a diabetes complication that affects the blood "
            "vessels in the retina. It is the leading cause of blindness in working-age "
            "adults. High blood sugar levels damage the tiny blood vessels in the retina, "
            "causing them to leak, swell, or grow abnormally. Early stages may have no "
            "symptoms, making regular fundus screening critical for diabetic patients. "
            "If untreated, it can lead to severe vision loss or complete blindness."
        ),
        "symptoms": "Floaters, blurred vision, dark areas, vision loss",
        "treatment": "Blood sugar control, laser treatment, anti-VEGF injections",
        "severity": "High",
    },
    "Glaucoma": {
        "full_name": "Glaucoma",
        "description": (
            "Glaucoma is a group of eye conditions that damage the optic nerve, "
            "essential for good vision. This damage is often caused by abnormally "
            "high intraocular pressure. Glaucoma is one of the leading causes of "
            "blindness for people over 60. It can occur at any age but is more "
            "common in older adults. The most common type develops gradually with "
            "no symptoms until significant vision loss has occurred. Early detection "
            "through fundus screening is crucial."
        ),
        "symptoms": "Peripheral vision loss, tunnel vision, eye pain, headache",
        "treatment": "Eye drops, laser therapy, surgery",
        "severity": "High",
    },
    "Normal": {
        "full_name": "Normal - Healthy Eye",
        "description": (
            "The fundus examination shows a healthy eye with no signs of disease. "
            "The retina appears normal with healthy blood vessels, a well-defined "
            "optic disc, and a clear macula. Regular eye examinations are still "
            "recommended to monitor eye health over time. Maintaining a healthy "
            "lifestyle, controlling blood pressure and blood sugar, and protecting "
            "eyes from UV light can help preserve good eye health."
        ),
        "symptoms": "No symptoms — healthy eye detected",
        "treatment": "Regular monitoring, healthy lifestyle",
        "severity": "None",
    },
}

# ── Model Information ──────────────────────────────────────
MODEL_INFO = {
    "Swin Transformer": {
        "file": "swin_scratch_best.pth",
        "accuracy": "99.33%",
        "architecture": "swin_tiny_patch4_window7_224",
        "parameters": "28M",
        "description": "Best performing model — Hierarchical Vision Transformer",
    },
    "EfficientNetV2-S": {
        "file": "efficientnetv2s_scratch_best.pth",
        "accuracy": "98.50%",
        "architecture": "tf_efficientnetv2_s",
        "parameters": "21M",
        "description": "Fast and efficient CNN-based model",
    },
    "ResNeXt50": {
        "file": "resnext50_scratch_best.pth",
        "accuracy": "97.80%",
        "architecture": "resnext50_32x4d",
        "parameters": "25M",
        "description": "Aggregated residual transformations network",
    },
    "FNet": {
        "file": "fnet_scratch_best.pth",
        "accuracy": "96.50%",
        "architecture": "fnet",
        "parameters": "12M",
        "description": "Fourier transform based mixing model",
    },
    "Perceiver": {
        "file": "perceiver_scratch_best.pth",
        "accuracy": "95.90%",
        "architecture": "perceiver",
        "parameters": "15M",
        "description": "General purpose attention-based architecture",
    },
}