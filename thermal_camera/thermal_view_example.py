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


plt.ion()
fig, axs = plt.subplots(2, 1, figsize=(8, 10))
plt.subplots_adjust(hspace=0.4)
max_history = []
history_len = 100
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
        # Update max value history
        if max_values:
            max_history.append(max_values[0])
        else:
            max_history.append(np.nan)
        if len(max_history) > history_len:
            max_history = max_history[-history_len:]

        axs[0].cla()
        axs[0].plot(max_history, color='red')
        axs[0].set_ylim([25, 35])
        axs[0].set_xlim([0, history_len-1])
        axs[0].set_title('Max Temperature Over Time')
        axs[0].set_xlabel('Frame')
        axs[0].set_ylabel('Temperature (C)')

        # Only create the imshow and colorbar once, then update data
        current_vmax = np.nanmax(masked_frame)
        if 'im' not in locals():
            axs[1].cla()
            im = axs[1].imshow(reshaped_frame, cmap='hot', interpolation='nearest', vmin=config.THERMAL_MIN_TEMP, vmax=current_vmax)
            cbar = fig.colorbar(im, ax=axs[1])
        else:
            im.set_data(reshaped_frame)
            im.set_clim(vmin=config.THERMAL_MIN_TEMP, vmax=current_vmax)
        # Remove previous cross/text artists if they exist
        if hasattr(axs[1], 'cross_artists'):
            for artist in axs[1].cross_artists:
                artist.remove()
        axs[1].cross_artists = []
        # Draw crosses for max values
        cross_colors = ['r', 'g', 'purple']
        for i, (pos, val) in enumerate(zip(max_positions, max_values)):
            cross = axs[1].plot(pos[1], pos[0], color=cross_colors[i], marker='+', markersize=15, markeredgewidth=2)[0]
            text = axs[1].text(pos[1]+1, pos[0]+1, f"{val:.2f}C", color=cross_colors[i], fontsize=10, weight='bold', va='bottom', ha='left')
            axs[1].cross_artists.extend([cross, text])
        # Draw blue cross for min
        cross_min = axs[1].plot(min_pos[1], min_pos[0], 'b+', markersize=15, markeredgewidth=2)[0]
        text_min = axs[1].text(min_pos[1]+1, min_pos[0]+1, f"{temp_min:.2f}C", color='blue', fontsize=10, weight='bold', va='top', ha='left')
        axs[1].cross_artists.extend([cross_min, text_min])
        # Show max and min values on the plot title
        max_str = '  '.join([f"Max{i+1}: {v:.2f}C" for i,v in enumerate(max_values)])
        axs[1].set_title(f"{max_str}  Min: {temp_min:.2f}C")

        plt.pause(0.01)
    except ValueError:
        # these happen, no biggie - retry
        continue
