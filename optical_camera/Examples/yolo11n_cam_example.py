# ============================================================
# bootstrap repo root before other imports
import subprocess, sys, os
from pathlib import Path

def add_git_root_to_path():
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL
        )
        git_root = Path(out.decode("utf-8").strip())
        sys.path.insert(0, str(git_root))
        return git_root
    except Exception:
        raise RuntimeError("Not inside a Git repository")

add_git_root_to_path()
# ============================================================ 


# # =================== 1st ===================
# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# # =================== 1st ===================
from ultralytics import YOLO
import cv2
import config
from picamera2 import Picamera2, Preview


model = YOLO(config.OPTICAL_YOLO_MODEL)
print("finish loading")


# Initialize camera
picam2 = Picamera2()
cam_config = picam2.create_still_configuration(main={"size": (1280, 960)})
picam2.configure(cam_config)
picam2.start()

# Open camera (IMX219 is usually /dev/video0)
# cap = cv2.VideoCapture(config.OPTICAL_CAM_ID)

frame_count = 0
while(True):
    # ret, frame = cap.read()
    frame = picam2.capture_array()

    print(f"frame num {frame_count}")


    results = model(frame, imgsz=config.OPTICAL_YOLO_WH, verbose=False)

        # Save annotated frame every 30 frames
    if frame_count % 30 == 0:
        annotated = results[0].plot()
        cv2.imwrite(f"frame_{frame_count}.jpg", annotated)

    frame_count += 1

picam2.stop()
cv2.destroyAllWindows()

