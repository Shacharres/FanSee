from gpiozero import Servo
from time import sleep

s = Servo(17)
s.min() # -40
# s.max() #35
# 50
# max 40
# min 30
s.pulse_width = 0.0016
s_borside = 0.0016

if __name__ == "__main__":
    print(s.pulse_width)
    while(True):
        pass
