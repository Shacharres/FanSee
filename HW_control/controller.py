import numpy as np
import RPi.GPIO as GPIO
import config


class ConfigControl:
    """
    Holds configuration data for hardware control, such as pin assignments and calibration arrays.
    """
    def __init__(self):
        # Pin assignments from config.py
        self.servo_pin = config.FAN_SERVO_PIN
        self.bobbles_pin = None  # Not defined in config.py, set to None or add to config.py
        self.mist_pin = config.FAN_MIST_PIN
        self.powerIO1 = config.FAN_SPEED_1_PIN
        self.powerIO2 = config.FAN_SPEED_2_PIN
        self.powerIO3 = config.FAN_SPEED_3_PIN
        # Azimuth and PWM calibration arrays
        self.azimuth = np.array([0, 90, 180])  # Example azimuth values
        self.PWM = np.array([1000, 1500, 2000])  # Example PWM values

def implementControl(targetAzimuth: float, fanPower: int, bobbles: bool, mist: bool, config: ConfigControl) -> None:
    """
    Sets hardware outputs based on input parameters.
    Args:
        targetAzimuth (float): Desired azimuth for servo (degrees or units).
        fanPower (int): Requested fan power level (1-3).
        bobbles (bool): Whether bobbles are on.
        mist (bool): Whether mist is on.
        config (ConfigControl): Pin configuration.
    Returns:
        None
    Effects:
        1. Set PWM for servoPin as function of targetAzimuth using np.interp
        2. Set bobbles pin high/low as requested
        3. Set mist pin high/low as requested
        4. Toggle powerIO1, powerIO2, powerIO3 based on fanPower
    """
    # Setup GPIO (should be called once in main code, shown here for completeness)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(config.servo_pin, GPIO.OUT)
    GPIO.setup(config.bobbles_pin, GPIO.OUT)
    GPIO.setup(config.mist_pin, GPIO.OUT)
    GPIO.setup(config.powerIO1, GPIO.OUT)
    GPIO.setup(config.powerIO2, GPIO.OUT)
    GPIO.setup(config.powerIO3, GPIO.OUT)

    # 1. Set PWM for servoPin using np.interp
    pwm_value = np.interp(targetAzimuth, config.azimuth, config.PWM)
    servo_pwm = GPIO.PWM(config.servo_pin, 50)  # 50Hz typical for servos
    servo_pwm.start(0)
    duty_cycle = pwm_value / 20000 * 100  # Example conversion, adjust for your servo
    servo_pwm.ChangeDutyCycle(duty_cycle)

    # 2. Set bobbles pin
    GPIO.output(config.bobbles_pin, GPIO.HIGH if bobbles else GPIO.LOW)

    # 3. Set mist pin
    GPIO.output(config.mist_pin, GPIO.HIGH if mist else GPIO.LOW)

    # 4. Toggle powerIO pins based on fanPower
    for i in range(1, 4):
        pin = getattr(config, f"powerIO{i}")
        state = GPIO.HIGH if i <= fanPower else GPIO.LOW
        GPIO.output(pin, state)