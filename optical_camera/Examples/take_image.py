# ============================================================
# bootstrap repo root before other imports
import subprocess, sys
from pathlib import Path
import sys
import os
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
#============================================================
import config
from picamera2 import Picamera2
import time
import cv2 

def take_image(verbose=False, flag_debug_save_image=False):
    # Init & Start the camera
    picam2 = Picamera2()
    camera_config = picam2.create_still_configuration(main={"size": (config.OPTICAL_W, config.OPTICAL_H)})
    picam2.configure(camera_config)
    picam2.start()
    time.sleep(2)

    # Capture directly into a NumPy array (BGR, OpenCV style)
    frame = picam2.capture_array()

    if verbose:
        print("Captured frame shape:", frame.shape)

    if flag_debug_save_image:
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite("image.jpg", frame_bgr)   # save the converted frame
        print("Picture saved as image.jpg")

    return frame



if __name__ == "__main__":
    take_image(verbose=False, flag_debug_save_image=True)



