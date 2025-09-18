from picamera2 import Picamera2
import time
import cv2 

def take_image(verbose=False, flag_debug_save_image=False):
    # Init & Start the camera
    picam2 = Picamera2()
    picam2.start()
    time.sleep(2)

    # Capture directly into a NumPy array (BGR, OpenCV style)
    frame = picam2.capture_array()

    if verbose:
        print("Captured frame shape:", frame.shape)

    if flag_debug_save_image:
        cv2.imwrite("image.jpg", frame)   
        print("Picture saved as image.jpg")

    return frame







