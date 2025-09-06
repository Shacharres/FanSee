from gpiozero import OutputDevice, Servo, AngularServo

relay_speed1 = OutputDevice(1)
relay_speed2 = OutputDevice(2)
relay_speed3 = OutputDevice(3)
relay_mist = OutputDevice(4)

# servo = Servo(17)
servo = AngularServo(17, min_angle=-60, max_angle=60)
