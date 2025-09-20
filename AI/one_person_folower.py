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

from picamera2 import Picamera2, Preview
import cv2
from ultralytics import YOLO
import config
from utils import get_center_pixels
from HW_control.fan_control import  set_servo_from_pixel

model = YOLO(config.OPTICAL_YOLO_MODEL)
print("finish loading")
# Initialize camera
picam2 = Picamera2()
cam_config = picam2.create_still_configuration(main={"size": (config.OPTICAL_W, config.OPTICAL_H)})
picam2.configure(cam_config)
picam2.start()

while True:
    # Capture frame
    frame = picam2.capture_array()
    results = model(frame, imgsz=config.OPTICAL_YOLO_WH, verbose=False)
    annotated = results[0].plot()
    # Show live preview
    cv2.imshow("Live View", annotated)
    boxes = []
    for det in results[0].boxes:
        cls_id = int(det.cls[0])       # class id
        conf = float(det.conf[0])      # confidence
        if cls_id == 0 and conf >= config.OPTICAL_IS_PERSON_YOLO_THR:  # class 0 = person
            x1, y1, x2, y2 = map(int, det.xyxy[0])
            # boxes.append((x1, y1, x2, y2))
            box = (x1, y1, x2, y2)
            x_center = x1/2 + x2/2
            wanted_fan = x_center/1280
            wanted_fan*2 -1
            set_servo_from_pixel(x_center)
            # print(x_center)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

picam2.stop()
cv2.destroyAllWindows()
