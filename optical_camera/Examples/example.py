import cv2
import time
from picamera2 import Picamera2, MappedArray


def setupCam():
        cam = Picamera2()
        def preview(request):
                with MappedArray(request, "main") as m:
                        pass

        cam.pre_callback = preview
        time.sleep(5)
        cam.start(show_preview=True)
        return cam


def test(cam):
        frame = cam.capture_array()
        height, width, _ = frame.shape
        middle = (int(width / 2), int(height / 2))
        while True:
                frame = cam.capture_array()
                cv2.circle(frame, middle, 10, (255, 0 , 255), -1)
                cv2.imshow('f', frame)


test(setupCam())