from ultralytics import YOLO
import cv2

# Load model (nano version)
model = YOLO("yolo11n.pt")

# Open camera (IMX219 is usually /dev/video0)
cap = cv2.VideoCapture(0)

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, imgsz=320, verbose=False)

    # Save annotated frame every 30 frames
    if frame_count % 30 == 0:
        annotated = results[0].plot()
        cv2.imwrite(f"frame_{frame_count}.jpg", annotated)

    frame_count += 1

cap.release()