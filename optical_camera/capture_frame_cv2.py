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
import config
from picamera2 import Picamera2
import time
import cv2


def capture_frame(d_state, verbose=False, flag_debug_save_image=False):
    """
    Captures a single frame from the PiCamera2.
    Updates d_state:
      - Increments on failure
      - Resets on success
      - Crashes if counter exceeds threshold
    Returns:
      (frame_bgr, d_state)
      - frame_bgr: np.ndarray (BGR, OpenCV style), or None on failure
      - d_state: updated dict
    """
    try:
        picam2 = Picamera2()
        camera_config = picam2.create_still_configuration(
            main={"size": (config.OPTICAL_W, config.OPTICAL_H)}
        )
        picam2.configure(camera_config)
        picam2.start()
        time.sleep(2)

        # Capture frame (RGB by default)
        frame_rgb = picam2.capture_array()
        picam2.close()

    except Exception as e:
        # Handle failure to open or capture
        d_state['failed_capture_counter'] = d_state.get('failed_capture_counter', 0) + 1
        if d_state['failed_capture_counter'] > config.OPTICAL_FAILED_CAPTURE_COUNTER_FOR_CRASH:
            raise RuntimeError(f"Camera capture failed too many times: {e}")
        return None, None, d_state

    # Convert to BGR (YOLO/OpenCV style)
    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

    # Reset failure counter on success
    d_state['failed_capture_counter'] = 0

    if verbose:
        print("Captured frame shape:", frame_bgr.shape)

    if flag_debug_save_image:
        cv2.imwrite("captured_frame.jpg", frame_rgb)
        print("Picture saved as captured_frame.jpg")

    return frame_bgr, frame_rgb, d_state


if __name__ == "__main__":
    _, frame_rgb, _ = capture_frame(d_state={}, verbose=True, flag_debug_save_image=True)
    if frame_rgb is not None:
        print("Frame captured successfully")
    else:
        print("Failed to capture frame")
