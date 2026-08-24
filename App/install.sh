#!/bin/bash
# ============================================================
# VisionAI - Eye Disease Detection System
# SMART - Sanjivani Multidisciplinary AI Research & Technology
# install.sh - Automated Deployment & Desktop Launcher Setup
# ============================================================

if [ -z "$BASH_VERSION" ]; then
    echo "Error: Please run with bash: bash install.sh"
    exit 1
fi

echo "============================================================"
echo "      Installing VisionAI (Raspberry Pi 5 / Linux OS)"
echo "============================================================"

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Application Directory: $APP_DIR"

echo "1. Cleaning up any conflicting global user site-packages..."
rm -rf ~/.local/lib/python3.13/site-packages/torch* ~/.local/lib/python3.13/site-packages/torchvision* 2>/dev/null || true
rm -rf ~/.local/lib/python3.*/site-packages/torch* ~/.local/lib/python3.*/site-packages/torchvision* 2>/dev/null || true

echo "2. Installing system dependencies (requires sudo)..."
sudo apt update
sudo apt install -y \
    python3-pip python3-venv python3-pyqt5 python3-opencv python3-pil \
    python3-tqdm python3-requests python3-dateutil \
    python3-picamera2 libcamera-apps v4l-utils libcamerify \
    libgl1 libopenblas-dev libxcb-cursor0 \
    libqt5widgets5 libqt5gui5 libqt5core5a \
    libglib2.0-0 libatlas-base-dev

echo "3. Configuring Raspberry Pi Camera Module 3 drivers & permissions..."
if command -v raspi-config &> /dev/null; then
    sudo raspi-config nonint do_camera 0 2>/dev/null || true
fi

if [ -f /boot/firmware/config.txt ]; then
    CONFIG_FILE="/boot/firmware/config.txt"
elif [ -f /boot/config.txt ]; then
    CONFIG_FILE="/boot/config.txt"
else
    CONFIG_FILE=""
fi

if [ -n "$CONFIG_FILE" ]; then
    if ! grep -q "^camera_auto_detect=1" "$CONFIG_FILE" 2>/dev/null; then
        echo "camera_auto_detect=1" | sudo tee -a "$CONFIG_FILE" > /dev/null
    fi
    if ! grep -q "^dtoverlay=imx708" "$CONFIG_FILE" 2>/dev/null; then
        echo "dtoverlay=imx708" | sudo tee -a "$CONFIG_FILE" > /dev/null
    fi
fi

# Grant camera and video permissions to current user
CURRENT_USER="$(whoami)"
sudo usermod -a -G video,input "$CURRENT_USER" 2>/dev/null || true

echo "4. Setting up virtual environment..."
python3 -m venv "$APP_DIR/venv" --system-site-packages
source "$APP_DIR/venv/bin/activate"

echo "5. Upgrading build tools inside virtual environment..."
"$APP_DIR/venv/bin/pip" install --upgrade pip setuptools wheel

echo "6. Installing PyTorch, torchvision, and Python package requirements..."
"$APP_DIR/venv/bin/pip" install torch torchvision --index-url https://download.pytorch.org/whl/cpu
"$APP_DIR/venv/bin/pip" install timm loguru reportlab Pillow requests tqdm python-dateutil

# Ensure logo PNG asset exists
if [ ! -f "$APP_DIR/assets/smartlab_logo.png" ] && [ -f "$APP_DIR/assets/smartlab_logo.ico" ]; then
    echo "Generating PNG logo from ICO..."
    "$APP_DIR/venv/bin/python3" -c "
from PIL import Image
try:
    img = Image.open('$APP_DIR/assets/smartlab_logo.ico')
    img.save('$APP_DIR/assets/smartlab_logo.png', 'PNG')
    print('PNG Logo generated.')
except Exception as e:
    print('Logo conversion skipped:', e)
"
fi

echo "7. Writing run_pi.sh launcher wrapper..."
cat << 'EOF' > "$APP_DIR/run_pi.sh"
#!/bin/bash
if [ -d "/home/smartlab/VisionAI" ]; then
    cd /home/smartlab/VisionAI
    DIR="/home/smartlab/VisionAI"
else
    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
    cd "$DIR"
fi

if [ -f "$DIR/venv/bin/python3" ]; then
    PYTHON_BIN="$DIR/venv/bin/python3"
else
    PYTHON_BIN="python3"
fi

export OMP_NUM_THREADS=2
export MKL_NUM_THREADS=2
export OPENBLAS_NUM_THREADS=2
export VECLIB_MAXIMUM_THREADS=2
export NUMEXPR_NUM_THREADS=2

export PYTHONNOUSERSITE=1
export QT_QPA_PLATFORM=xcb

export QT_AUTO_SCREEN_SCALE_FACTOR=0
export QT_ENABLE_HIGHDPI_SCALING=0
export QT_SCALE_FACTOR=1
export QT_FONT_DPI=96

exec "$PYTHON_BIN" main.py "$@"
EOF
chmod +x "$APP_DIR/run_pi.sh"

echo "8. Creating persistent desktop shortcut, autostart config & registering system menu item..."
DESKTOP_DIR="$HOME/Desktop"
MENU_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"
SMARTLAB_AUTOSTART_DIR="/home/smartlab/.config/autostart"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$MENU_DIR"
mkdir -p "$AUTOSTART_DIR"
if [ -d "/home/smartlab" ]; then
    mkdir -p "$SMARTLAB_AUTOSTART_DIR"
fi

TEMP_DESKTOP="/tmp/visionai.desktop"

cat << EOF > "$TEMP_DESKTOP"
[Desktop Entry]
Version=1.0
Type=Application
Name=VisionAI
Comment=Eye Disease Detection System Autostart
Exec=bash "$APP_DIR/run_pi.sh"
Icon=$APP_DIR/assets/smartlab_logo.png
Path=$APP_DIR
Terminal=false
StartupNotify=false
X-GNOME-Autostart-enabled=true
Categories=Utility;Medical;
EOF

DESKTOP_FILE="$DESKTOP_DIR/visionai.desktop"
MENU_FILE="$MENU_DIR/visionai.desktop"
AUTOSTART_FILE="$AUTOSTART_DIR/visionai.desktop"

cp "$TEMP_DESKTOP" "$DESKTOP_FILE"
chmod +x "$DESKTOP_FILE"
cp "$TEMP_DESKTOP" "$MENU_FILE"
chmod +x "$MENU_FILE"
cp "$TEMP_DESKTOP" "$AUTOSTART_FILE"
chmod +x "$AUTOSTART_FILE"

if [ -d "$SMARTLAB_AUTOSTART_DIR" ]; then
    cp "$TEMP_DESKTOP" "$SMARTLAB_AUTOSTART_DIR/visionai.desktop"
    chmod +x "$SMARTLAB_AUTOSTART_DIR/visionai.desktop"
fi

# Clean up temporary installer desktop file
rm -f "$TEMP_DESKTOP"

if command -v gio &> /dev/null; then
    gio set "$DESKTOP_FILE" metadata::trusted true 2>/dev/null || true
    gio set "$MENU_FILE" metadata::trusted true 2>/dev/null || true
    gio set "$AUTOSTART_FILE" metadata::trusted true 2>/dev/null || true
fi

cat << EOF > "$APP_DIR/INSTALL.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Install VisionAI
Comment=Install VisionAI and create desktop shortcut
Exec=bash -c "cd '$APP_DIR' && bash install.sh; read -p 'Press Enter to close...'"
Icon=$APP_DIR/assets/smartlab_logo.png
Path=$APP_DIR
Terminal=true
Categories=Utility;
EOF
chmod +x "$APP_DIR/INSTALL.desktop"

echo "============================================================"
echo "              Installation Complete!"
echo "============================================================"
echo "Desktop Shortcut : $DESKTOP_FILE"
echo "System Menu Entry: $MENU_FILE"
echo "Launcher Wrapper : $APP_DIR/run_pi.sh"
echo ""
echo "To launch VisionAI:"
echo "  - Double-click the VisionAI icon on your desktop, OR"
echo "  - Run: bash run_pi.sh"
echo "============================================================"
