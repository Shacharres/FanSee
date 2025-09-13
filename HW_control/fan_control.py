from gpiozero import OutputDevice, Servo, AngularServo
import config 

# Initialize relays for fan speeds and misting
relay_speed1 = OutputDevice(config.FAN_SPEED_1_PIN)
relay_speed2 = OutputDevice(config.FAN_SPEED_2_PIN)
relay_speed3 = OutputDevice(config.FAN_SPEED_3_PIN)
relay_mist = OutputDevice(config.FAN_MIST_PIN)

# servo 
servo = AngularServo(config.FAN_SERVO_PIN, min_angle=-60, max_angle=60)
