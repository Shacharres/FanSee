# =================== 1st ===================
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# =================== 1st ===================
from ultralytics import YOLO
from utils import get_center_pixels
import cv2
import config

# Load YOLO model once
model = YOLO(config.OPTICAL_YOLO_MODEL)

def detect_people(frame, state=None, return_annotated=False):
    """
    Detect people in a single frame using YOLO, with optional state tracking.

    Args:
        frame (np.ndarray): Input image (BGR)
        state (dict, optional): Dictionary to store/maintain state across frames
        return_annotated (bool): If True, also return annotated frame
    
    Returns:
        boxes (list of tuple): List of bounding boxes (x1, y1, x2, y2) for each detected person
        centers (list of tuple): List of center pixels (x, y) for each detected person
        annotated_frame (np.ndarray, optional): Annotated image with bounding boxes (if requested)
        state (dict): Updated state dictionary
    """
    if state is None:
        state = {}

    results = model(frame, imgsz=config.OPTICAL_YOLO_WH, verbose=False)

    boxes = []
    for det in results[0].boxes:
        cls_id = int(det.cls[0])       # class id
        conf = float(det.conf[0])      # confidence
        if cls_id == 0 and conf >= config.OPTICAL_IS_PERSON_YOLO_THR:  # class 0 = person
            x1, y1, x2, y2 = map(int, det.xyxy[0])
            boxes.append((x1, y1, x2, y2))

    centers = get_center_pixels(boxes)

    annotated_frame = results[0].plot() if return_annotated else None

    return boxes, centers, annotated_frame, state
