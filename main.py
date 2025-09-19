import os


import config
from stabilizer import init_stabilizer, update_buffer, get_stable_boxes
from optical_camera.gesture_detection import init_gesture_recognizer, is_wave_gesture
from optical_camera.capture_frame_cv2 import capture_frame
from thermal_camera.adafruit_cam import init_thermal_camera, get_max_temp


gestures_recognizer = None
thermal_camera = None
history = None
dState = dict()


def init():
    model_path = os.path.abspath('./optical_camera/gesture_recognizer.task')
    gestures_recognizer = init_gesture_recognizer(model_path)
    thermal_camera = init_thermal_camera(config.THERMAL_FRAME_RATE, (config.THERMAL_H, config.THERMAL_W))
    history = init_stabilizer(config.STABILIZER_N_FRAMES)
    dState['isInitalized'] = True

    return dState
    


def main():
    # init HW
    dState = init()
    # main loop:
    while True:
        # capture image
        frame = capture_frame_cv2()

        # detection + tracking
        detected_boxes, detected_centers, annotated_frame, dState = detect_people(frame, state=dState, return_annotated=True)
        yolo_res = None
        detected_boxes = [r.box.xyxy[0].cpu().numpy() for r in yolo_res if r.cls == 0 and r.conf > config.OPTICAL_IS_PERSON_YOLO_THR]  # only persons
        history = update_buffer(history, detected_boxes)
        boxes_to_consider = get_stable_boxes(history, detected_boxes, config.STABILIZER_M_FRAMES)
        
        # for res in yolo_res:
        #     box = res.box.xyxy[0].cpu().numpy()  # x1,y1,x2,y2
        #     temp = get_max_temp(thermal_camera, box, (config.OPTICAL_W, config.OPTICAL_H))
        #     conf = res.conf
        #     cls = res.cls
    #   calc metrics
    #   fan control
    


if __name__ == "__main__":
    main()
