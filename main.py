import os
import config
from stabilizer import init_stabilizer, update_buffer, get_stable_boxes
from optical_camera.gesture_detection import init_gesture_recognizer, is_wave_gesture, is_exit_sequence
from optical_camera.capture_frame_cv2 import capture_frame, init_camera
from optical_camera.YOLO_detect_ppl import detect_people
from thermal_camera.adafruit_cam import init_thermal_camera, get_max_temp
from AI.brainless import init_brain_state, propagate_priority
from HW_control.fan_control import set_fan_speed, set_servo_angle, Speed


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
    d_state = init_brain_state(config, d_state=d_state)
    return d_state
    

def cleanup(d_state):
    # optical camera
    if 'picam' in d_state.keys():
        try:
            d_state['picam'].close()
        except Exception as e:
            print(f"Error cleaning up optical camera: {e}")
    # thermal camera
    try:
        d_state['thermal_camera'].exit()
    except Exception as e:
        print(f"Error cleaning up thermal camera: {e}")
    # fan
    set_fan_speed(Speed.OFF)

    d_state['isInitalized'] = False
    print("Cleanup successful.")


def main():
    # init HW
    d_state = init()
    # main loop:
    while True:
        try:
            # capture image
            frame_bgr, frame_rgb, d_state = capture_frame(d_state)

            # detection + stabilization
            detected_boxes, detected_centers, annotated_frame, d_state = detect_people(frame_bgr, state=d_state, return_annotated=True)
            d_state['history'] = update_buffer(d_state['history'], detected_boxes)
            boxes_to_consider, centers_to_consider = get_stable_boxes(d_state['history'], detected_boxes, config.STABILIZER_M_FRAMES)

            # for each box, run the blocks that acquire data to build "heat score"
            is_wave_list = []
            max_temp_list = []
            for box in boxes_to_consider:
                x1, y1, x2, y2 = box
                # crop frame for gesture recognition
                framed_frame = frame_rgb[y1:y2, x1:x2]
                is_wave = is_wave_gesture(d_state['gestures_recognizer'], d_state['gesture_history'], image_matrix=framed_frame)
                max_temp = get_max_temp(d_state['thermal_camera'], box, (config.OPTICAL_W, config.OPTICAL_H))
                is_wave_list.append(is_wave)
                max_temp_list.append(max_temp)
            
            d_targets = {
                'boxes': boxes_to_consider,
                'centers': centers_to_consider,
                'is_wave': is_wave_list,
                'max_temp': max_temp_list
            }

            if is_exit_sequence(d_state['gestures_recognizer'], d_state['gesture_history'], image_matrix=frame_rgb) :  # define your own break condition
                # TODO: ADD here graceful shutdown of HW   ---- not needed - handled in cleanup()
                print("Exit sequence detected. Exiting...")
                break

            # decide if there was a change in the scene, if not - continue to next iteration
            # change: num boxes changed, top of queue lost score
            # update priority queue 
            # call controller


        except Exception as e:
            print(f"Error occurred: {e}")

        finally:
            # cleanup and HW studown
            cleanup(d_state)
    


if __name__ == "__main__":
    main()
