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



def init_camera(d_state: dict = None):
    """
    Initialize PiCamera2 with retries until max failure threshold is reached.
    Updates d_state:
      - Stores 'picam' object on success
      - Increments failed_capture_counter on failure
      - Raises RuntimeError if threshold exceeded
    """
    if d_state is None:
        d_state = {}

    picam2 = None
    while picam2 is None and d_state.get('failed_capture_counter', 0) < config.OPTICAL_FAILED_CAPTURE_COUNTER_FOR_CRASH:
        try:
            picam2 = Picamera2()
            camera_config = picam2.create_still_configuration(
                main={"size": (config.OPTICAL_W, config.OPTICAL_H)}
            )
            picam2.configure(camera_config)
            picam2.start()
            time.sleep(config.OPTICAL_INIT_CAM_WARMUP)  # allow camera to warm up

        except Exception as e:
            d_state['failed_capture_counter'] = d_state.get('failed_capture_counter', 0) + 1
            if d_state['failed_capture_counter'] >= config.OPTICAL_FAILED_CAPTURE_COUNTER_FOR_CRASH:
                raise RuntimeError(f"Camera init failed too many times: {e}")

    d_state['picam'] = picam2
    return d_state


def capture_frame(d_state, verbose=False, flag_debug_save_image=False):
    """
    Captures a frame with retries until max failure threshold is reached.
    Updates d_state:
      - Increments failed_capture_counter on failure
      - Resets failed_capture_counter on success
      - Raises RuntimeError if threshold exceeded
    Returns:
      (frame_bgr, frame_rgb, d_state)
    """
    frame_bgr, frame_rgb = None, None

    while frame_bgr is None and d_state['failed_capture_counter'] < config.OPTICAL_FAILED_CAPTURE_COUNTER_FOR_CRASH:
        try:
            frame_bgr = d_state['picam'].capture_array()
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

            # reset failure counter on success
            d_state['failed_capture_counter'] = 0

        except Exception as e:
            d_state['failed_capture_counter'] += 1
            if d_state['failed_capture_counter'] >= config.OPTICAL_FAILED_CAPTURE_COUNTER_FOR_CRASH:
                raise RuntimeError(f"Camera capture failed too many times: {e}")

    if verbose and frame_bgr is not None:
        print("Captured frame shape:", frame_bgr.shape)

    if flag_debug_save_image and frame_rgb is not None:
        cv2.imwrite("captured_frame.jpg", frame_rgb)
        print("Picture saved as captured_frame.jpg")

    return frame_bgr, frame_rgb, d_state


if __name__ == "__main__":
    _, frame_rgb, _ = capture_frame(d_state={}, verbose=True, flag_debug_save_image=True)
    if frame_rgb is not None:
        print("Frame captured successfully")
    else:
        print("Failed to capture frame")
