import os
import config
import traceback
import pygame


from stabilizer import init_stabilizer, update_buffer, get_stable_boxes
from optical_camera.gesture_detection import init_gesture_recognizer, is_wave_gesture, is_exit_sequence, gesture_to_change_fan_speed
from optical_camera.capture_frame_cv2 import capture_frame, init_camera
from optical_camera.YOLO_detect_ppl import detect_people_and_ties, toothbrush_detected
from optical_camera.detect_distance import init_distance_detector, detect_distance
from thermal_camera.adafruit_cam import init_thermal_camera, get_max_temp
from AI.brainless import get_implement_commands, init_brain_state, propagate_priority, switch_target
from HW_control.fan_control import set_fan_speed, Speed, set_mist, set_servo_from_pixel


def init(d_state: dict = None):
    if d_state is not None and d_state['isInitalized']:
        return d_state
    recognizer, gesture_history = init_gesture_recognizer(os.path.abspath('./optical_camera/gesture_recognizer.task'))
    d_state = {
        'isInitalized': True,
        'gestures_recognizer': recognizer,
        'gesture_history': gesture_history,
        'distance_detector': init_distance_detector(),
        'thermal_camera': init_thermal_camera(config.THERMAL_FRAME_RATE, (config.THERMAL_H, config.THERMAL_W)),
        'history': init_stabilizer(config.STABILIZER_N_FRAMES),
        'picam': None,
        'failed_capture_counter': 0,
        'loop_counter': 0
    }
    init_camera(d_state)
    pygame.mixer.init()
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
    set_fan_speed(Speed.STOP)

    d_state['isInitalized'] = False
    print("Cleanup successful.")


def premium_flow_single_iteration(d_state, tie_box, frame_rgb):
    tie_loc_x1, tie_loc_y1, tie_loc_x2, tie_loc_y2 = tie_box
    tie_center = tie_loc_x1//2 + tie_loc_x2//2
    # x1, y1, x2, y2 = (  max(0, tie_loc_x1-350), 
    #                     max(0, tie_loc_y1-350), 
    #                     min(config.OPTICAL_W, tie_loc_x2+350), 
    #                     min(config.OPTICAL_H, tie_loc_y2+350))
    # detect gesture for changing fan speed
    # speed_change_instruction, speed_change_value = gesture_to_change_fan_speed(d_state['gestures_recognizer'], d_state['gesture_history'], image_matrix=frame_rgb[y1:y2, x1:x2])

    tie_box_area = (tie_loc_x2 - tie_loc_x1) * (tie_loc_y2 - tie_loc_y1)
    print(f"Tie box area: {tie_box_area}")

    config.TIE_AREA_THRESHOLD_LOW_VEL = 90918
    config.TIE_AREA_THRESHOLD_MED_VEL = 70918
    config.TIE_AREA_THRESHOLD_HIGH_VEL = 40918

    if tie_box_area >= config.TIE_AREA_THRESHOLD_LOW_VEL:
        desired_speed = Speed.LOW
    elif tie_box_area < config.TIE_AREA_THRESHOLD_HIGH_VEL:
        desired_speed = Speed.HIGH
    else:
        desired_speed = Speed.MIDDLE

    # if tie_box_area < config.TIE_AREA_THRESHOLD_LOW_VEL:
    #     speed_change_instruction, speed_change_value = "decrease_speed", -1
    # elif tie_box_area > config.TIE_AREA_THRESHOLD_LOW:
    #     speed_change_instruction, speed_change_value = "increase_speed", 1
    # else:
    #     speed_change_instruction, speed_change_value = "no_change", 0

    # move fan and change speed
    set_servo_from_pixel(tie_center)
    d_state = set_fan_speed(desired_speed, None, d_state)

    return d_state


def reg_flow_single_iteration(d_state, detected_boxes, frame_rgb):
    boxes_to_consider, centers_to_consider = get_stable_boxes(d_state['history'], detected_boxes, config.STABILIZER_M_FRAMES)

    # (3) for each box, run the blocks that acquire data to build "heat score"
    is_wave_list, max_temp_list, depth_list = [], [], []

    for box in boxes_to_consider:
        x1, y1, x2, y2 = box
        # crop frame for gesture recognition
        framed_frame = frame_rgb[y1:y2, x1:x2]
        is_wave = is_wave_gesture(d_state['gestures_recognizer'], d_state['gesture_history'], image_matrix=framed_frame)
        depth = detect_distance(d_state['distance_detector'], framed_frame)
        max_temp = get_max_temp(d_state['thermal_camera'], box, (config.OPTICAL_W, config.OPTICAL_H))
        
        depth_list.append(depth)
        is_wave_list.append(is_wave)
        max_temp_list.append(max_temp)
    
    d_targets = {
        'boxes': boxes_to_consider,
        'centers': centers_to_consider,
        'is_wave': is_wave_list,
        'max_temp': max_temp_list,
        'depth': depth_list
    }

    # depth - controls fan speed, add boundaries
    # choose box based on heat + gesture
    # if no box, servo to mid, fan off
    # move servo to center of chosen box, set fan speed based on max temp

    return d_state


def main():
    # init HW
    d_state = init()
    # main loop:
    while True:
        try:
            d_state['loop_counter'] += 1
            # (1) capture image
            frame_bgr, frame_rgb, d_state = capture_frame(d_state)

            # (2) detection + stabilization of ppl 
            detected_boxes, detected_centers, annotated_frame, d_state, tie_detected = detect_people_and_ties(frame_bgr, state=d_state, return_annotated=True)
            
            d_state['history'] = update_buffer(d_state['history'], detected_boxes)

            if tie_detected:
                print("Tie detected, switching to premium flow")
                d_state = premium_flow_single_iteration(d_state, detected_boxes[0], frame_rgb)
            else:
                d_state = reg_flow_single_iteration(d_state, detected_boxes, frame_rgb)

            if toothbrush_detected(frame_bgr):
                print("toothbrush detected, setting mist on")
                set_mist(True)
            else:
                set_mist(False)

            # (4) AI brain to decide commands
            if is_exit_sequence(d_state['gestures_recognizer'], d_state['gesture_history'], image_matrix=frame_rgb) :  # define your own break condition
                print("Exit sequence detected. Exiting...")
                break


        except Exception as e:
            print(f"Error occurred: {e}; {traceback.format_exc()}")
            break

    # cleanup and HW studown
    cleanup(d_state)
    


if __name__ == "__main__":
    main()
