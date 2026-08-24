# ============================================================
# VisionAI - Eye Disease Detection System
# SMART - Sanjivani Multidisciplinary AI Research & Technology
# utils/camera_capture.py - Unified Camera Interface (Pi & Laptops)
# ============================================================

import glob
import os
import sys
import cv2
from loguru import logger


def is_raspberry_pi() -> bool:
    """Check if running on a Raspberry Pi device."""
    try:
        if os.path.exists("/proc/device-tree/model"):
            with open("/proc/device-tree/model", "r") as f:
                return "raspberry pi" in f.read().lower()
    except Exception:
        pass
    return False


class CameraCapture:
    """
    Unified, thermal-safe camera interface for Raspberry Pi Camera Module 3,
    V4L2 USB webcams, and Laptop built-in cameras (Windows/Linux/macOS).
    """

    BACKEND_PICAMERA2 = "picamera2"
    BACKEND_V4L2 = "v4l2"
    BACKEND_OPENCV = "opencv"

    def __init__(self, width: int = 640, height: int = 480, fps: int = 15):
        self.width = width
        self.height = height
        self.fps = fps
        self._backend = None
        self._cap = None
        self._picam2 = None

    @property
    def picam2(self):
        """Property accessor for Picamera2 instance."""
        return self._picam2

    def open(self) -> bool:
        """Attempt to open camera using available hardware backends."""
        try:
            if is_raspberry_pi():
                if self._try_picamera2():
                    return True
                logger.warning("Picamera2 backend unavailable. Falling back to V4L2 OpenCV capture driver.")
                if self._try_v4l2_devices():
                    return True
            return self._try_opencv_indices()
        except Exception as exc:
            logger.error(f"Error in CameraCapture.open: {exc}")
            self.release()
            return False

    def _try_picamera2(self) -> bool:
        """Try initializing Picamera2 as primary backend on Raspberry Pi."""
        picam2 = None
        try:
            import picamera2
            import time

            picam2 = picamera2.Picamera2()

            # Force preview config with 640x480 resolution
            config = None
            try:
                config = picam2.create_preview_configuration(
                    main={"size": (self.width, self.height), "format": "RGB888"}
                )
            except Exception as e:
                logger.warning(f"Picamera2 RGB888 preview config failed: {e}")
                try:
                    config = picam2.create_preview_configuration(
                        main={"size": (self.width, self.height)}
                    )
                except Exception as e2:
                    logger.warning(f"Picamera2 sized preview config failed: {e2}")
                    config = picam2.create_preview_configuration()

            picam2.configure(config)
            picam2.start()
            time.sleep(0.1)

            frame = picam2.capture_array()
            if frame is not None and frame.size > 0:
                self._picam2 = picam2
                self._backend = self.BACKEND_PICAMERA2
                logger.info("Camera opened via Picamera2 (640x480 @ 15 FPS target)")
                return True

        except Exception as exc:
            logger.warning(f"Picamera2 backend initialization failed: {exc}")
        finally:
            # Until ownership is transferred to self, this local instance must be
            # closed even after a failed configuration/start.  Otherwise libcamera
            # can retain the Pi camera and make the next start attempt fail.
            if self._picam2 is None and picam2 is not None:
                try:
                    picam2.stop()
                except Exception:
                    pass
                try:
                    picam2.close()
                except Exception:
                    pass
        return False

    def _try_v4l2_devices(self) -> bool:
        for device_path in sorted(glob.glob("/dev/video*")):
            cap = None
            try:
                cap = cv2.VideoCapture(device_path, cv2.CAP_V4L2)
                if not cap.isOpened():
                    cap.release()
                    continue

                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 15)
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    self._cap = cap
                    self._backend = self.BACKEND_V4L2
                    logger.info(f"Camera opened via V4L2 driver: {device_path} (640x480, 15 FPS)")
                    return True

                cap.release()
            except Exception as exc:
                if cap is not None:
                    try:
                        cap.release()
                    except Exception:
                        pass
                logger.warning(f"V4L2 open failed for {device_path}: {exc}")
        return False

    def _try_opencv_indices(self) -> bool:
        import time

        if sys.platform.startswith("win"):
            backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, None]
        elif sys.platform.startswith("linux"):
            backends = [cv2.CAP_V4L2]
        else:
            backends = [None]

        for index in [0, 1, 2, 3]:
            for backend in backends:
                cap = None
                try:
                    if backend is not None:
                        cap = cv2.VideoCapture(index, backend)
                    else:
                        cap = cv2.VideoCapture(index, cv2.CAP_V4L2 if sys.platform.startswith("linux") else cv2.CAP_ANY)

                    if cap is None or not cap.isOpened():
                        if cap is not None:
                            try:
                                cap.release()
                            except Exception:
                                pass
                        time.sleep(0.05)
                        continue

                    # Force 640x480 resolution & cap frame rate to 15 FPS
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_FPS, 15)

                    time.sleep(0.1)

                    for _ in range(3):
                        ret, frame = cap.read()
                        if ret and frame is not None and frame.size > 0:
                            self._cap = cap
                            self._backend = self.BACKEND_OPENCV
                            logger.info(
                                f"Camera opened via OpenCV index {index} "
                                f"(backend={backend}, 640x480, 15 FPS)"
                            )
                            return True
                        time.sleep(0.05)

                    try:
                        cap.release()
                    except Exception:
                        pass
                    time.sleep(0.05)
                except Exception as exc:
                    if cap is not None:
                        try:
                            cap.release()
                        except Exception:
                            pass
                    time.sleep(0.05)
                    logger.warning(
                        f"OpenCV camera index {index} backend {backend} failed: {exc}"
                    )
        return False

    def read(self):
        """Read frame safely, returning (ret, frame) or (False, None)."""
        try:
            if self._backend == self.BACKEND_PICAMERA2 and self._picam2 is not None:
                try:
                    frame = self._picam2.capture_array()
                    if frame is not None and frame.size > 0:
                        bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        return True, bgr_frame
                except Exception as exc:
                    logger.warning(f"Picamera2 capture_array read failed: {exc}")
                return False, None

            if self._cap is not None and self._cap.isOpened():
                try:
                    ret, frame = self._cap.read()
                    if ret and frame is not None and frame.size > 0:
                        return True, frame
                except Exception as exc:
                    logger.warning(f"OpenCV capture read failed: {exc}")
        except Exception as exc:
            logger.error(f"Unexpected error in CameraCapture.read: {exc}")

        return False, None

    def reconnect(self) -> bool:
        """Safely release and attempt to reopen the camera."""
        try:
            self.release()
            return self.open()
        except Exception as exc:
            logger.error(f"Error in CameraCapture.reconnect: {exc}")
            return False

    def release(self) -> None:
        """Release driver resources and reset backends cleanly."""
        if self._picam2 is not None:
            try:
                self._picam2.stop()
            except Exception:
                pass
            try:
                self._picam2.close()
            except Exception:
                pass
            self._picam2 = None

        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None

        self._backend = None

    def close(self) -> None:
        """Close driver resources cleanly (alias for release)."""
        self.release()

    @property
    def is_open(self) -> bool:
        try:
            if self._backend == self.BACKEND_PICAMERA2:
                return self._picam2 is not None
            return self._cap is not None and self._cap.isOpened()
        except Exception:
            return False

