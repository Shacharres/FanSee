from picamera2 import Picamera2, Preview
import cv2

# Initialize camera
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (1280, 960)})
picam2.configure(config)
picam2.start()

while True:
    # Capture frame
    frame = picam2.capture_array()

    # Show live preview
    cv2.imshow("Live View", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

picam2.stop()
cv2.destroyAllWindows()
