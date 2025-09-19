# =================== 1st ===================
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# =================== 1st ===================
import cv2
import config

def capture_frame():
    """
    Captures a single frame from the camera and returns it.
    """
    cap = cv2.VideoCapture(config.OPTICAL_CAM_ID)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera ID {config.OPTICAL_CAM_ID}")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise RuntimeError("Failed to capture frame from camera")

    return frame
