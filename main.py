# ============================================================
# VisionAI - Eye Disease Detection System
# SMART - Sanjivani Multidisciplinary AI Research & Technology
# Root Launcher - Delegates to App/main.py
# ============================================================

import os
import sys

# Ensure App directory is in sys.path
app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "App")
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

if __name__ == "__main__":
    from App.main import main
    main()