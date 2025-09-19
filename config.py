"""
Pins configuration file.
Thresholds and other constants.
"""

# ================================================
# Fan and fan servo 
# ================================================
FAN_SPEED_1_PIN = 1
FAN_SPEED_2_PIN = 2
FAN_SPEED_3_PIN = 3
FAN_MIST_PIN = 4
FAN_SERVO_PIN = 17

# ================================================
# Camera Thermal
# ================================================
# PH
# I2C address
# image size
THERMAL_H = 24
THERMAL_W = 32
# frame rate
THERMAL_FRAME_RATE = 4
# lowermost temp to consider
THERMAL_MIN_TEMP = 20


# ================================================
# Camera RGB
# ================================================
OPTICAL_CAM_ID = 0
OPTICAL_H = 480 
OPTICAL_W = 640 
OPTICAL_FAILED_CAPTURE_COUNTER_FOR_CRASH = 5

# PPL detection YOLO
OPTICAL_YOLO_WH = 320  # width/height for YOLO model input size
OPTICAL_YOLO_MODEL = "yolo11n.pt"  
OPTICAL_IS_PERSON_YOLO_THR = 0.5  # confidence threshold for person detection

# ================================================
# Camera TOF
# ================================================
# PH

# ================================================
# Stabilizer
# ================================================
STABILIZER_N_FRAMES = 50  # number of frames to consider
STABILIZER_M_FRAMES = 10  # number of frames to trigger action