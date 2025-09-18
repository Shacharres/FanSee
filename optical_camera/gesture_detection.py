import urllib
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import cv2
import matplotlib.pyplot as plt


KNOWN_GESTURES_NAMES = ["None", "Closed_Fist", "Open_Palm", "Pointing_Up", "Thumb_Down", "Thumb_Up", "Victory", "ILoveYou"]


def init_gesture_recognizer(model_path: str) -> vision.GestureRecognizer: # type: ignore
    """Initializes the gesture recognizer with the given model path."""
    if not os.path.isfile(model_path):
        raise IOError(f"Model file not found at {model_path}")
   
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.GestureRecognizerOptions(base_options=base_options)
    recognizer = vision.GestureRecognizer.create_from_options(options)
    return recognizer


def get_gesture_prediction(recognizer: vision.GestureRecognizer, image_path: str = None, image_matrix=None) -> tuple[str, float]: # type: ignore
    """Gets gesture prediction for a single image."""
    if image_path is None and image_matrix is None:
        raise ValueError("Either image_path or image_matrix must be provided.")
    if image_matrix is not None:
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_matrix)
    else:
        image = mp.Image.create_from_file(image_path)
    recognition_result = recognizer.recognize(image)
    top_gesture = recognition_result.gestures[0][0]
#   hand_landmarks = recognition_result.hand_landmarks
    return top_gesture.category_name, top_gesture.score


def is_wave_gesture(recognizer: vision.GestureRecognizer, image_path: str = None, image_matrix=None, conf_threshold: float = 0.5) -> bool: # type: ignore
    """Checks if the gesture in the image is a wave gesture."""
    gesture_name, score = get_gesture_prediction(recognizer, image_path, image_matrix)
    return gesture_name == "Open_Palm" and score > conf_threshold


if __name__ == "__main__":
    model_path = os.path.abspath('./optical_camera/gesture_recognizer.task')
   # Create a GestureRecognizer object.
    recognizer = init_gesture_recognizer(model_path)
    IMAGE_FILENAMES = ['thumbs_down.jpg', 'victory.jpg', 'thumbs_up.jpg', 'pointing_up.jpg']

    for name in IMAGE_FILENAMES:
        url = f'https://storage.googleapis.com/mediapipe-tasks/gesture_recognizer/{name}'
        urllib.request.urlretrieve(url, name)
        gesture = get_gesture_prediction(recognizer, image_path=name)
        print(f'Gesture: {gesture[0]}, Score: {gesture[1]:.2f}')
    