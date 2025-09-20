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


def detect_people_and_ties(frame, state=None, return_annotated=False):
    """
    Similar to detect_people but also checks for ties.
    If a tie is detected, it prioritizes that detection and ignores other people.
    """
    if state is None:
        state = {}

    tie_detected = False
    results = model(frame, imgsz=config.OPTICAL_YOLO_WH, verbose=False)

    boxes = []
    for det in results[0].boxes:
        cls_id = int(det.cls[0])       # class id
        conf = float(det.conf[0])      # confidence
        if cls_id == config.OPTICAL_YOLO_TIE_ID and conf >= config.OPTICAL_IS_TIE_YOLO_THR:
            tie_detected = True 
            x1, y1, x2, y2 = map(int, det.xyxy[0])
            boxes = [(x1, y1, x2, y2)]  # overrun boxes to only care about the tie
            break  # only care about the first tie detected

        if cls_id == 0 and conf >= config.OPTICAL_IS_PERSON_YOLO_THR:  # class 0 = person
            x1, y1, x2, y2 = map(int, det.xyxy[0])
            boxes.append((x1, y1, x2, y2))

    centers = get_center_pixels(boxes)

    annotated_frame = results[0].plot() if return_annotated else None
    # cv2.imshow("Live View", annotated_frame)
    # cv2.waitKey(1) 
    return boxes, centers, annotated_frame, state, tie_detected


def toothbrush_detected(frame):
    results = model(frame, imgsz=config.OPTICAL_YOLO_WH, verbose=False)

    for det in results[0].boxes:
        cls_id = int(det.cls[0])       # class id
        if cls_id == config.OPTICAL_YOLO_TOOTHBRUSH_ID and conf >= config.OPTICAL_IS_TOOTHBRUSH_YOLO_THR:
            return True
    return False
