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
        # Mask dead pixels (row 1, columns 8 and 16, i.e., [0,7] and [0,15])
        masked_frame = reshaped_frame.copy()
        masked_frame[0,7] = np.nan
        masked_frame[0,15] = np.nan
        # Compute min/max ignoring dead pixels
        temp_min = np.nanmin(masked_frame)
        min_pos = np.unravel_index(np.nanargmin(masked_frame), masked_frame.shape)

        # Find up to 3 max values with separation >= 5 pixels
        max_positions = []
        max_values = []
        temp_mask = masked_frame.copy()
        separation = 5
        for i in range(3):
            if np.all(np.isnan(temp_mask)):
                break
            max_val = np.nanmax(temp_mask)
            max_idx = np.nanargmax(temp_mask)
            max_pos = np.unravel_index(max_idx, temp_mask.shape)
            max_positions.append(max_pos)
            max_values.append(max_val)
            # Mask out a region around this max to enforce separation
            rr, cc = max_pos
            rmin = max(0, rr-separation)
            rmax = min(temp_mask.shape[0], rr+separation+1)
            cmin = max(0, cc-separation)
            cmax = min(temp_mask.shape[1], cc+separation+1)
            temp_mask[rmin:rmax, cmin:cmax] = np.nan
        plt.imshow(reshaped_frame, cmap='hot', interpolation='nearest')
        plt.colorbar()
        # Draw crosses for max values
        cross_colors = ['r', 'g', 'purple']
        for i, (pos, val) in enumerate(zip(max_positions, max_values)):
            plt.plot(pos[1], pos[0], color=cross_colors[i], marker='+', markersize=15, markeredgewidth=2)
            plt.text(pos[1]+1, pos[0]+1, f"{val:.2f}C", color=cross_colors[i], fontsize=10, weight='bold', va='bottom', ha='left')
        # Draw blue cross for min
        plt.plot(min_pos[1], min_pos[0], 'b+', markersize=15, markeredgewidth=2)
        plt.text(min_pos[1]+1, min_pos[0]+1, f"{temp_min:.2f}C", color='blue', fontsize=10, weight='bold', va='top', ha='left')
        # Show max and min values on the plot title
        max_str = '  '.join([f"Max{i+1}: {v:.2f}C" for i,v in enumerate(max_values)])
        plt.title(f"{max_str}  Min: {temp_min:.2f}C")
        plt.draw()
        plt.pause(0.01)
        plt.clf()    
    except ValueError:
        # these happen, no biggie - retry
        continue
