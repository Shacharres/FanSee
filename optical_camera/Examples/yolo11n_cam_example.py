# =================== 1st ===================
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# =================== 1st ===================
from ultralytics import YOLO
import cv2
import config


model = YOLO(config.OPTICAL_YOLO_MODEL)

# Open camera (IMX219 is usually /dev/video0)
cap = cv2.VideoCapture(config.OPTICAL_CAM_ID)

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, imgsz=config.OPTICAL_YOLO_WH, verbose=False)

    # Save annotated frame every 30 frames
    if frame_count % 30 == 0:
        annotated = results[0].plot()
        cv2.imwrite(f"frame_{frame_count}.jpg", annotated)

    frame_count += 1

cap.release()