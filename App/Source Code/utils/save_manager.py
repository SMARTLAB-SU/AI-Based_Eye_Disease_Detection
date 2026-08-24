# ============================================================
# VisionAI - Eye Disease Detection System
# SMART - Sanjivani Multidisciplinary AI Research & Technology
# utils/save_manager.py - Save All Results and Files
# ============================================================

import os
import cv2
import json
import shutil
import numpy as np
from datetime import datetime
from loguru import logger


import sys


def get_desktop_dir() -> str:
    """
    Returns the absolute path to the user's actual Desktop directory.
    Handles Windows shell folders (including OneDrive Desktop redirection).
    """
    user_home = os.path.expanduser("~")

    if sys.platform.startswith("win"):
        # 1. Try Windows Registry for redirected Desktop path (e.g. OneDrive\Desktop)
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            )
            desktop_path, _ = winreg.QueryValueEx(key, "Desktop")
            winreg.CloseKey(key)
            desktop_path = os.path.expandvars(desktop_path)
            if os.path.exists(desktop_path):
                return desktop_path
        except Exception as e:
            logger.warning(f"Could not read Desktop from winreg: {e}")

        # 2. Check OneDrive Desktop environment variables or standard locations
        onedrive = os.environ.get("OneDrive") or os.environ.get("OneDriveConsumer")
        if onedrive:
            onedrive_desktop = os.path.join(onedrive, "Desktop")
            if os.path.exists(onedrive_desktop):
                return onedrive_desktop

        user_onedrive_desktop = os.path.join(user_home, "OneDrive", "Desktop")
        if os.path.exists(user_onedrive_desktop):
            return user_onedrive_desktop

    # 3. Standard fallback: ~/Desktop
    desktop = os.path.join(user_home, "Desktop")
    if not os.path.exists(desktop):
        os.makedirs(desktop, exist_ok=True)
    return desktop


import threading
from concurrent.futures import ThreadPoolExecutor

_file_io_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="SaveManagerIO")


def save_image_async(filepath: str, image: np.ndarray, callback=None):
    """Offload cv2.imwrite disk writing to a background thread."""
    def _write_job():
        try:
            if image is not None and image.size > 0:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                cv2.imwrite(filepath, image)
                logger.info(f"Async frame saved to: {filepath}")
                if callback:
                    callback(True, filepath)
        except Exception as exc:
            logger.error(f"Error in save_image_async for {filepath}: {exc}")
            if callback:
                callback(False, str(exc))

    threading.Thread(target=_write_job, daemon=True).start()


def upload_image_async(file_path: str, upload_url: str, headers: dict = None, callback=None):
    """Offload network image uploading to a background thread."""
    def _upload_job():
        try:
            import requests
            if not os.path.exists(file_path):
                logger.warning(f"Upload file not found: {file_path}")
                if callback: callback(False, "File not found")
                return

            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "image/jpeg")}
                response = requests.post(upload_url, files=files, headers=headers, timeout=15)
                if response.status_code in (200, 201):
                    logger.info(f"Image uploaded successfully to {upload_url}")
                    if callback: callback(True, response.text)
                else:
                    logger.warning(f"Upload failed with status {response.status_code}")
                    if callback: callback(False, f"HTTP {response.status_code}")
        except Exception as exc:
            logger.error(f"Error uploading image {file_path}: {exc}")
            if callback: callback(False, str(exc))

    threading.Thread(target=_upload_job, daemon=True).start()


class SaveManager:
    """
    Handles saving all detection results safely and asynchronously.
    Saves everything in a single folder on the user's Desktop:
        VisionAI_Patients/
        └── PatientID/
            ├── original_photo/
            ├── detected_image/
            ├── captured_images/
            ├── original_video/
            ├── detected_video/
            ├── loaded_video/
            ├── loaded_image/
            ├── result_YYYY-MM-DD_HH-MM-SS.json
            ├── report_YYYY-MM-DD_HH-MM-SS.txt
            └── progress.txt
    """

    def __init__(self, base_save_dir: str = None):
        if base_save_dir is None:
            desktop = get_desktop_dir()
            self.base_save_dir = os.path.join(desktop, "VisionAI_Patients")
        else:
            self.base_save_dir = base_save_dir

        try:
            os.makedirs(self.base_save_dir, exist_ok=True)
        except Exception as exc:
            logger.error(f"Could not create base save directory {self.base_save_dir}: {exc}")
        logger.info(f"SaveManager initialised — Desktop base dir: {self.base_save_dir}")

    # ── Get Patient Folder ─────────────────────────────────
    def _get_patient_folder(self, patient_id: str, timestamp: str = None) -> str:
        safe_id = "".join(c for c in patient_id if c.isalnum() or c in "-_")
        if not safe_id:
            safe_id = "patient_unknown"
        path = os.path.join(self.base_save_dir, safe_id)
        for folder in ("original_photo", "detected_image", "captured_images", "original_video", "detected_video", "loaded_video", "loaded_image"):
            try:
                os.makedirs(os.path.join(path, folder), exist_ok=True)
            except Exception as exc:
                logger.error(f"Error creating directory {folder}: {exc}")
        return path

    # ── Main Save Function ─────────────────────────────────
    def save_all(
        self,
        patient_id:     str,
        original_frame: np.ndarray,
        detected_frame: np.ndarray,
        snapshots:      list,
        result:         dict,
        model_name:     str,
        timestamp:      str = None,
    ) -> str:
        """
        Save everything for a patient session safely.
        Returns the path to the patient folder.
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        patient_path = self._get_patient_folder(patient_id)

        if original_frame is not None:
            try:
                filename = f"original_photo_{timestamp}.jpg"
                filepath = os.path.join(patient_path, "original_photo", filename)
                cv2.imwrite(filepath, original_frame)
            except Exception as exc:
                logger.error(f"Failed to save original frame: {exc}")

        if detected_frame is not None:
            try:
                filename = f"detected_image_{timestamp}.jpg"
                filepath = os.path.join(patient_path, "detected_image", filename)
                cv2.imwrite(filepath, detected_frame)
            except Exception as exc:
                logger.error(f"Failed to save detected frame: {exc}")

        if snapshots:
            snapshots_dir = os.path.join(patient_path, "captured_images")
            for i, snap in enumerate(snapshots):
                try:
                    frame = snap.get("frame")
                    disease = snap.get("disease", "Unknown")
                    confidence = snap.get("confidence", 0.0)
                    if frame is not None:
                        filename = f"captured_{timestamp}_{i+1:03d}_{disease}_{confidence:.0f}pct.jpg"
                        filepath = os.path.join(snapshots_dir, filename)
                        cv2.imwrite(filepath, frame)
                except Exception as exc:
                    logger.error(f"Failed to save snapshot #{i+1}: {exc}")

        # Save result JSON in patient folder
        try:
            self._save_result_json(patient_path, patient_id, result, model_name, timestamp)
        except Exception as exc:
            logger.error(f"Failed to save result JSON: {exc}")

        # Update patient progress log
        try:
            self._update_progress_log(patient_path, patient_id, result, model_name, timestamp)
        except Exception as exc:
            logger.error(f"Failed to update progress log: {exc}")

        logger.info(f"All data saved to patient folder: {patient_path}")
        return patient_path

    # ── Get Recordings Path ────────────────────────────────
    def get_recording_path(self, patient_id: str, timestamp: str, is_detected: bool = False) -> str:
        """
        Get full path for a new recording file.
        """
        patient_path = self._get_patient_folder(patient_id)
        folder = "detected_video" if is_detected else "original_video"
        prefix = "detected" if is_detected else "original"
        filename = f"{prefix}_video_{timestamp}.avi"
        return os.path.join(patient_path, folder, filename)

    # ── Save Result JSON ───────────────────────────────────
    def _save_result_json(
        self,
        patient_path: str,
        patient_id:   str,
        result:       dict,
        model_name:   str,
        timestamp:    str,
    ):
        data = {
            "patient_id":  patient_id,
            "date_time":   timestamp,
            "model":       model_name,
            "disease":     result.get("disease",    "Unknown"),
            "confidence":  result.get("confidence", 0.0),
            "timestamp":   result.get("timestamp",  ""),
            "top_results": result.get("results",    []),
        }

        filename = f"result_{timestamp}.json"
        filepath = os.path.join(patient_path, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            logger.info(f"Result JSON saved: {filename}")
        except Exception as exc:
            logger.error(f"Error writing JSON {filename}: {exc}")

    # ── Save Uploaded File ─────────────────────────────────
    def save_uploaded_file(self, src_path: str, patient_id: str, timestamp: str) -> str:
        try:
            if not os.path.exists(src_path):
                logger.warning(f"Source file not found: {src_path}")
                return None
            ext = os.path.splitext(src_path)[1].lower()
            filename = os.path.basename(src_path)
            filename = f"loaded_{timestamp}_{filename}"

            patient_path = self._get_patient_folder(patient_id)
            if ext in (".mp4", ".avi", ".mov"):
                dst_path = os.path.join(patient_path, "loaded_video", filename)
            else:
                dst_path = os.path.join(patient_path, "loaded_image", filename)

            shutil.copy2(src_path, dst_path)
            logger.info(f"Uploaded file saved: {dst_path}")
            return dst_path
        except Exception as exc:
            logger.error(f"Error in save_uploaded_file for {src_path}: {exc}")
            return None

    # ── Update Progress Log ────────────────────────────────
    def _update_progress_log(
        self,
        patient_path: str,
        patient_id:   str,
        result:       dict,
        model_name:   str,
        timestamp:    str,
    ):
        """
        Updates a progress log file (progress.txt) at the root of the patient's folder.
        It keeps track of all visits, dates, diagnoses, and notes progress trends.
        """
        progress_file = os.path.join(patient_path, "progress.txt")
        progress_json_path = os.path.join(patient_path, "progress.json")
        disease = result.get("disease", "Unknown")
        confidence = result.get("confidence", 0.0)

        # Read existing history if available
        history = []
        if os.path.exists(progress_json_path):
            try:
                with open(progress_json_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception as e:
                logger.warning(f"Error reading progress.json: {e}")

        # Determine trend based on previous visits
        trend = "First visit recorded."
        if history:
            last_visit = history[-1]
            last_disease = last_visit.get("disease", "Unknown")
            last_conf = last_visit.get("confidence", 0.0)

            if last_disease == "Normal" and disease != "Normal":
                trend = f"⚠️ REGRESSION: Patient went from Normal to {disease}."
            elif last_disease != "Normal" and disease == "Normal":
                trend = f"🎉 IMPROVEMENT: Patient condition resolved from {last_disease} to Normal."
            elif last_disease != "Normal" and disease != "Normal":
                if last_disease == disease:
                    if confidence > last_conf + 5:
                        trend = f"⚠️ STABLE/SLIGHT PROGRESSION: {disease} detected with higher confidence ({last_conf:.1f}% -> {confidence:.1f}%)."
                    elif confidence < last_conf - 5:
                        trend = f"👍 STABLE/SLIGHT IMPROVEMENT: {disease} detected with lower confidence ({last_conf:.1f}% -> {confidence:.1f}%)."
                    else:
                        trend = f"➡️ STABLE: {disease} detected with similar confidence ({last_conf:.1f}% -> {confidence:.1f}%)."
                else:
                    trend = f"🔄 CHANGE: Patient condition changed from {last_disease} ({last_conf:.1f}%) to {disease} ({confidence:.1f}%)."

        # Append current visit
        current_visit = {
            "timestamp": timestamp,
            "disease": disease,
            "confidence": confidence,
            "model": model_name,
            "trend": trend
        }
        history.append(current_visit)

        # Save progress.json
        try:
            with open(progress_json_path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to write progress.json: {e}")

        # Write/Update human-readable progress.txt
        try:
            with open(progress_file, "w", encoding="utf-8") as f:
                f.write("=" * 65 + "\n")
                f.write(f"           PATIENT VISIT & PROGRESS HISTORY LOG\n")
                f.write(f"  Patient ID: {patient_id}\n")
                f.write(f"  Created: {history[0]['timestamp'].replace('_', ' ').replace('-', ':')}\n")
                f.write(f"  Total Visits: {len(history)}\n")
                f.write("=" * 65 + "\n\n")

                for idx, visit in enumerate(history):
                    v_time = visit['timestamp'].replace('_', ' ').replace('-', ':')
                    f.write(f"VISIT #{idx+1} - {v_time}\n")
                    f.write(f"  Model Used : {visit['model']}\n")
                    f.write(f"  Diagnosis  : {visit['disease']} ({visit['confidence']:.2f}%)\n")
                    f.write(f"  Trend/Status: {visit['trend']}\n")
                    f.write("-" * 65 + "\n")
        except Exception as e:
            logger.error(f"Failed to write progress.txt: {e}")

    def get_base_dir(self) -> str:
        return self.base_save_dir