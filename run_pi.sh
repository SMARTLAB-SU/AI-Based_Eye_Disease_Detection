#!/bin/bash
# ============================================================
# VisionAI - Eye Disease Detection System
# SMART - Sanjivani Multidisciplinary AI Research & Technology
# run_pi.sh - Native Bash Launcher Wrapper
# ============================================================

# Target directory setup (/home/smartlab/VisionAI with dynamic fallback)
if [ -d "/home/smartlab/VisionAI" ]; then
    cd /home/smartlab/VisionAI
    DIR="/home/smartlab/VisionAI"
else
    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
    cd "$DIR"
fi

# Select Python binary (virtual environment if available, else system python3)
if [ -f "$DIR/venv/bin/python3" ]; then
    PYTHON_BIN="$DIR/venv/bin/python3"
else
    PYTHON_BIN="python3"
fi

# Limit CPU threads to prevent current spikes and shutdowns on Raspberry Pi 5
export OMP_NUM_THREADS=2
export MKL_NUM_THREADS=2
export OPENBLAS_NUM_THREADS=2
export VECLIB_MAXIMUM_THREADS=2
export NUMEXPR_NUM_THREADS=2

# Ignore global broken user site-packages to prevent libtorch_cpu undefined symbol errors
export PYTHONNOUSERSITE=1

# Force X11/XCB platform integration to prevent Wayland-related GUI thread abort crashes
export QT_QPA_PLATFORM=xcb

# Fix high-DPI scaling and oversized UI/dropdown layout issues by forcing exact 1:1 scale metrics
export QT_AUTO_SCREEN_SCALE_FACTOR=0
export QT_ENABLE_HIGHDPI_SCALING=0
export QT_SCALE_FACTOR=1
export QT_FONT_DPI=96

# Launch application using native Python (Picamera2 compatibility)
exec "$PYTHON_BIN" main.py "$@"
