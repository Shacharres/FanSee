import os


from optical_camera.gesture_detection import init_gesture_recognizer, is_wave_gesture


gestures_recognizer = None


def init():
    model_path = os.path.abspath('./optical_camera/gesture_recognizer.task')
    gestures_recognizer = init_gesture_recognizer(model_path)


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
