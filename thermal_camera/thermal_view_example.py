import time
import board
import busio
import adafruit_mlx90640
import sys
# import keyboard 

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, '/home/fansee/Documents/FanSee')
import config
i2c = busio.I2C(board.SCL, board.SDA, frequency=800000)
# i2c0 = busio.I2C(board.SCL0, board.SDA0, frequency=800000)

mlx_55 = adafruit_mlx90640.MLX90640(i2c)
# mlx_110 = adafruit_mlx90640.MLX90640(i2c0)
print("MLX addr detected on I2C", [hex(i) for i in mlx_55.serial_number])


# if using higher refresh rates yields a 'too many retries' exception,
# try decreasing this value to work with certain pi/camera combinations
if config.THERMAL_FRAME_RATE == 2:
    mlx_55.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
elif config.THERMAL_FRAME_RATE == 4:
    mlx_55.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_4_HZ
elif config.THERMAL_FRAME_RATE == 8:
    mlx_55.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_8_HZ
else:
    raise ValueError("Unsupported frame rate for the thermal camera, try 2, 4, or 8")


plt.figure()
plt.ion()
frame = [0] * config.THERMAL_H * config.THERMAL_W
while True:
    # if keyboard.is_pressed('q'):
    #     print("You pressed 'q'. Thank you, goodbye!")
    #     break
    try:
        mlx_55.getFrame(frame)
        reshaped_frame = np.reshape(frame, (config.THERMAL_H, config.THERMAL_W))
        reshaped_frame[reshaped_frame < config.THERMAL_MIN_TEMP] = config.THERMAL_MIN_TEMP  # we honestly don't care about values lower than 20C

        plt.imshow(reshaped_frame, cmap='hot', interpolation='nearest')
        plt.colorbar()
        plt.draw()
        plt.pause(0.01)
        plt.clf()    
    except ValueError:
        # these happen, no biggie - retry
        continue
