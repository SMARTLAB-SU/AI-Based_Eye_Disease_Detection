# ============================================================
# VisionAI - Eye Disease Detection System
# SMART - Sanjivani Multidisciplinary AI Research & Technology
# main.py - Application Entry Point
# ============================================================

import os
import sys

# ── Force PyQt XCB Platform on Linux & 1:1 Scale Metrics ───────
# Programmatically set environment overrides before QApplication instantiation
if sys.platform.startswith("linux"):
    os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"
os.environ["QT_FONT_DPI"] = "96"

# ── CPU Thread Limits & Environment Configuration ──────────
# Limiting thread count prevents thermal throttling and hard power cuts on Pi 5 / SBCs
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
os.environ["OPENBLAS_NUM_THREADS"] = "2"
os.environ["VECLIB_MAXIMUM_THREADS"] = "2"
os.environ["NUMEXPR_NUM_THREADS"] = "2"

# Prevent OpenMP duplicate-library errors & ignore global user site-packages
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["PYTHONNOUSERSITE"] = "1"

from loguru import logger

# Dual PyQt5 / PyQt6 import abstraction
try:
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont
    from PyQt5.QtWidgets import QApplication
except ImportError:
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QFont
    from PyQt6.QtWidgets import QApplication

# ── Display Scaling Setup (1:1 Metrics Enforced) ─────────────
if hasattr(Qt, "AA_EnableHighDpiScaling"):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, False)
if hasattr(Qt, "AA_UseHighDpiPixmaps"):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, False)

from ui.main_window import MainWindow

# Configuration
KIOSK_MODE = os.environ.get("VISIONAI_KIOSK", "0").lower() in ("1", "true", "yes")

# Logging Setup
log_directory = os.path.join(
    os.path.expanduser("~"),
    "VisionAI",
    "logs",
)

os.makedirs(log_directory, exist_ok=True)

logger.add(
    os.path.join(log_directory, "visionai_{time}.log"),
    rotation="10 MB",
    retention="7 days",
    level="INFO",
    encoding="utf-8",
    enqueue=True,
)

# PyTorch Thread Optimization
try:
    import torch

    torch.set_num_threads(2)

    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        pass

    logger.info("PyTorch CPU threads limited to 2 for system thermal stability")

except ImportError:
    logger.warning("PyTorch could not be imported")


def log_display_information(app: QApplication) -> None:
    """Write connected display information to the log."""
    screens = app.screens()

    if not screens:
        logger.warning("No display was detected")
        return

    for index, screen in enumerate(screens, start=1):
        geometry = screen.geometry()
        available = screen.availableGeometry()

        logger.info(
            "Display {}: name={} resolution={}x{} "
            "available={}x{} DPR={:.2f} logicalDPI={:.2f}",
            index,
            screen.name(),
            geometry.width(),
            geometry.height(),
            available.width(),
            available.height(),
            screen.devicePixelRatio(),
            screen.logicalDotsPerInch(),
        )


def apply_display_mode(
    window: MainWindow,
    app: QApplication,
) -> None:
    """Make the application fit the display."""
    screen = window.screen() or app.primaryScreen()

    if screen is None:
        logger.warning("Unable to determine the current display")
        window.show()
        return

    geometry = screen.geometry()

    logger.info(
        "Applying display mode: {}x{}",
        geometry.width(),
        geometry.height(),
    )

    if KIOSK_MODE:
        window.showFullScreen()
    else:
        window.showMaximized()


def connect_display_change_handlers(
    window: MainWindow,
    app: QApplication,
) -> None:
    """Reapply the display mode when display geometry changes."""
    connected_screens = set()

    def connect_screen(screen) -> None:
        if screen is None:
            return

        screen_name = screen.name()

        if screen_name in connected_screens:
            return

        connected_screens.add(screen_name)

        screen.geometryChanged.connect(
            lambda _geometry: QTimer.singleShot(
                100,
                lambda: apply_display_mode(window, app),
            )
        )

        screen.availableGeometryChanged.connect(
            lambda _geometry: QTimer.singleShot(
                100,
                lambda: apply_display_mode(window, app),
            )
        )

        screen.logicalDotsPerInchChanged.connect(
            lambda _dpi: QTimer.singleShot(
                100,
                lambda: apply_display_mode(window, app),
            )
        )

        logger.info(
            "Display-change handling enabled for {}",
            screen_name,
        )

    for current_screen in app.screens():
        connect_screen(current_screen)

    app.screenAdded.connect(connect_screen)

    def handle_screen_removed(_screen) -> None:
        QTimer.singleShot(
            200,
            lambda: apply_display_mode(window, app),
        )

    app.screenRemoved.connect(handle_screen_removed)

    window_handle = window.windowHandle()

    if window_handle is not None:
        window_handle.screenChanged.connect(
            lambda new_screen: (
                connect_screen(new_screen),
                QTimer.singleShot(
                    100,
                    lambda: apply_display_mode(window, app),
                ),
            )
        )


def ensure_pi_autostart() -> None:
    """Ensure system autostart desktop file exists on Raspberry Pi / Linux."""
    try:
        if not sys.platform.startswith("linux"):
            return

        autostart_dir = "/home/smartlab/.config/autostart"
        desktop_file = os.path.join(autostart_dir, "visionai.desktop")
        target_script = "/home/smartlab/VisionAI/run_pi.sh"

        if os.path.exists("/home/smartlab") or os.path.exists("/proc/device-tree/model"):
            os.makedirs(autostart_dir, exist_ok=True)
            content = (
                "[Desktop Entry]\n"
                "Type=Application\n"
                "Name=VisionAI\n"
                "Comment=Eye Disease Detection System Autostart\n"
                f"Exec={target_script}\n"
                "Icon=/home/smartlab/VisionAI/assets/smartlab_logo.png\n"
                "Path=/home/smartlab/VisionAI\n"
                "Terminal=false\n"
                "X-GNOME-Autostart-enabled=true\n"
            )
            if not os.path.exists(desktop_file):
                with open(desktop_file, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info(f"Autostart configuration verified/created at {desktop_file}")
    except Exception as exc:
        logger.warning(f"Could not configure system autostart: {exc}")


def main() -> None:
    """Launch the VisionAI application."""
    logger.info("Starting VisionAI - Eye Disease Detection System")
    logger.info("SMART - Sanjivani Multidisciplinary AI Research & Technology")

    app = QApplication(sys.argv)

    app.setApplicationName("VisionAI")
    app.setApplicationDisplayName("VisionAI - Eye Disease Detection System")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SMART - Sanjivani Multidisciplinary AI Research & Technology")

    font_family = "DejaVu Sans" if sys.platform.startswith("linux") else "Segoe UI"
    application_font = QFont(font_family)
    application_font.setPixelSize(16)
    app.setFont(application_font)

    log_display_information(app)

    ensure_pi_autostart()

    try:
        window = MainWindow()
        window.setMinimumSize(320, 240)

        apply_display_mode(window, app)

        QTimer.singleShot(
            0,
            lambda: connect_display_change_handlers(window, app),
        )

        logger.info("VisionAI launched successfully")

        exit_code = app.exec() if hasattr(app, "exec") else app.exec_()

        logger.info(
            "VisionAI closed with exit code {}",
            exit_code,
        )

        sys.exit(exit_code)

    except Exception:
        logger.exception("VisionAI failed to start because of an unexpected error")
        raise


if __name__ == "__main__":
    main()