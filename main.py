import os


import config
from stabilizer import init_stabilizer, update_buffer, get_stable_cells
from optical_camera.gesture_detection import init_gesture_recognizer, is_wave_gesture
from optical_camera.capture_frame_cv2 import capture_frame
from thermal_camera.adafruit_cam import init_thermal_camera, get_max_temp


gestures_recognizer = None
thermal_camera = None
history = None


def init():
    model_path = os.path.abspath('./optical_camera/gesture_recognizer.task')
    gestures_recognizer = init_gesture_recognizer(model_path)
    thermal_camera = init_thermal_camera(config.THERMAL_FRAME_RATE, (config.THERMAL_H, config.THERMAL_W))
    history = init_stabilizer(config.STABILIZER_N_FRAMES)


def main():
    # init HW
    init()
    # main loop:
    while True:
        break
        # capture image
        frame = capture_frame()
        # detection + tracking
        yolo_res = None
        for res in yolo_res:
            box = res.box.xyxy[0].cpu().numpy()  # x1,y1,x2,y2
            temp = get_max_temp(thermal_camera, box, (config.OPTICAL_W, config.OPTICAL_H))
            conf = res.conf
            cls = res.cls
    #   calc metrics
    #   fan control
    


if __name__ == "__main__":
    main()
