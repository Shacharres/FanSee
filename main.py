import os


from optical_camera.gesture_detection import init_gesture_recognizer, is_wave_gesture
from thermal_camera.adafruit_cam import init_thermal_camera
import config

gestures_recognizer = None
thermal_camera = None


def init():
    model_path = os.path.abspath('./optical_camera/gesture_recognizer.task')
    gestures_recognizer = init_gesture_recognizer(model_path)
    thermal_camera = init_thermal_camera(config.THERMAL_FRAME_RATE, (config.THERMAL_H, config.THERMAL_W))


def main():
    # init HW
    init()
    # main loop:
    while True:
        break
    #   detection + tracking
    #   calc metrics
    #   fan control
    


if __name__ == "__main__":
    main()
