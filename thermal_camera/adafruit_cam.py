import board
import busio
import adafruit_mlx90640
import numpy as np


THERMAL_H, THERMAL_W = 24, 32  # fixed for MLX90640
DEFAULT_TEMP = 28.0  # default temp if reading fails


def init_thermal_camera(frame_rate, frame_size=(24,32)):
    """Initializes the thermal camera."""
    i2c = busio.I2C(board.SCL, board.SDA, frequency=800000)

    mlx_55 = adafruit_mlx90640.MLX90640(i2c)
    print("MLX addr detected on I2C", [hex(i) for i in mlx_55.serial_number])

    if frame_size:
        global THERMAL_H, THERMAL_W
        THERMAL_H, THERMAL_W = frame_size
    
    # if using higher refresh rates yields a 'too many retries' exception,
    # try decreasing this value to work with certain pi/camera combinations
    if frame_rate == 2:
        mlx_55.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
    elif frame_rate == 4:
        mlx_55.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_4_HZ
    elif frame_rate == 8:
        mlx_55.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_8_HZ
    else:
        raise ValueError("Unsupported frame rate for the thermal camera, try 2, 4, or 8")
    return mlx_55


def convert_optical_to_thermal_box(optical_box, optical_frame_size=(640, 480)) -> list[int]:
    """Converts bounding box from optical camera coordinates to thermal camera coordinates."""
    ox_w, ox_h = optical_frame_size
    x1, y1, x2, y2 = optical_box
    x1_th = int(x1 / ox_w * THERMAL_W)
    y1_th = int(y1 / ox_h * THERMAL_H)
    x2_th = int(x2 / ox_w * THERMAL_W)
    y2_th = int(y2 / ox_h * THERMAL_H)
    # ensure box is within bounds
    x1_th = max(0, min(THERMAL_W - 1, x1_th))
    y1_th = max(0, min(THERMAL_H - 1, y1_th))
    x2_th = max(0, min(THERMAL_W - 1, x2_th))
    y2_th = max(0, min(THERMAL_H - 1, y2_th))
    return [x1_th, y1_th, x2_th, y2_th]


def get_max_temp(cam, optical_box, optical_frame_size, retries: int = 5) -> float:
    frame = [0] * THERMAL_H * THERMAL_W
    while retries > 0 and not np.any(frame):
        try:
            cam.getFrame(frame)
        except ValueError:
            retries -= 1
            continue

    if not np.any(frame):
        print("Warning: failed to get frame from thermal camera")
        return DEFAULT_TEMP
    
    x1, y1, x2, y2 = convert_optical_to_thermal_box(optical_box, optical_frame_size)
    region = np.reshape(frame, (THERMAL_H, THERMAL_W))[y1:y2, x1:x2]
    return np.max(region)
