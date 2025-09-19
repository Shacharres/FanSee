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

import numpy as np
import time

# =========================
# Initialization
# =========================
def init_brain_state(config, d_state=None):
    """
    Initialize or append missing fields to the state dictionary.
    Existing entries in d_state are preserved.
    """
    if d_state is None:
        d_state = {}

    defaults = {
        'current_target': None,         # {'index': int, 'azimuth_bin': int}
        'target_timestamp': None,
        'intended_time': 0,
        'Num_of_bins': config.Num_of_bins,
        'priority_bins': np.zeros(config.Num_of_bins),
        'target_dist_bin': config.target_dist_bin,
        'target_clustering_mins': config.target_clustering_mins,
        'serve_time': config.serve_time,
        'fullSwingTime': config.fullSwingTime
    }

    for k, v in defaults.items():
        if k not in d_state:
            d_state[k] = v

    return d_state


# =========================
# Hot factor computation
# =========================
def get_hot_factors(max_temp_list, delta=1.0):
    """
    Compute thermal factor for each target in list.
    min temp => 1
    others => 1 + delta * (temp - min_temp)
    """
    if not max_temp_list:
        return []
    min_temp = min(max_temp_list)
    factors = [1 + delta * (t - min_temp) for t in max_temp_list]
    return factors

# =========================
# Propagate priority
# =========================
def propagate_priority(d_targets, d_state, delta=1.0):
    """
    Update priority_bins in d_state using d_targets.
    """
    centers = d_targets.get('centers', [])
    is_wave = d_targets.get('is_wave', [])
    max_temp = d_targets.get('max_temp', [])

    factors = get_hot_factors(max_temp, delta)

    for idx, az in enumerate(centers):
        bin_idx = int(az)
        wave_factor = 2.0 if is_wave[idx] else 1.0
        b_idx = max(0, min(d_state['Num_of_bins'] - 1, bin_idx))
        d_state['priority_bins'][b_idx] += factors[idx] * wave_factor

# =========================
# Switch target
# =========================
def switch_target(d_targets, d_state):
    """
    Decide which target to serve next.
    """
    now = time.time()
    centers = d_targets.get('centers', [])
    bins_with_targets = [int(az) for az in centers]

    current_target = d_state.get('current_target')
    current_bin = int(current_target['azimuth_bin']) if current_target else -1
    time_served = now - d_state.get('target_timestamp', now) if current_target else 0

    # Check if current target is still in range
    target_in_range_idx = None
    for idx, b in enumerate(bins_with_targets):
        if abs(b - current_bin) <= d_state['target_dist_bin']:
            target_in_range_idx = idx
            break

    # Decide if need to switch
    if time_served > d_state['intended_time'] or target_in_range_idx is None:
        visible_bins = set(bins_with_targets)
        visible_priorities = {b: d_state['priority_bins'][b] for b in visible_bins}
        if visible_priorities:
            max_bin = max(visible_priorities, key=lambda b: visible_priorities[b])
            candidate_bins = range(max(0, max_bin - d_state['target_clustering_mins']),
                                   min(d_state['Num_of_bins'], max_bin + d_state['target_clustering_mins'] + 1))
            candidate_bins = [b for b in candidate_bins if b in visible_bins]
            if candidate_bins:
                selected_bin = max(candidate_bins, key=lambda b: d_state['priority_bins'][b])
                # Clear priority around selected bin
                for b in range(max(0, selected_bin - d_state['target_clustering_mins']),
                               min(d_state['Num_of_bins'], selected_bin + d_state['target_clustering_mins'] + 1)):
                    d_state['priority_bins'][b] = 0
                # Assign new target
                new_idx = bins_with_targets.index(selected_bin)
                d_state['current_target'] = {'index': new_idx, 'azimuth_bin': selected_bin}
                d_state['target_timestamp'] = now
                bin_distance = abs(selected_bin - current_bin)
                transition_time = d_state['fullSwingTime'] * bin_distance / d_state['Num_of_bins']
                d_state['intended_time'] = d_state['serve_time'] + transition_time
    else:
        # Continue tracking current target
        d_state['current_target'] = {'index': target_in_range_idx, 'azimuth_bin': bins_with_targets[target_in_range_idx]}

# =========================
# Get implement commands
# =========================
def get_implement_commands(d_targets, d_state):
    """
    Return dict with x_pixel and fan_speed.
    """
    current_target = d_state.get('current_target')
    if current_target:
        idx = current_target['index']
        x_pixel = d_targets['centers'][idx]
        fan_speed = d_targets['max_temp'][idx] if 'max_temp' in d_targets else 1
        return {'x_pixel': x_pixel, 'fan_speed': fan_speed}
    else:
        return {'x_pixel': 0, 'fan_speed': 1}

# =========================
# Example usage
# =========================
# import config
# d_state = init_brain_state(config)
# d_targets = {
#     'boxes': [...],
#     'centers': [10, 25, 40],
#     'is_wave': [False, True, False],
#     'max_temp': [0.5, 1.2, 0.8]
# }
# propagate_priority(d_targets, d_state)
# switch_target(d_targets, d_state)
# commands = get_implement_commands(d_targets, d_state)
# print(commands)
