import urllib
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import cv2
import matplotlib.pyplot as plt


def init_gesture_recognizer(model_path: str) -> vision.GestureRecognizer:
    """Initializes the gesture recognizer with the given model path."""
    if not os.path.isfile(model_path):
        os.system("!wget -q https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task")
        raise SystemExit("Downloaded the model file. Please move it to the correct directory and rerun the script.")
   
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.GestureRecognizerOptions(base_options=base_options)
    recognizer = vision.GestureRecognizer.create_from_options(options)
    return recognizer


def get_gesture_prediction(recognizer: vision.GestureRecognizer, image_path: str = None, image_matrix=None):
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
    return top_gesture


if __name__ == "__main__":
    model_path = './gesture_recognizer.task'
   # Create a GestureRecognizer object.
    recognizer = init_gesture_recognizer(model_path)
    IMAGE_FILENAMES = ['thumbs_down.jpg', 'victory.jpg', 'thumbs_up.jpg', 'pointing_up.jpg']

    for name in IMAGE_FILENAMES:
        url = f'https://storage.googleapis.com/mediapipe-tasks/gesture_recognizer/{name}'
        urllib.request.urlretrieve(url, name)
        gesture = get_gesture_prediction(recognizer, image_path=name)
        print(f'Gesture: {gesture.category_name}, Score: {gesture.score:.2f}')
    