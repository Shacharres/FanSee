import os
import config
from stabilizer import init_stabilizer, update_buffer, get_stable_boxes
from optical_camera.gesture_detection import init_gesture_recognizer, is_wave_gesture, is_exit_sequence
from optical_camera.capture_frame_cv2 import capture_frame, init_camera
from optical_camera.YOLO_detect_ppl import detect_people
from thermal_camera.adafruit_cam import init_thermal_camera, get_max_temp


def init(d_state: dict = None):
    if d_state is not None and d_state['isInitalized']:
        return d_state
    recognizer, gesture_history = init_gesture_recognizer(os.path.abspath('./optical_camera/gesture_recognizer.task'))
    d_state = {
        'isInitalized': True,
        'gestures_recognizer': recognizer,
        'gesture_history': gesture_history,
        'thermal_camera': init_thermal_camera(config.THERMAL_FRAME_RATE, (config.THERMAL_H, config.THERMAL_W)),
        'history': init_stabilizer(config.STABILIZER_N_FRAMES),
        'picam': None,
        'failed_capture_counter': 0
    }
    init_camera(d_state)
    return d_state
    

def cleanup(d_state):
    if 'cap' in d_state.keys():
        try:
            d_state['cap'].release()
        except Exception as e:
            print(f"Error cleaning up optical camera: {e}")
    try:
        d_state['thermal_camera'].exit()
    except Exception as e:
        print(f"Error cleaning up thermal camera: {e}")
    d_state['isInitalized'] = False
    print("Cleanup successful.")


def main():
    # init HW
    d_state = init()
    # main loop:
    while True:
        # capture image
        frame_bgr, frame_rgb, d_state = capture_frame(d_state)

        # detection + stabilization
        detected_boxes, detected_centers, annotated_frame, d_state = detect_people(frame_bgr, state=d_state, return_annotated=True)
        d_state['history'] = update_buffer(d_state['history'], detected_boxes)
        boxes_to_consider = get_stable_boxes(d_state['history'], detected_boxes, config.STABILIZER_M_FRAMES)

        # for each box, run the blocks that acquire data to build "heat score"
        for box in boxes_to_consider:
            is_wave = is_wave_gesture(d_state['gestures_recognizer'], d_state['gesture_history'], image_matrix=frame_rgb)
            temp = get_max_temp(d_state['thermal_camera'], box, (config.OPTICAL_W, config.OPTICAL_H))
            print(f"Max temp in box {box}: {temp}")


        if is_exit_sequence(d_state['gestures_recognizer'], d_state['gesture_history'], image_matrix=frame_rgb) :  # define your own break condition
            break

        # for res in yolo_res:
        #     box = res.box.xyxy[0].cpu().numpy()  # x1,y1,x2,y2
        #     temp = get_max_temp(thermal_camera, box, (config.OPTICAL_W, config.OPTICAL_H))
        #     conf = res.conf
        #     cls = res.cls
    #   calc metrics
    #   fan control
    
    # cleanup
    cleanup(d_state)


if __name__ == "__main__":
    main()
