# =================== 1st ===================
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# =================== 1st ===================
import cv2
import config

def capture_frame(d_state):
    """
    Captures a single frame from the camera and returns it.
    Updates d_state
      - Increments on failure.
      - Resets on success.
      - Crashes if counter exceeds threshold.
    """
    cap = cv2.VideoCapture(config.OPTICAL_CAM_ID)
    if not cap.isOpened():
        d_state['failed_capture_counter'] = d_state.get('failed_capture_counter', 0) + 1
        if d_state['failed_capture_counter'] > config.OPTICAL_FAILED_CAPTURE_COUNTER_FOR_CRASH:
            raise RuntimeError(f"Camera unavailable (ID {config.OPTICAL_CAM_ID}), crash triggered")
        return None, d_state  # return None to indicate failure

    ret, frame = cap.read()
    cap.release()

    if not ret:
        d_state['failed_capture_counter'] = d_state.get('failed_capture_counter', 0) + 1
        if d_state['failed_capture_counter'] > config.OPTICAL_FAILED_CAPTURE_COUNTER_FOR_CRASH:
            raise RuntimeError("Failed to capture frame, crash triggered")
        return None, d_state

    d_state['failed_capture_counter'] = 0
    return frame, d_state
