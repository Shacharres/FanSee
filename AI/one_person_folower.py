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
from HW_control.fan_control import  set_servo_from_pixel, set_fan_speed, Speed
import numpy as np


def is_fansee(boxes):
    # the tie ID is 27
    config.OPTICAL_YOLO_TIE_ID
    cls_id_arr = np.array([int(box.cls[0]) for box in boxes])
    cls_conf_arr = np.array([float(box.conf[0]) for box in boxes])
    if config.OPTICAL_YOLO_TIE_ID in cls_id_arr:
        tie_box = boxes[cls_id_arr == config.OPTICAL_YOLO_TIE_ID]
        if float(tie_box.conf[0] > config.OPTICAL_IS_TIE_YOLO_THR):
            # print(f"found tie at tie_conf: {tie_box.conf[0]}")
            tie_loc_x1, tie_loc_y1, tie_loc_x2, tie_loc_y2 = map(int, tie_box.xyxy[0])
            x1, y1, x2, y2 = box
            print(f"tie loc: {tie_box.xyxy[0]}")
            for box in boxes:
                if int(box.cls[0])  == 0:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    if x1<tie_loc_x1 and y1 < tie_loc_y1 and x2>tie_loc_x2 and y2>tie_loc_y2:
                        x_center = x1//2 + x2//2
                        tie_center = tie_loc_x1//2 + tie_loc_x2//2
                        set_servo_from_pixel(tie_center)

model = YOLO(config.OPTICAL_YOLO_MODEL)
print("finish loading")
# Initialize camera
picam2 = Picamera2()
cam_config = picam2.create_still_configuration(main={"size": (config.OPTICAL_W, config.OPTICAL_H)})
picam2.configure(cam_config)
picam2.start()
set_fan_speed(Speed.LOW)
set_servo_from_pixel(config.OPTICAL_W//2)


while True:
    # Capture frame
    frame_bgr = picam2.capture_array()
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    results = model(frame_bgr, imgsz=config.OPTICAL_YOLO_WH, verbose=False)
    annotated = results[0].plot()
    # Show live preview
    cv2.imshow("Live View", annotated)
    # boxes = []
    # cls_id_arr = np.array([int(det.cls[0]) for det in results[0].boxes])
    # cls_conf_arr = np.array([float(det.conf[0]) for det in results[0].boxes])
    # if np.any(np.logical_and(cls_id_arr==0,cls_conf_arr>config.OPTICAL_IS_PERSON_YOLO_THR)):
    #     print("person found")
    #     if np.any(np.cls_id_arr == config.OPTICAL_YOLO_TIE_ID):
    #         print("fansee person")
    is_fansee(results[0].boxes)
    # for det in results[0].boxes:
    #     cls_id = int(det.cls[0])       # class id
    #     conf = float(det.conf[0])      # confidence
    #     if cls_id == 0 and conf >= config.OPTICAL_IS_PERSON_YOLO_THR:  # class 0 = person
    #         x1, y1, x2, y2 = map(int, det.xyxy[0])
    #         # boxes.append((x1, y1, x2, y2))
    #         x_center = x1/2 + x2/2
    #         wanted_fan = x_center/1280
    #         wanted_fan*2 -1
    #         # set_servo_from_pixel(x_center)
    #         # print(x_center)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

picam2.stop()
cv2.destroyAllWindows()




