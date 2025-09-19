import mediapipe as mp
import cv2
import numpy as np

def init_distance_detector():
    # Initialize MediaPipe Pose
    mp_pose = mp.solutions.pose
    return mp_pose.Pose(static_image_mode=True)


def detect_distance(pose_detector, rgb_box: np.ndarray):
    """ Returns the mean distance of a person from the camera in the given RGB image box using MediaPipe. """
    results = pose_detector.process(rgb_box)

    if results.pose_world_landmarks:
        lm = results.pose_world_landmarks.landmark
        depth = np.mean([coord.z for coord in lm])
    else:  # No person detected
        depth = -1 
    return depth 


if __name__ == "__main__":
    pose, mp_drawing = init_distance_detector()
    detect_distance(pose, None, r"C:\Users\user\Desktop\Untitled.png")