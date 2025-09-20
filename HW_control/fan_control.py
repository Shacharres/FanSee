# ============================================================
# bootstrap repo root before other imports
import subprocess, sys, os
from pathlib import Path

def add_git_root_to_path():
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL
        )
        git_root = Path(out.decode("utf-8").strip())
        sys.path.insert(0, str(git_root))
        return git_root
    except Exception:
        raise RuntimeError("Not inside a Git repository")

add_git_root_to_path()
# ============================================================

from gpiozero import OutputDevice, Servo
import config
from enum import Enum

class Speed(Enum):
    STOP = 1
    LOW = 2
    MIDDLE = 3
    HIGH = 4

# ================= CONSTS =================
SERVO_MAX_PULSE_LEFT = 0.0012
SERVO_MIN_PULSE_RIGHT = 0.0022
SERVO_PULSE_MID = 0.0016
PIXEL_OFFSET = config.OPTICAL_W/10
INTRP_RESULTION = 3280
INTRP_PIX_LIST = [60,1090,1940,3600]
INTRP_PWM_LIST = [2000,1800,1600,1400]


# ================= INITIALIZE HARDWARE =================
relay_speed1 = OutputDevice(config.FAN_SPEED_1_PIN)
relay_speed2 = OutputDevice(config.FAN_SPEED_2_PIN)
relay_speed3 = OutputDevice(config.FAN_SPEED_3_PIN)
relay_mist = OutputDevice(config.FAN_MIST_PIN)

# Set all relays off (normally closed when HIGH)
relay_speed1.on()
relay_speed2.on()
relay_speed3.on()
relay_mist.on()

servo = Servo(config.FAN_SERVO_PIN)

# ================= HELPER FUNCTIONS =================
def lerp(a, b, t):
    return a + (b - a) * t

def interpolate_three(x, x0, y0, x1, y1, x2, y2):
    """Piecewise linear interpolation through 3 points."""
    if x <= x1:
        t = (x - x0) / (x1 - x0)
        return lerp(y0, y1, t)
    else:
        t = (x - x1) / (x2 - x1)
        return lerp(y1, y2, t)

def set_servo_from_pixel(x_pixel):
    """Map pixel position to servo pulse using camera width from config."""
    x_min = 0
    x_max = config.OPTICAL_W
    x_mid = x_max / 2

    # Map x_pixel to normalized range [-1, 1]
    norm_val = interpolate_three(x_pixel, x_min, -1, x_mid, 0, x_max, 1)

    # Map normalized value to servo pulse
    servo_pulse_len = interpolate_three(
        norm_val,
        -0.9, SERVO_MIN_PULSE_RIGHT,
         0, SERVO_PULSE_MID,
         0.9, SERVO_MAX_PULSE_LEFT
    )
    servo.pulse_width = servo_pulse_len


def set_fan_speed(speed = None, relative_speed: int = None, state: dict = {}):
    if speed is None:  # want to change the current speed relatively
        speed = state.get('current_fan_speed', Speed.STOP)
        speed = Speed(min(max(speed.value + (relative_speed if relative_speed else 0), Speed.STOP.value), Speed.HIGH.value))
    
    if isinstance(speed, Speed):
        speed = speed.value

    relay_speed1.off() if speed > Speed.STOP.value else relay_speed1.on()
    relay_speed2.off() if speed > Speed.LOW.value else relay_speed2.on()
    relay_speed3.off() if speed > Speed.MIDDLE.value else relay_speed3.on()
    state['current_fan_speed'] = speed # store current speed in state for reference
    return state


def set_mist(mist_enable: bool):
    relay_mist.off() if mist_enable else relay_mist.on()

# ================= MAIN CONTROL FUNCTION =================
def apply_target_control(target: dict):
    """
    Apply hardware control based on target dictionary:
    {
        'x_pixel': int,
        'fan_speed': Speed,
        'prt_bin': int,        # optional, can be used for logging or extra logic
        'prt_temp': float,     # optional
        'mist_enable': bool
    }
    """
    x_pixel = target.get('x_pixel', config.OPTICAL_W / 2)
    fan_speed = target.get('fan_speed', Speed.STOP)
    mist_enable = target.get('mist_enable', False)

    print('x_pixel:', x_pixel)

    set_servo_from_pixel(x_pixel)
    set_fan_speed(fan_speed)
    set_mist(mist_enable)

    # Optional: log or use prt_bin/prt_temp for other actions
    prt_bin = target.get('prt_bin', None)
    prt_temp = target.get('prt_temp', None)
    # For example, could implement temperature-based fan override here
    # print(f"Bin: {prt_bin}, Temp: {prt_temp}")

# ================= TEST / MAIN LOOP =================
if __name__ == "__main__":
    # set_servo_from_pixel(config.OPTICAL_W)  # center
    set_servo_from_pixel(0)  # center
    set_fan_speed(Speed.LOW)
    set_mist(False)
    
    # Example usage
    target_example = {
        'x_pixel': 450,
        'fan_speed': Speed.MIDDLE,
        'prt_bin': 2,
        'prt_temp': 45.0,
        'mist_enable': True
    }

    # apply_target_control(target_example)
    print("Servo pulse:", servo.pulse_width)
    
    while True:
        pass
