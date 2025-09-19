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

# Initialize relays for fan speeds and misting
relay_speed1 = OutputDevice(config.FAN_SPEED_1_PIN)
relay_speed2 = OutputDevice(config.FAN_SPEED_2_PIN)
relay_speed3 = OutputDevice(config.FAN_SPEED_3_PIN)
relay_mist = OutputDevice(config.FAN_MIST_PIN)
relay_speed1.on()
relay_speed2.on()
relay_speed3.on()
relay_mist.on()
# # servo 
servo = AngularServo(config.FAN_SERVO_PIN, min_angle=-90, max_angle=60)
servo.angle = 0


if __name__ == "__main__":
    relay_speed1.off()
    # relay_speed2.off()
    # relay_speed3.off()
    # relay_mist.off()
    while(True):
        pass


