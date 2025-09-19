
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

from gpiozero import OutputDevice, Servo, AngularServo
import config 

from enum import Enum

class Speed(Enum):
    STOP = 1
    LOW = 2
    MIDDLE = 3
    HIGH = 4




#CONSTS
SERVO_MIDDLE = 40



# Initialize relays for fan speeds and misting
relay_speed1 = OutputDevice(config.FAN_SPEED_1_PIN)
relay_speed2 = OutputDevice(config.FAN_SPEED_2_PIN)
relay_speed3 = OutputDevice(config.FAN_SPEED_3_PIN)
relay_mist = OutputDevice(config.FAN_MIST_PIN)
# set all rellays off (normaly close when  high)
relay_speed1.on()
relay_speed2.on()
relay_speed3.on()
relay_mist.on()

# Initialize servo 
servo = AngularServo(config.FAN_SERVO_PIN, min_angle=-180, max_angle=180) #servo has off set
servo.angle = 0

def set_mist(mist_enable):
    if mist_enable:
        relay_mist.off()
    else:
        relay_mist.on()

def set_servo_angle(angle):
    servo.angle = angle

def set_fan_speed(speed):
    if speed.value > Speed.STOP.value:
        relay_speed1.off()
    else:
        relay_speed1.on()
    if speed.value > Speed.LOW.value:
        relay_speed2.off()
    else:
        relay_speed2.on()
    if speed.value > Speed.MIDDLE.value:
        relay_speed3.off()
    else:
        relay_speed3.on()


if __name__ == "__main__":
    
    # relay_mist.off()
    set_servo_angle(SERVO_MIDDLE+40)
    set_fan_speed(Speed.STOP)
    print(servo.angle)
    while(True):
        pass


