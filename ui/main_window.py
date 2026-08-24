# ============================================================
# VisionAI - Eye Disease Detection System
# SMART - Sanjivani Multidisciplinary AI Research & Technology
# ui/main_window.py - Complete Main Window UI & Worker Threads
# ============================================================

import os
import sys
import cv2
import queue
import numpy as np
from datetime import datetime
from loguru import logger

# ── Dual PyQt5 / PyQt6 Import Compatibility Layer ──────────
try:
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QTimer
    from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QPushButton, QComboBox, QLineEdit, QTabWidget,
        QProgressBar, QFileDialog, QMessageBox, QInputDialog,
        QFrame, QSizePolicy, QScrollArea, QApplication
    )
    ALIGN_CENTER = Qt.AlignCenter
    KEEP_ASPECT = Qt.KeepAspectRatio
    SMOOTH_TRANSFORM = Qt.SmoothTransformation
    RGB888 = QImage.Format_RGB888
    NO_FRAME = QFrame.NoFrame
    VLINE = QFrame.VLine
    ALWAYS_OFF = Qt.ScrollBarAlwaysOff
    AS_NEEDED = Qt.ScrollBarAsNeeded
    QUEUED_CONNECTION = Qt.QueuedConnection
except ImportError:
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QTimer
    from PyQt6.QtGui import QPixmap, QImage, QFont, QIcon
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QPushButton, QComboBox, QLineEdit, QTabWidget,
        QProgressBar, QFileDialog, QMessageBox, QInputDialog,
        QFrame, QSizePolicy, QScrollArea, QApplication
    )
    ALIGN_CENTER = Qt.AlignmentFlag.AlignCenter
    KEEP_ASPECT = Qt.AspectRatioMode.KeepAspectRatio
    SMOOTH_TRANSFORM = Qt.TransformationMode.SmoothTransformation
    RGB888 = QImage.Format.Format_RGB888
    NO_FRAME = QFrame.Shape.NoFrame
    VLINE = QFrame.Shape.VLine
    ALWAYS_OFF = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    AS_NEEDED = Qt.ScrollBarPolicy.ScrollBarAsNeeded
    QUEUED_CONNECTION = Qt.ConnectionType.QueuedConnection

from ui.styles import (
    DROPDOWN_STYLE, PROGRESS_BAR_STYLE, STATUS_BAR_STYLE,
    DISEASE_COLORS, DISEASE_INFO, MODEL_INFO,
)
from models.model_loader import ModelLoader
from models.predictor import Predictor
from utils.save_manager import SaveManager
from utils.report_generator import ReportGenerator
from utils.camera_capture import CameraCapture


def is_raspberry_pi() -> bool:
    """Check if running on a Raspberry Pi device."""
    try:
        if os.path.exists("/proc/device-tree/model"):
            with open("/proc/device-tree/model", "r") as f:
                return "raspberry pi" in f.read().lower()
    except Exception:
        pass
    return False


# ── Camera Worker ──────────────────────────────────────────
class CameraWorker(QThread):
    frame_ready = pyqtSignal(np.ndarray)
    opened      = pyqtSignal()
    error       = pyqtSignal(str)

    def __init__(self, camera_index: int = 0):
        super().__init__()
        self.camera_index = camera_index
        self.running      = False
        self.paused       = False

    def run(self):
        self.running = True
        camera = CameraCapture(width=640, height=480, fps=15)

        if not camera.open() or not self.running:
            if self.running:
                hint = (
                    "Cannot open camera. Verify camera connection or run install.sh "
                    "to configure system drivers."
                )
                self.error.emit(hint)
            camera.release()
            return

        consecutive_failures = 0
        has_emitted_opened = False

        while self.running:
            try:
                if not self.paused:
                    ret, frame = camera.read()
                    if ret and frame is not None and frame.size > 0:
                        consecutive_failures = 0
                        # Only activate the UI after libcamera has supplied a frame.
                        if not has_emitted_opened:
                            has_emitted_opened = True
                            self.opened.emit()
                        self.frame_ready.emit(frame)
                    else:
                        consecutive_failures += 1
                        logger.warning(f"Camera frame read drop #{consecutive_failures}")
                        self.msleep(50)
                        if consecutive_failures >= 5:
                            logger.warning("Camera feed frame read failed repeatedly. Attempting to reconnect...")
                            consecutive_failures = 0
                            self.msleep(300)
                            if not self.running:
                                break
                            if not camera.reconnect():
                                self.error.emit("Camera feed lost and cannot reconnect.")
                                break

                self.msleep(66)
            except Exception as e:
                logger.error(f"Error in CameraWorker run loop: {e}")
                self.msleep(50)

        camera.release()

    def stop(self):
        self.running = False
        if not self.wait(1500):
            logger.warning("CameraWorker thread did not stop within timeout")

    def pause(self):  self.paused = True
    def resume(self): self.paused = False


# ── Video Worker ───────────────────────────────────────────
class VideoWorker(QThread):
    frame_ready = pyqtSignal(np.ndarray)
    finished    = pyqtSignal()
    error       = pyqtSignal(str)

    def __init__(self, video_path: str):
        super().__init__()
        self.video_path  = video_path
        self.running     = False
        self.paused      = False
        self._frame_pos  = 0

    def run(self):
        if not self.video_path or not os.path.exists(self.video_path):
            self.error.emit("Video file does not exist.")
            return

        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            cap.release()
            self.error.emit("Cannot open video file.")
            return

        if self._frame_pos > 0:
            cap.set(cv2.CAP_PROP_POS_FRAMES, self._frame_pos)

        self.running = True
        fps   = cap.get(cv2.CAP_PROP_FPS)
        delay = int(1000 / fps) if fps > 0 else 33
        delay = max(20, min(100, delay))

        while self.running:
            if not self.paused:
                ret, frame = cap.read()
                if ret and frame is not None:
                    self._frame_pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                    self.frame_ready.emit(frame)
                else:
                    self.finished.emit()
                    break
            self.msleep(delay)

        cap.release()

    def stop(self):
        self.running = False
        self.wait(1500)

    def pause(self):  self.paused = True
    def resume(self): self.paused = False


# ── Model Loader Worker ────────────────────────────────────
class ModelWorker(QThread):
    model_ready = pyqtSignal(object)
    error       = pyqtSignal(str)

    def __init__(self, model_loader, architecture, weight_file):
        super().__init__()
        self.model_loader = model_loader
        self.architecture = architecture
        self.weight_file  = weight_file

    def run(self):
        try:
            model = self.model_loader.load_model(self.architecture, self.weight_file)
            self.model_ready.emit(model)
        except Exception as e:
            self.error.emit(str(e))


# Alias for backward compatibility & persistent thread tracking
ModelLoaderThread = ModelWorker


# ── Inference Worker ───────────────────────────────────────
class InferenceWorker(QThread):
    results_ready = pyqtSignal(list, np.ndarray)  # (results, original_frame)
    error         = pyqtSignal(str)

    def __init__(self, predictor=None, skip_frames: int = 2):
        super().__init__()
        self.predictor     = predictor
        self.frame_queue   = queue.Queue(maxsize=1)
        self.running       = False
        # Initialize all counters & state as instance attributes to prevent UnboundLocalError
        self.frame_counter = 0
        self.skip_frames   = max(1, skip_frames)
        self.last_results  = []

    def set_predictor(self, predictor):
        self.predictor = predictor

    def predict_frame(self, frame: np.ndarray):
        if frame is None or self.predictor is None:
            return

        self.frame_counter += 1
        # Frame-skipping: process inference every Nth frame to reduce thermal/CPU load
        if self.frame_counter % self.skip_frames != 0:
            return

        # Safely put frame into queue without blocking Qt event loop
        try:
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass
            self.frame_queue.put_nowait(frame.copy())
        except (queue.Full, Exception):
            pass

    def run(self):
        self.running = True
        while self.running:
            try:
                frame = self.frame_queue.get(timeout=0.03)
            except queue.Empty:
                self.msleep(10)
                continue

            if not self.running:
                break

            if frame is None:
                continue

            try:
                results = self.predictor.predict(frame)
                if results and self.running:
                    self.last_results = results
                    self.results_ready.emit(results, frame)
            except Exception as e:
                logger.error(f"Inference worker error: {e}")
                if self.running:
                    self.error.emit(str(e))
            finally:
                try:
                    self.frame_queue.task_done()
                except ValueError:
                    pass

            self.msleep(10)

    def stop(self):
        self.running = False
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
                self.frame_queue.task_done()
            except (queue.Empty, ValueError):
                break
        self.wait(1500)


# ── Video Writer Worker ─────────────────────────────────────
class VideoWriterWorker(QThread):
    """Background worker to write video frames asynchronously."""
    def __init__(self, filepath: str, fps: int, width: int, height: int):
        super().__init__()
        self.filepath = filepath
        self.fps      = fps
        self.width    = width
        self.height   = height
        self.queue    = queue.Queue(maxsize=30)
        self.running  = False

    def write(self, frame: np.ndarray):
        if self.running and frame is not None and frame.size > 0:
            try:
                if self.queue.full():
                    try:
                        self.queue.get_nowait()
                    except queue.Empty:
                        pass
                self.queue.put_nowait(frame.copy())
            except Exception:
                pass

    def run(self):
        self.running = True
        writer = None
        writer_failed = False
        while self.running or not self.queue.empty():
            try:
                frame = self.queue.get(timeout=0.05)
                if frame is None or frame.size == 0 or writer_failed:
                    continue
                if writer is None:
                    fh, fw = frame.shape[:2]
                    try:
                        writer = cv2.VideoWriter(
                            self.filepath, cv2.VideoWriter_fourcc(*"MJPG"), self.fps, (fw, fh)
                        )
                        if not writer.isOpened():
                            logger.error(f"Failed to open VideoWriter for {self.filepath}")
                            writer_failed = True
                            continue
                    except Exception as exc:
                        logger.error(f"VideoWriter initialization failed: {exc}")
                        writer_failed = True
                        continue

                if writer is not None and writer.isOpened():
                    fh, fw = frame.shape[:2]
                    target_w, target_h = self.width, self.height
                    if (fw, fh) != (target_w, target_h):
                        try:
                            frame = cv2.resize(frame, (target_w, target_h))
                        except Exception:
                            pass
                    writer.write(frame)
                
                try:
                    self.queue.task_done()
                except ValueError:
                    pass
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error writing video frame: {e}")
        if writer is not None:
            try:
                writer.release()
            except Exception:
                pass

    def release(self):
        self.running = False
        if not self.wait(1500):
            logger.warning("VideoWriterWorker thread did not finish cleanly")


# ── Save Worker ────────────────────────────────────────────
class SaveWorker(QThread):
    """Runs save operations in background — prevents UI freeze."""
    finished = pyqtSignal(str)   # save_path
    error    = pyqtSignal(str)

    def __init__(
        self, save_manager, report_generator,
        patient_id, original_frame, detected_frame,
        snapshots, result, model_name, timestamp
    ):
        super().__init__()
        self.save_manager      = save_manager
        self.report_generator  = report_generator
        self.patient_id        = patient_id
        self.original_frame    = original_frame
        self.detected_frame    = detected_frame
        self.snapshots         = snapshots
        self.result            = result
        self.model_name        = model_name
        self.timestamp         = timestamp

    def run(self):
        try:
            save_path = self.save_manager.save_all(
                patient_id     = self.patient_id,
                original_frame = self.original_frame,
                detected_frame = self.detected_frame,
                snapshots      = self.snapshots,
                result         = self.result,
                model_name     = self.model_name,
                timestamp      = self.timestamp,
            )
            self.report_generator.generate(
                save_path  = save_path,
                patient_id = self.patient_id,
                result     = self.result,
                model_name = self.model_name,
                timestamp  = self.timestamp,
            )
            self.finished.emit(save_path)
        except Exception as e:
            self.error.emit(str(e))


# ── File Upload Worker ─────────────────────────────────────
class FileUploadWorker(QThread):
    """Runs file copy & image loading asynchronously in background."""
    finished = pyqtSignal(str, object)  # (saved_path, frame_or_none)
    error    = pyqtSignal(str)

    def __init__(self, save_manager, src_path: str, patient_id: str, timestamp: str):
        super().__init__()
        self.save_manager = save_manager
        self.src_path     = src_path
        self.patient_id   = patient_id
        self.timestamp    = timestamp

    def run(self):
        try:
            saved_path = self.save_manager.save_uploaded_file(self.src_path, self.patient_id, self.timestamp)
            if not saved_path:
                saved_path = self.src_path

            ext = os.path.splitext(saved_path)[1].lower()
            frame = None
            if ext in (".jpg", ".jpeg", ".png", ".bmp"):
                frame = cv2.imread(saved_path)

            self.finished.emit(saved_path, frame)
        except Exception as e:
            self.error.emit(str(e))


# ── Snapshot Card ──────────────────────────────────────────
class SnapshotCard(QWidget):
    def __init__(self, size_mode: str = "large", scale: float = 1.0):
        super().__init__()
        self.size_mode = size_mode

        def sc(pixels: int) -> int:
            return max(1, int(pixels * scale))

        w, h = sc(220), sc(160)
        img_w, img_h = sc(204), sc(110)
        font_img = f"{sc(9)}pt"
        font_disease = f"{sc(8)}pt"
        font_conf = f"{sc(8)}pt"
        padding_disease = "2px 4px"
            
        self.setFixedSize(w, h)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(sc(6), sc(6), sc(6), sc(6))
        layout.setSpacing(sc(4))

        self.img_label = QLabel()
        self.img_label.setFixedSize(img_w, img_h)
        self.img_label.setAlignment(ALIGN_CENTER)
        self.img_label.setStyleSheet(
            f"background:#F0F4F8;border-radius:4px;color:#A0AEC0;font-size:{font_img};"
        )
        self.img_label.setText("No Detection Yet")

        info_layout = QHBoxLayout()
        info_layout.setSpacing(sc(3))

        self.disease_label = QLabel("No Detection")
        self.disease_label.setStyleSheet(
            f"background:#2A7BDE;color:white;border-radius:3px;"
            f"font-size:{font_disease};font-weight:bold;padding:{padding_disease};"
        )
        self.conf_label = QLabel("")
        self.conf_label.setStyleSheet(
            f"color:#718096;font-size:{font_conf};background:transparent;"
        )

        info_layout.addWidget(self.disease_label)
        info_layout.addWidget(self.conf_label)
        info_layout.addStretch()

        layout.addWidget(self.img_label)
        layout.addLayout(info_layout)
        self.setStyleSheet(
            "QWidget{background:white;border-radius:8px;border:1px solid #E2E8F0;}"
        )


# ── Main Window ────────────────────────────────────────────
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VisionAI - Eye Disease Detection System")

        # Detect screen geometry and calculate adaptive UI scaling factor for any display
        screen = QApplication.primaryScreen()
        if screen:
            rect = screen.availableGeometry()
            self.screen_width = rect.width()
            self.screen_height = rect.height()
        else:
            self.screen_width = 1920
            self.screen_height = 1080

        self.ui_scale = min(self.screen_width / 1280.0, self.screen_height / 720.0)
        self.ui_scale = max(0.65, min(1.05, self.ui_scale))
        self.is_small = self.screen_width < 1024 or self.screen_height < 600
        self.is_micro = self.screen_width < 640 or self.screen_height < 480

        logger.info(
            f"Display geometry: {self.screen_width}x{self.screen_height} "
            f"(scale={self.ui_scale:.2f}, adaptive mode)"
        )

        font_family = "DejaVu Sans" if sys.platform.startswith("linux") else "Segoe UI"
        app_font = QFont(font_family, max(8, int(10 * self.ui_scale)))
        QApplication.setFont(app_font)

        # State
        self.current_frame      = None
        self.detected_frame     = None
        self.camera_worker      = None
        self.video_worker       = None
        self.video_writer       = None
        self.detected_video_writer = None
        self.model_loader       = ModelLoader()
        self.predictor          = None
        self.save_manager       = SaveManager()
        self.report_generator   = ReportGenerator()
        self.snapshots          = []
        self.snapshot_cards     = []
        self.is_camera_active   = False
        self.is_recording       = False
        self.is_paused          = False
        self.current_result     = None
        self.uploaded_file_path = None
        self.current_video_path = None
        self.save_worker        = None
        self.upload_worker      = None
        self.inference_worker   = None
        self.loader_thread      = None  # Persistent instance reference for model loading thread
        self.model_worker       = None  # Persistent instance reference for model worker
        self._preload_worker    = None  # Persistent instance reference for model pre-loader thread
        self._background_threads = set() # Persistent set tracking active QThread instances
        self.current_session_timestamp = None
        self.last_autosnap_time        = 0.0
        self.last_autosnap_disease     = None

        # Pre-init widgets
        self.progress_bar     = None
        self.progress_text    = None
        self.model_info_label = None
        self.status_dot       = None

        self.frame_counter = 0
        self.last_results  = []
        self._model_cache  = {}

        self.setStyleSheet("""
            QMainWindow { background:#F0F4F8; }
            QWidget { background:#F0F4F8; font-family:'Segoe UI'; }
            QScrollBar:horizontal { height:6px; background:#E2E8F0; border-radius:3px; }
            QScrollBar::handle:horizontal { background:#2A7BDE; border-radius:3px; }
            QToolTip { background:#1A2B4A; color:white; border:none;
                       padding:4px; border-radius:4px; }
        """)

        self._setup_status_bar()
        self._build_ui()
        QTimer.singleShot(50, lambda: self._on_model_changed(self.model_dropdown.currentText()))
        self.showMaximized()
        logger.info("MainWindow initialised successfully")

    def _s(self, pixels: int) -> int:
        """Scale fixed pixel sizes adaptively for the current display."""
        return max(1, int(pixels * self.ui_scale))

    def _track_thread(self, thread: QThread) -> QThread:
        """Attach thread instance to persistent set until finished to prevent Python GC during execution."""
        if thread is not None:
            self._background_threads.add(thread)
            thread.finished.connect(lambda: self._background_threads.discard(thread))
        return thread

    # ── Build UI ───────────────────────────────────────────
    def _build_ui(self):
        # Central area setup: lock scrollbars to prevent unwanted screen scrolling on 7-inch displays
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(NO_FRAME)
        scroll.setVerticalScrollBarPolicy(ALWAYS_OFF)
        scroll.setHorizontalScrollBarPolicy(ALWAYS_OFF)
        scroll.setStyleSheet("QScrollArea { background-color: #F0F4F8; border: none; }")
        self.setCentralWidget(scroll)

        central = QWidget()
        central.setStyleSheet("background-color: #F0F4F8;")
        scroll.setWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        self.title_bar = self._build_title_bar()
        self.model_bar = self._build_model_bar()
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.model_bar)

        # Display Area
        self.display_area = self._build_display_area()
        main_layout.addWidget(self.display_area, stretch=1)

        # Snapshots Bar
        self.snapshots_bar = self._build_snapshots_bar()
        main_layout.addWidget(self.snapshots_bar)

        # Bottom Bar
        self.bottom_bar = self._build_bottom_bar()
        main_layout.addWidget(self.bottom_bar)

    def _build_title_bar(self):
        widget = QWidget()
        widget.setFixedHeight(self._s(38) if self.is_small else self._s(55))
        widget.setStyleSheet("background:white;border-bottom:2px solid #E2E8F0;")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(self._s(20), 0, self._s(20), 0)
        title = QLabel("VisionAI")
        title.setAlignment(ALIGN_CENTER)
        font_size = self._s(16) if self.is_small else self._s(24)
        title.setStyleSheet(f"""
            color:#1A2B4A;font-size:{font_size}pt;font-weight:bold;
            font-family:'Segoe UI';letter-spacing:3px;background:transparent;
        """)
        layout.addWidget(title)
        return widget

    def _build_model_bar(self):
        widget = QWidget()
        widget.setFixedHeight(self._s(34) if self.is_small else self._s(45))
        widget.setStyleSheet("background:#F8FAFC;border-bottom:1px solid #E2E8F0;")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(self._s(20), self._s(2), self._s(20), self._s(2))
        layout.setSpacing(self._s(12))
        label = QLabel("🧠 Select AI Model:")
        label.setStyleSheet(f"color:#1A2B4A;font-weight:bold;font-size:{self._s(9 if self.is_small else 10)}pt;background:transparent;")
        self.model_dropdown = QComboBox()
        self.model_dropdown.setStyleSheet(DROPDOWN_STYLE)
        self.model_dropdown.setMinimumWidth(self._s(200 if self.is_small else 220))
        self.model_dropdown.setMaximumWidth(self._s(320))
        self.model_dropdown.setFixedHeight(self._s(28 if self.is_small else 34))
        for name in MODEL_INFO.keys():
            self.model_dropdown.addItem(name)
        self.model_dropdown.currentTextChanged.connect(self._on_model_changed)
        self.model_info_label = QLabel()
        self.model_info_label.setStyleSheet("color:#718096;font-size:9pt;background:transparent;")
        layout.addWidget(label)
        layout.addWidget(self.model_dropdown)
        layout.addWidget(self.model_info_label)
        layout.addStretch()
        return widget

    def _build_display_area(self):
        widget = QWidget()
        widget.setStyleSheet("background:#F0F4F8;")
        widget.setMinimumHeight(self._s(240) if self.is_small else self._s(360))

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(self._s(12), self._s(6), self._s(12), self._s(6))
        layout.setSpacing(self._s(12))

        title_h = self._s(28 if self.is_small else 36)
        title_font = f"{self._s(9 if self.is_small else 10)}pt"

        left   = QWidget()
        left.setStyleSheet("background:white;border-radius:12px;border:2px solid #3B82F6;")
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(0, 0, 0, 0)
        left_l.setSpacing(0)
        left_title = QLabel("LIVE CAMERA / INPUT FEED")
        left_title.setFixedHeight(title_h)
        left_title.setAlignment(ALIGN_CENTER)
        left_title.setStyleSheet(f"""
            color:#1A2B4A;font-size:{title_font};font-weight:bold;letter-spacing:1px;
            background:transparent;border-bottom:2px solid #3B82F6;padding:2px;
        """)
        self.input_display = QLabel()
        self.input_display.setAlignment(ALIGN_CENTER)
        self.input_display.setMinimumSize(240 if self.is_small else 320, 180 if self.is_small else 240)
        self.input_display.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.input_display.setStyleSheet(f"QLabel{{background:#0F172A;color:#475569;font-size:{self._s(9 if self.is_small else 10)}pt;letter-spacing:2px;}}")
        self.input_display.setText("INITIALIZING FEED...")
        left_l.addWidget(left_title)
        left_l.addWidget(self.input_display, stretch=1)

        right   = QWidget()
        right.setStyleSheet("background:white;border-radius:12px;border:2px solid #EF4444;")
        right_l = QVBoxLayout(right)
        right_l.setContentsMargins(0, 0, 0, 0)
        right_l.setSpacing(0)
        right_title = QLabel("DISEASE DETECTION AI")
        right_title.setFixedHeight(title_h)
        right_title.setAlignment(ALIGN_CENTER)
        right_title.setStyleSheet(f"""
            color:#1A2B4A;font-size:{title_font};font-weight:bold;letter-spacing:1px;
            background:transparent;border-bottom:2px solid #EF4444;padding:2px;
        """)
        self.output_display = QLabel()
        self.output_display.setAlignment(ALIGN_CENTER)
        self.output_display.setMinimumSize(240 if self.is_small else 320, 180 if self.is_small else 240)
        self.output_display.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.output_display.setStyleSheet(f"QLabel{{background:#0F172A;color:#475569;font-size:{self._s(9 if self.is_small else 10)}pt;letter-spacing:2px;}}")
        self.output_display.setText("INITIALIZING FEED...")
        right_l.addWidget(right_title)
        right_l.addWidget(self.output_display, stretch=1)

        layout.addWidget(left,  stretch=1)
        layout.addWidget(right, stretch=1)

        return widget

    def _build_snapshots_bar(self):
        widget = QWidget()
        widget.setFixedHeight(self._s(120) if self.is_small else self._s(180))
        widget.setStyleSheet("background:#F8FAFC;border-top:1px solid #E2E8F0;")
        
        bar_layout = QHBoxLayout(widget)
        bar_layout.setContentsMargins(12, 6, 12, 6)
        bar_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(NO_FRAME)
        scroll.setVerticalScrollBarPolicy(ALWAYS_OFF)
        scroll.setHorizontalScrollBarPolicy(AS_NEEDED)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.snapshot_cards = []
        card_size = "small" if self.is_small else "large"
        for _ in range(5):
            card = SnapshotCard(card_size, scale=self.ui_scale)
            self.snapshot_cards.append(card)
            layout.addWidget(card)

        scroll.setWidget(container)
        bar_layout.addWidget(scroll)
        return widget

    def _build_bottom_bar(self):
        widget = QWidget()
        widget.setStyleSheet("background:white;border-top:2px solid #E2E8F0;")

        self.patient_id_input = QLineEdit()
        self.patient_id_input.setText("")
        self.patient_id_input.setPlaceholderText("Enter Patient ID (e.g. PT-001)")
        self.patient_id_input.setStyleSheet("""
            QLineEdit { background:white;color:#1A2B4A;border:2px solid #CBD5E0;
                border-radius:8px;padding:4px 10px;font-size:10pt; }
            QLineEdit:focus { border:2px solid #3B82F6; }
        """)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(PROGRESS_BAR_STYLE)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        self.progress_text = QLabel("0%")
        self.progress_text.setStyleSheet("color:#718096;font-size:9pt;background:transparent;")

        self.status_dot = QLabel("● System Ready")
        self.status_dot.setStyleSheet("color:#22C55E;font-size:8pt;background:transparent;")

        def make_btn(text, color, hover, height, font_size):
            b = QPushButton(text)
            b.setFixedHeight(height)
            b.setStyleSheet(f"""
                QPushButton {{ background:{color};color:white;border:none;
                    border-radius:8px;padding:6px 12px;font-size:{font_size}pt;font-weight:bold; }}
                QPushButton:hover {{ background:{hover}; }}
                QPushButton:disabled {{ background:#CBD5E0; }}
            """)
            return b

        btn_height = self._s(42)
        btn_font = max(7, int(9 * self.ui_scale))

        self.save_btn   = make_btn("💾 SAVE",         "#22C55E", "#16A34A", btn_height, btn_font)
        self.upload_btn = make_btn("📁 Load Video",   "#F59E0B", "#D97706", btn_height, btn_font)
        self.camera_btn = make_btn("📷 Start Camera", "#3B82F6", "#2563EB", btn_height, btn_font)
        self.pause_btn  = make_btn("⏸ Pause",         "#EF4444", "#DC2626", btn_height, btn_font)
        self.photo_btn  = make_btn("📸 Capture",      "#8B5CF6", "#7C3AED", btn_height, btn_font)

        self.save_btn.clicked.connect(self._save_results)
        self.upload_btn.clicked.connect(self._upload_file)
        self.camera_btn.clicked.connect(self._toggle_camera)
        self.pause_btn.clicked.connect(self._toggle_pause)
        self.photo_btn.clicked.connect(self._capture_photo)

        self.save_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.photo_btn.setEnabled(False)

        def make_divider():
            d = QFrame()
            d.setFrameShape(VLINE)
            d.setStyleSheet("color:#E2E8F0;")
            return d

        widget.setFixedHeight(self._s(100))
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(self._s(12), self._s(8), self._s(12), self._s(8))
        layout.setSpacing(self._s(12))

        logo_widget = QWidget()
        logo_widget.setFixedWidth(self._s(230))
        logo_widget.setStyleSheet("background:transparent;")
        logo_l = QHBoxLayout(logo_widget)
        logo_l.setContentsMargins(0, 0, 0, 0)
        logo_l.setSpacing(self._s(8))
        self.logo_label = QLabel()
        logo_size = self._s(75)
        self.logo_label.setFixedSize(logo_size, logo_size)
        self.logo_label.setAlignment(ALIGN_CENTER)
        if getattr(sys, "frozen", False):
            base_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
            logo_path = os.path.join(base_dir, "assets", "smartlab_logo.png")
            if not os.path.exists(logo_path):
                logo_path = os.path.join(base_dir, "assets", "smartlab_logo.ico")
        else:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "smartlab_logo.png")
            if not os.path.exists(logo_path):
                logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "smartlab_logo.ico")
        if os.path.exists(logo_path):
            px = QPixmap(logo_path)
            icon_size = self._s(73)
            self.logo_label.setPixmap(px.scaled(icon_size, icon_size, KEEP_ASPECT, SMOOTH_TRANSFORM))
        else:
            self.logo_label.setText("SMART")
            self.logo_label.setStyleSheet(f"color:#1A2B4A;font-weight:bold;font-size:{self._s(12)}pt;")
        
        logo_text_l = QVBoxLayout()
        logo_text_l.setSpacing(2)
        logo_name = QLabel("VisionAI")
        logo_name.setStyleSheet(f"color:#1A2B4A;font-size:{self._s(13)}pt;font-weight:bold;background:transparent;")
        logo_sub = QLabel("Sanjivani Multidisciplinary AI\nResearch & Technology")
        logo_sub.setStyleSheet(f"color:#718096;font-size:{self._s(7)}pt;background:transparent;")
        logo_text_l.addWidget(logo_name)
        logo_text_l.addWidget(logo_sub)
        logo_l.addWidget(self.logo_label)
        logo_l.addLayout(logo_text_l)

        patient_w = QWidget()
        patient_w.setFixedWidth(self._s(190))
        patient_w.setStyleSheet("background:transparent;")
        patient_l = QVBoxLayout(patient_w)
        patient_l.setContentsMargins(0, 0, 0, 0)
        patient_l.setSpacing(4)
        p_label = QLabel("Patient ID")
        p_label.setStyleSheet(f"color:#1A2B4A;font-weight:bold;font-size:{self._s(9)}pt;background:transparent;")
        self.patient_id_input.setFixedHeight(self._s(36))
        patient_l.addWidget(p_label)
        patient_l.addWidget(self.patient_id_input)

        btn_w = QWidget()
        btn_w.setStyleSheet("background:transparent;")
        btn_l = QHBoxLayout(btn_w)
        btn_l.setContentsMargins(0, 0, 0, 0)
        btn_l.setSpacing(8)
        btn_l.addWidget(self.save_btn)
        btn_l.addWidget(self.upload_btn)
        btn_l.addWidget(self.camera_btn)
        btn_l.addWidget(self.pause_btn)
        btn_l.addWidget(self.photo_btn)

        prog_w = QWidget()
        prog_w.setFixedWidth(self._s(180))
        prog_w.setStyleSheet("background:transparent;")
        prog_l = QVBoxLayout(prog_w)
        prog_l.setContentsMargins(0, 0, 0, 0)
        prog_l.setSpacing(5)
        prog_title = QLabel("Processing Progress")
        prog_title.setStyleSheet(f"color:#1A2B4A;font-weight:bold;font-size:{self._s(9)}pt;background:transparent;")
        prog_row = QHBoxLayout()
        self.progress_bar.setFixedHeight(self._s(10))
        self.progress_text.setFixedWidth(self._s(35))
        self.progress_text.setStyleSheet(f"color:#718096;font-size:{self._s(9)}pt;background:transparent;")
        prog_row.addWidget(self.progress_bar)
        prog_row.addWidget(self.progress_text)
        
        prog_l.addWidget(prog_title)
        prog_l.addLayout(prog_row)
        prog_l.addWidget(self.status_dot)

        layout.addWidget(logo_widget)
        layout.addWidget(make_divider())
        layout.addWidget(patient_w)
        layout.addWidget(make_divider())
        layout.addWidget(btn_w, stretch=1)
        layout.addWidget(make_divider())
        layout.addWidget(prog_w)
        self._update_camera_btn_style()
        return widget

    # ── Status Bar ─────────────────────────────────────────
    def _setup_status_bar(self):
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet(STATUS_BAR_STYLE)
        self.status_bar.showMessage("✅ VisionAI Ready")

    # ── Model Changed ──────────────────────────────────────
    def _weights_dir(self) -> str:
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
            return os.path.join(base_dir, "weights")
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "weights")

    def _on_model_changed(self, model_name: str):
        if not model_name or model_name not in MODEL_INFO:
            return
        info = MODEL_INFO[model_name]
        if self.model_info_label:
            self.model_info_label.setText(
                f"Accuracy: {info['accuracy']} | {info['parameters']} params | {info['description']}"
            )

        weight_file = os.path.join(self._weights_dir(), info["file"])
        if not os.path.exists(weight_file):
            self.status_bar.showMessage(f"⚠️ Weight not found: {info['file']}")
            self._set_progress(0, "0%")
            self._update_dot("● Weight Missing", "#EF4444")
            return

        cache_key = info["file"]
        if cache_key in self._model_cache:
            self._on_model_loaded(self._model_cache[cache_key], model_name, info)
            return

        if self.model_worker is not None:
            try:
                self.model_worker.model_ready.disconnect()
                self.model_worker.error.disconnect()
            except Exception:
                pass
            if self.model_worker.isRunning():
                self.model_worker.wait(1500)

        if self.inference_worker is not None:
            self.inference_worker.set_predictor(None)

        self.model_dropdown.setEnabled(False)
        self.camera_btn.setEnabled(False)
        self.upload_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.status_bar.showMessage(f"⏳ Loading: {model_name}...")
        self._set_progress(10, "10%")
        self._update_dot("● Loading...", "#F59E0B")

        self.model_worker = ModelWorker(self.model_loader, info["architecture"], weight_file)
        self.loader_thread = self.model_worker  # Persistent instance reference
        self._track_thread(self.model_worker)
        self.model_worker.model_ready.connect(
            lambda model: self._on_model_loaded(model, model_name, info)
        )
        self.model_worker.error.connect(self._on_model_error)
        self.model_worker.start()

    def _preload_remaining_models(self) -> None:
        if self._preload_worker is not None and self._preload_worker.isRunning():
            return

        weights_dir = self._weights_dir()
        pending = []
        for name, info in MODEL_INFO.items():
            if info["file"] in self._model_cache:
                continue
            weight_file = os.path.join(weights_dir, info["file"])
            if os.path.exists(weight_file):
                pending.append((info["architecture"], info["file"], weight_file))

        if not pending:
            return

        architecture, cache_key, weight_file = pending[0]

        def _on_preloaded(model, key=cache_key):
            self._model_cache[key] = model
            logger.info(f"Preloaded model: {key}")
            QTimer.singleShot(200, self._preload_remaining_models)

        def _on_preload_error(_msg, key=cache_key):
            logger.warning(f"Preload skipped for {key}")
            QTimer.singleShot(200, self._preload_remaining_models)

        self._preload_worker = ModelWorker(self.model_loader, architecture, weight_file)
        self._track_thread(self._preload_worker)
        self._preload_worker.model_ready.connect(_on_preloaded)
        self._preload_worker.error.connect(_on_preload_error)
        self._preload_worker.start()

    def _on_model_loaded(self, model, model_name, info):
        self._model_cache[info["file"]] = model
        self.predictor = Predictor(model)
        if self.inference_worker is None:
            self.inference_worker = InferenceWorker(self.predictor)
            self._track_thread(self.inference_worker)
            self.inference_worker.results_ready.connect(
                self._on_prediction_ready, QUEUED_CONNECTION
            )
            self.inference_worker.error.connect(
                self._on_prediction_error, QUEUED_CONNECTION
            )
            self.inference_worker.start()
        else:
            self.inference_worker.set_predictor(self.predictor)

        self.model_dropdown.setEnabled(True)
        self.camera_btn.setEnabled(True)
        self.upload_btn.setEnabled(True)
        self.status_bar.showMessage(f"✅ {model_name} — {info['accuracy']} accuracy")
        self._set_progress(100, "100%")
        self._update_dot("● Model Ready", "#22C55E")
        logger.info(f"Model loaded: {model_name}")
        QTimer.singleShot(500, self._preload_remaining_models)

    def _on_prediction_ready(self, results: list, frame: np.ndarray):
        if not results or frame is None or frame.size == 0:
            return
        self.last_results = results
        top        = results[0]
        disease    = top["class"]
        confidence = top["confidence"]
        detected   = self._draw_overlay(frame.copy(), disease, confidence, results)
        self.detected_frame = detected
        self._display_frame(detected, self.output_display)
        
        self.current_result = {
            "disease":    disease,
            "confidence": confidence,
            "results":    results,
            "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        if disease != "Normal":
            self._auto_snapshot(detected, disease, confidence, is_manual=False)
        pct   = int(confidence)
        color = DISEASE_COLORS.get(disease, "#2A7BDE")
        self._set_progress(pct, f"{pct}%")
        self._update_dot(f"● {disease} {confidence:.1f}%", color)
        self.status_bar.showMessage(
            f"🔍 {disease} | {confidence:.1f}% | {self.model_dropdown.currentText()}"
        )
        self.save_btn.setEnabled(True)

    def _on_prediction_error(self, error_msg: str):
        logger.error(f"Inference thread error: {error_msg}")
        self.status_bar.showMessage(f"❌ Inference error: {error_msg}")

    def _on_model_error(self, error_msg):
        self.model_dropdown.setEnabled(True)
        self.camera_btn.setEnabled(True)
        self.upload_btn.setEnabled(True)
        self.status_bar.showMessage(f"❌ {error_msg}")
        self._set_progress(0, "0%")
        self._update_dot("● Error", "#EF4444")
        QMessageBox.critical(self, "Model Load Error", error_msg)

    def _update_camera_btn_style(self):
        font_sz = 7 if self.is_micro else 9
        border_r = 6 if self.is_micro else 8
        if self.is_camera_active:
            self.camera_btn.setText("⏹ Stop" if self.is_micro else "⏹ Stop Camera")
            self.camera_btn.setStyleSheet(f"""
                QPushButton {{ background:#DC2626;color:white;border:none;
                    border-radius:{border_r}px;padding:4px;font-size:{font_sz}pt;font-weight:bold; }}
                QPushButton:hover {{ background:#B91C1C; }}
            """)
        else:
            self.camera_btn.setText("📷 Start" if self.is_micro else "📷 Start Camera")
            self.camera_btn.setStyleSheet(f"""
                QPushButton {{ background:#3B82F6;color:white;border:none;
                    border-radius:{border_r}px;padding:4px;font-size:{font_sz}pt;font-weight:bold; }}
                QPushButton:hover {{ background:#2563EB; }}
            """)

    # ── Camera Controls ────────────────────────────────────
    def _toggle_camera(self):
        if self.is_camera_active:
            self._stop_camera()
        else:
            self._start_camera()

    def _start_camera(self):
        if not self._check_patient_id():
            return
        if self.camera_worker is not None and self.camera_worker.isRunning():
            self.camera_worker.stop()
        self.current_session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.camera_worker = CameraWorker(0)
        self._track_thread(self.camera_worker)
        self.camera_worker.frame_ready.connect(
            self._process_frame, QUEUED_CONNECTION
        )
        self.camera_worker.opened.connect(
            self._on_camera_opened, QUEUED_CONNECTION
        )
        self.camera_worker.error.connect(
            self._on_camera_error, QUEUED_CONNECTION
        )
        self.camera_worker.start()
        self.camera_btn.setEnabled(False)
        self.status_bar.showMessage("📷 Starting camera...")
        self._update_dot("● Starting camera", "#F59E0B")

    def _on_camera_opened(self):
        """Activate controls only after the worker has read its first frame."""
        if self.camera_worker is None or not self.camera_worker.isRunning():
            return

        self.is_camera_active = True
        self._start_recording()
        self.camera_btn.setEnabled(True)
        self._update_camera_btn_style()
        self.pause_btn.setEnabled(True)
        self.photo_btn.setEnabled(True)

        if is_raspberry_pi():
            self.status_bar.showMessage("📷 Camera active")
            self._update_dot("● Camera active", "#3B82F6")
        else:
            self.status_bar.showMessage("📷 Camera active — recording started...")
            self._update_dot("● Camera + Recording", "#3B82F6")

    def _stop_camera(self):
        if self.is_recording:
            self._stop_recording()
        if self.current_result:
            self._save_results()
        if self.camera_worker:
            self.camera_worker.stop()
            self.camera_worker = None
        self.is_camera_active = False
        self.is_paused        = False
        self._update_camera_btn_style()
        self.pause_btn.setEnabled(False)
        self.photo_btn.setEnabled(False)
        self.pause_btn.setText("⏸ Pause")
        self.status_bar.showMessage("⏹ Camera stopped — recording saved")
        self._update_dot("● System Ready", "#22C55E")
        self._set_progress(0, "0%")

    def _on_camera_error(self, msg):
        self.camera_btn.setEnabled(True)
        QMessageBox.warning(self, "Camera Error", msg)
        self._stop_camera()

    # ── Recording ──────────────────────────────────────────
    def _start_recording(self):
        if self.current_frame is None and not self.is_camera_active:
            return
        patient_id = self.patient_id_input.text().strip() or "unknown"
        if not self.current_session_timestamp:
            self.current_session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path_live = self.save_manager.get_recording_path(patient_id, self.current_session_timestamp, is_detected=False)
        path_detected = self.save_manager.get_recording_path(patient_id, self.current_session_timestamp, is_detected=True)

        if self.current_frame is not None and self.current_frame.size > 0:
            h, w = self.current_frame.shape[:2]
        else:
            h, w = 480, 640

        if is_raspberry_pi():
            # OpenCV's MJPEG VideoWriter can be unstable with libcamera on Pi.
            # Snapshots and the live diagnosis remain available.
            logger.info("Raspberry Pi detected: video recording disabled for camera stability")
            self.video_writer = None
            self.detected_video_writer = None
        else:
            self.video_writer = VideoWriterWorker(path_live, 20, w, h)
            self._track_thread(self.video_writer)
            self.video_writer.start()

            self.detected_video_writer = VideoWriterWorker(path_detected, 20, w, h)
            self._track_thread(self.detected_video_writer)
            self.detected_video_writer.start()
        self.is_recording = True
        logger.info(f"Recordings started — Live: {path_live if self.video_writer else 'Disabled'}, Detected: {path_detected}")

    def _stop_recording(self):
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        if self.detected_video_writer:
            self.detected_video_writer.release()
            self.detected_video_writer = None
        self.is_recording = False
        logger.info("Recording stopped and saved")

    # ── Pause ──────────────────────────────────────────────
    def _toggle_pause(self):
        if self.is_paused:
            if self.camera_worker: self.camera_worker.resume()
            if self.video_worker:  self.video_worker.resume()
            self.is_paused = False
            self.pause_btn.setText("⏸ Pause")
            self.status_bar.showMessage("▶️ Resumed")
        else:
            if self.camera_worker: self.camera_worker.pause()
            if self.video_worker:  self.video_worker.pause()
            self.is_paused = True
            self.pause_btn.setText("▶️ Resume")
            self.status_bar.showMessage("⏸ Paused")

    # ── Capture Photo ──────────────────────────────────────
    # ── Capture Photo ──────────────────────────────────────
    def _capture_photo(self):
        if self.current_frame is None or self.current_frame.size == 0:
            return
        if not self.current_result and self.predictor:
            try:
                results = self.predictor.predict(self.current_frame)
                if results:
                    self._on_prediction_ready(results, self.current_frame)
            except Exception as e:
                logger.error(f"Error predicting photo capture: {e}")

        disease    = self.current_result["disease"]    if self.current_result else "Normal"
        confidence = self.current_result["confidence"] if self.current_result else 0.0
        frame_to_snap = self.detected_frame if self.detected_frame is not None else self.current_frame
        self._auto_snapshot(frame_to_snap.copy(), disease, confidence, is_manual=True)
        self.status_bar.showMessage("📸 Photo captured!")

    # ── Upload File ────────────────────────────────────────
    def _upload_file(self):
        if not self._check_patient_id():
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image or Video", "",
            "Media Files (*.jpg *.jpeg *.png *.bmp *.mp4 *.avi *.mov)",
        )
        if not file_path:
            return
        self.current_session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        patient_id = self.patient_id_input.text().strip() or "unknown"

        self.status_bar.showMessage("⏳ Loading uploaded file in background...")
        self._set_progress(15, "15%")

        if self.upload_worker is not None and self.upload_worker.isRunning():
            self.upload_worker.wait(1000)

        self.upload_worker = FileUploadWorker(
            save_manager=self.save_manager,
            src_path=file_path,
            patient_id=patient_id,
            timestamp=self.current_session_timestamp,
        )
        self._track_thread(self.upload_worker)
        self.upload_worker.finished.connect(self._on_upload_file_finished, QUEUED_CONNECTION)
        self.upload_worker.error.connect(
            lambda e: QMessageBox.warning(self, "Upload Error", e),
            QUEUED_CONNECTION,
        )
        self.upload_worker.start()

    def _on_upload_file_finished(self, saved_path: str, frame: object):
        self.uploaded_file_path = saved_path
        ext = os.path.splitext(saved_path)[1].lower()
        if ext in (".jpg", ".jpeg", ".png", ".bmp"):
            if frame is None or getattr(frame, "size", 0) == 0:
                QMessageBox.warning(self, "Error", "Cannot load image.")
                return
            self._set_progress(30, "30%")
            self._process_frame(frame)
            if self.predictor:
                try:
                    results = self.predictor.predict(frame)
                    if results:
                        self._on_prediction_ready(results, frame)
                except Exception as e:
                    logger.error(f"Error predicting loaded image: {e}")
            self.status_bar.showMessage(f"🖼️ {os.path.basename(saved_path)}")
        elif ext in (".mp4", ".avi", ".mov"):
            self._load_video(saved_path)
        else:
            QMessageBox.warning(self, "Invalid File", "Select a valid image or video.")

    def _load_image(self, path: str):
        frame = cv2.imread(path)
        if frame is None or frame.size == 0:
            QMessageBox.warning(self, "Error", "Cannot load image.")
            return
        self._set_progress(30, "30%")
        self._process_frame(frame)
        if self.predictor:
            try:
                results = self.predictor.predict(frame)
                if results:
                    self._on_prediction_ready(results, frame)
            except Exception as e:
                logger.error(f"Error predicting loaded image: {e}")
        self.status_bar.showMessage(f"🖼️ {os.path.basename(path)}")

    def _load_video(self, path: str):
        if self.is_camera_active:
            self._stop_camera()
        if self.video_worker:
            self.video_worker.stop()
            self.video_worker = None
        if self.is_recording:
            self._stop_recording()

        self.current_video_path = path

        self.video_worker = VideoWorker(path)
        self._track_thread(self.video_worker)
        self.video_worker.frame_ready.connect(
            self._process_frame, QUEUED_CONNECTION
        )
        self.video_worker.finished.connect(
            self._on_video_finished, QUEUED_CONNECTION
        )
        self.video_worker.error.connect(
            lambda e: QMessageBox.warning(self, "Error", e),
            QUEUED_CONNECTION,
        )
        self.video_worker.start()

        self._start_recording()
        self.pause_btn.setEnabled(True)
        self.status_bar.showMessage(f"🎬 {os.path.basename(path)} — recording...")
        self._update_dot("● Video + Recording", "#F59E0B")

    def _on_video_finished(self):
        if self.is_recording:
            self._stop_recording()
        if self.current_result:
            self._save_results()
        self.video_worker = None
        self.pause_btn.setEnabled(False)
        self.status_bar.showMessage("✅ Video complete — restarting camera...")
        self._set_progress(100, "100%")

        if self._check_patient_id(silent=True):
            self._start_camera()

    # ── Process Frame ──────────────────────────────────────
    def _process_frame(self, frame: np.ndarray):
        try:
            if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
                return

            self._display_frame(frame, self.input_display)
            self.current_frame = frame.copy()

            if self.is_recording:
                if self.video_writer:
                    self.video_writer.write(frame)
                if self.detected_video_writer:
                    if self.detected_frame is not None and self.detected_frame.shape == frame.shape:
                        self.detected_video_writer.write(self.detected_frame)
                    else:
                        self.detected_video_writer.write(frame)

            if self.predictor is None or self.inference_worker is None:
                self._display_frame(frame, self.output_display)
                return

            # Background prediction (drops frame if queue full)
            self.inference_worker.predict_frame(frame)

            if self.last_results:
                top = self.last_results[0]
                detected = self._draw_overlay(
                    frame.copy(), top["class"], top["confidence"], self.last_results
                )
                self._display_frame(detected, self.output_display)
            else:
                self._display_frame(frame, self.output_display)
        except Exception as e:
            logger.error(f"Error in _process_frame: {e}")

    # ── Draw Overlay ───────────────────────────────────────
    def _draw_overlay(self, frame, disease, confidence, results):
        try:
            if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0 or frame.ndim != 3:
                return frame
            h, w = frame.shape[:2]
            if h <= 0 or w <= 0:
                return frame
            color_map = {
                "AMD":      (0,   0,   220),
                "Cataract": (0,   140, 255),
                "Dementia": (128, 0,   180),
                "Diabetes": (0,   200, 255),
                "Glaucoma": (255, 80,  0  ),
                "Normal":   (0,   200, 0  ),
            }
            color = color_map.get(disease, (42, 123, 222))
            conf_val = float(confidence) if confidence is not None else 0.0

            cv2.rectangle(frame, (0, 0), (w, 52), (15, 23, 42), -1)
            cv2.putText(frame, str(disease), (12, 36), cv2.FONT_HERSHEY_SIMPLEX, 1.1, color, 2)
            cv2.putText(frame, f"{conf_val:.1f}%", (max(10, w-115), 36), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
            cv2.rectangle(frame, (0, max(0, h-65)), (w, h), (15, 23, 42), -1)
            if results and isinstance(results, list):
                for i, res in enumerate(results[:3]):
                    x  = 12 + i * max(1, (w // 3))
                    res_class = str(res.get('class', 'Unknown'))
                    res_conf  = float(res.get('confidence', 0.0))
                    cv2.putText(frame, f"{res_class}: {res_conf:.1f}%",
                        (x, max(0, h-40)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (126, 179, 245), 1)
                    bw = max(0, min(w // 3 - 10, int((res_conf / 100.0) * max(10, (w // 3 - 20)))))
                    cv2.rectangle(frame, (x, max(0, h-28)), (x+bw, max(0, h-14)), color, -1)
            cv2.rectangle(frame, (2, 2), (w-2, h-2), color, 2)
            return frame
        except Exception as e:
            logger.error(f"Error in _draw_overlay: {e}")
            return frame

    # ── Display Frame ──────────────────────────────────────
    def _display_frame(self, frame: np.ndarray, label: QLabel):
        try:
            if frame is None or label is None or frame.size == 0 or frame.ndim != 3:
                return
            if label.width() <= 0 or label.height() <= 0:
                return
            rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qt_img = QImage(rgb.tobytes(), w, h, ch * w, RGB888).copy()
            pixmap = QPixmap.fromImage(qt_img)
            label.setPixmap(pixmap.scaled(
                label.size(),
                KEEP_ASPECT,
                SMOOTH_TRANSFORM,
            ))
        except Exception as e:
            logger.error(f"Error in _display_frame: {e}")

    # ── Auto Snapshot ──────────────────────────────────────
    def _auto_snapshot(self, frame, disease, confidence, is_manual: bool = False):
        try:
            if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
                return
            import time
            now = time.time()

            if not is_manual:
                cooldown = 5.0 if disease == getattr(self, "last_autosnap_disease", None) else 1.5
                if now - getattr(self, "last_autosnap_time", 0.0) < cooldown:
                    return
                self.last_autosnap_time = now
                self.last_autosnap_disease = disease

            timestamp = datetime.now().strftime("%H:%M:%S")
            self.snapshots.insert(0, {
                "frame": frame.copy(), "disease": disease,
                "confidence": confidence, "timestamp": timestamp,
            })
            if len(self.snapshots) > 5:
                self.snapshots = self.snapshots[:5]

            if self.current_session_timestamp:
                patient_id = self.patient_id_input.text().strip() or "unknown"
                patient_path = self.save_manager._get_patient_folder(patient_id)
                snapshots_dir = os.path.join(patient_path, "captured_images")
                os.makedirs(snapshots_dir, exist_ok=True)
                file_ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                tag = "manual" if is_manual else "autosnap"
                filename = f"captured_{file_ts}_{tag}_{disease}_{confidence:.0f}pct.jpg"
                filepath = os.path.join(snapshots_dir, filename)
                import threading
                threading.Thread(target=cv2.imwrite, args=(filepath, frame.copy()), daemon=True).start()
                logger.info(f"Saved snapshot ({tag}) in background: {filepath}")

            for i, card in enumerate(self.snapshot_cards):
                if i < len(self.snapshots):
                    s = self.snapshots[i]
                    try:
                        rgb2 = cv2.cvtColor(s["frame"], cv2.COLOR_BGR2RGB)
                        h2, w2, ch2 = rgb2.shape
                        qi    = QImage(rgb2.tobytes(), w2, h2, ch2*w2, RGB888).copy()
                        px    = QPixmap.fromImage(qi)
                        color = DISEASE_COLORS.get(s["disease"], "#2A7BDE")
                        card_w = max(1, card.img_label.width())
                        card_h = max(1, card.img_label.height())
                        card.img_label.setPixmap(px.scaled(
                            card_w,
                            card_h,
                            KEEP_ASPECT,
                            SMOOTH_TRANSFORM,
                        ))
                        card.img_label.setStyleSheet("background:#1A2B4A;border-radius:6px;")
                        card.disease_label.setText(s["disease"])
                        card.disease_label.setStyleSheet(
                            f"background:{color};color:white;border-radius:4px;"
                            f"font-size:8pt;font-weight:bold;padding:2px 6px;"
                        )
                        card.conf_label.setText(f"{s['confidence']:.0f}%")
                    except Exception as e:
                        logger.error(f"Snapshot update error: {e}")
        except Exception as e:
            logger.error(f"Error in _auto_snapshot: {e}")

    # ── Save Results ───────────────────────────────────────
    def _save_results(self):
        patient_id = self.patient_id_input.text().strip()
        if not patient_id:
            QMessageBox.warning(self, "Patient ID", "Please enter a Patient ID.")
            return
        if not self.current_result:
            QMessageBox.warning(self, "No Results", "No detection results to save.")
            return

        self.save_btn.setEnabled(False)
        self._set_progress(20, "20%")
        self._update_dot("● Saving...", "#F59E0B")
        self.status_bar.showMessage("💾 Saving in background...")

        if not self.current_session_timestamp:
            self.current_session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        if self.save_worker is not None and self.save_worker.isRunning():
            self.save_worker.wait(1500)

        self.save_worker = SaveWorker(
            save_manager      = self.save_manager,
            report_generator  = self.report_generator,
            patient_id        = patient_id,
            original_frame    = self.current_frame,
            detected_frame    = self.detected_frame,
            snapshots         = self.snapshots,
            result            = self.current_result,
            model_name        = self.model_dropdown.currentText(),
            timestamp         = self.current_session_timestamp,
        )
        self._track_thread(self.save_worker)
        self.save_worker.finished.connect(self._on_save_finished, QUEUED_CONNECTION)
        self.save_worker.error.connect(self._on_save_error, QUEUED_CONNECTION)
        self.save_worker.start()

    def _on_save_finished(self, save_path: str):
        self._set_progress(100, "100%")
        self._update_dot("● Saved ✓", "#22C55E")
        self.status_bar.showMessage(f"💾 Saved: {save_path}")
        self.save_btn.setEnabled(True)
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Saved Successfully!")
        msg_box.setText(f"All patient data saved to Desktop!\n\nFolder Path:\n{save_path}")
        msg_box.setIcon(QMessageBox.Icon.Information if hasattr(QMessageBox, "Icon") else QMessageBox.Information)
        open_btn = msg_box.addButton("📁 Open Folder", QMessageBox.ButtonRole.ActionRole if hasattr(QMessageBox, "ButtonRole") else QMessageBox.ActionRole)
        ok_btn = msg_box.addButton(QMessageBox.StandardButton.Ok if hasattr(QMessageBox, "StandardButton") else QMessageBox.Ok)
        msg_box.setDefaultButton(ok_btn)
        msg_box.exec()
        if msg_box.clickedButton() == open_btn:
            try:
                if sys.platform.startswith("win"):
                    os.startfile(save_path)
                elif sys.platform.startswith("darwin"):
                    import subprocess
                    subprocess.Popen(["open", save_path])
                else:
                    import subprocess
                    subprocess.Popen(["xdg-open", save_path])
            except Exception as e:
                logger.warning(f"Could not open patient folder: {e}")

    def _on_save_error(self, error_msg: str):
        self._set_progress(0, "0%")
        self._update_dot("● Save Error", "#EF4444")
        self.save_btn.setEnabled(True)
        QMessageBox.critical(self, "Save Error", error_msg)

    # ── Helpers ────────────────────────────────────────────
    def _check_patient_id(self, silent: bool = False) -> bool:
        patient_id = self.patient_id_input.text().strip()
        if not patient_id:
            if not silent:
                echo_mode = QLineEdit.EchoMode.Normal if hasattr(QLineEdit, "EchoMode") else QLineEdit.Normal
                text, ok = QInputDialog.getText(
                    self,
                    "Patient ID Required",
                    "Please enter Patient ID (e.g., PT-001):",
                    echo_mode,
                    ""
                )
                if ok and text.strip():
                    patient_id = text.strip()
                    self.patient_id_input.setText(patient_id)
                    return True
                else:
                    QMessageBox.warning(
                        self,
                        "Patient ID Required",
                        "A valid Patient ID is required to start session or save data."
                    )
                    self.patient_id_input.setFocus()
                    return False
            return False
        return True

    def _set_progress(self, value: int, text: str):
        if self.progress_bar  is not None: self.progress_bar.setValue(value)
        if self.progress_text is not None: self.progress_text.setText(text)

    def _update_dot(self, text: str, color: str):
        if self.status_dot is not None:
            self.status_dot.setText(text)
            self.status_dot.setStyleSheet(f"color:{color};font-size:8pt;background:transparent;")

    # ── Resize Event ──────────────────────────────────────────
    def resizeEvent(self, event):
        super().resizeEvent(event)
        h = self.height()
        if hasattr(self, "snapshots_bar") and self.snapshots_bar:
            if h < 500:
                self.snapshots_bar.hide()
            else:
                self.snapshots_bar.show()

        is_feed_active = self.is_camera_active or (self.video_worker and self.video_worker.isRunning() and not self.is_paused)
        if not is_feed_active:
            if getattr(self, "current_frame", None) is not None:
                try:
                    self._display_frame(self.current_frame, self.input_display)
                except Exception as e:
                    logger.debug(f"Error updating input display on resize: {e}")
            if getattr(self, "detected_frame", None) is not None:
                try:
                    self._display_frame(self.detected_frame, self.output_display)
                except Exception as e:
                    logger.debug(f"Error updating output display on resize: {e}")

    # ── Close Event & Temp File Cleanup ───────────────────────
    def closeEvent(self, event):
        logger.info("Closing VisionAI application and releasing resources...")
        if self.is_recording:
            self._stop_recording()
        if self.camera_worker and self.camera_worker.isRunning():
            self.camera_worker.stop()
        if self.video_worker and self.video_worker.isRunning():
            self.video_worker.stop()
        if self.inference_worker and self.inference_worker.isRunning():
            self.inference_worker.stop()
        if self.video_writer and self.video_writer.isRunning():
            self.video_writer.release()
        if self.detected_video_writer and self.detected_video_writer.isRunning():
            self.detected_video_writer.release()
        if self.model_worker and self.model_worker.isRunning():
            self.model_worker.wait(1000)
        if self.loader_thread and self.loader_thread.isRunning():
            self.loader_thread.wait(1000)
        if self._preload_worker and self._preload_worker.isRunning():
            self._preload_worker.wait(1000)
        if self.save_worker and self.save_worker.isRunning():
            self.save_worker.wait(1000)

        for thread in list(self._background_threads):
            if thread and thread.isRunning():
                thread.wait(1000)

        # Temp file cleanup
        self.current_frame = None
        self.detected_frame = None
        self.snapshots.clear()

        logger.info("VisionAI closed cleanly")
        event.accept()
