"""
Pins configuration file.
Thresholds and other constants.
"""

# ================================================
# Fan and fan servo 
# ================================================
FAN_SPEED_1_PIN = 24
FAN_SPEED_2_PIN = 23
FAN_SPEED_3_PIN = 22
FAN_MIST_PIN = 27
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
# Mode 1: 3280×2464 full FOV (still capture)
# Mode 2: 1920×1080 cropped FOV (video-friendly)
# Mode 3: 1640×1232 (binned, wide FOV)
OPTICAL_W = 1640
OPTICAL_H = 1232
OPTICAL_INIT_CAM_WARMUP = 2 
OPTICAL_FAILED_CAPTURE_COUNTER_FOR_CRASH = 5

# PPL detection YOLO
OPTICAL_YOLO_WH = 640  # width/height for YOLO model input size
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


# ================================================
# Brain Module Parameters
# ================================================
serve_time = 4
fullSwingTime = 1 # Full swing time for fan movement (seconds)
Num_of_bins = 100
target_dist_bin = 7
target_clustering_mins = 2