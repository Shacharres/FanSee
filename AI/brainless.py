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

class BrainState:
    def __init__(self):
        import config
        self.current_target = None  # Target object or ID
        self.target_timestamp = None  # When started serving
        self.intended_time = 0  # How long to serve
        self.priority_bins = np.zeros(config.Num_of_bins)  # azimuth bins
        self.Num_of_bins = config.Num_of_bins
        self.target_dist_bin = config.target_dist_bin
        self.target_clustering_mins = config.target_clustering_mins
        self.serve_time = config.serve_time
        self.fullSwingTime = config.fullSwingTime

    def get_hot_factor(self, target):
        # Placeholder: get thermal factor from target, default to 1
        return getattr(target, 'thermalFactor', 1)

    def propagate_priority(self, targets):
        # Increase priority in bins for each target
        for target in targets:
            bin_idx = int(target.azimuth_bin)
            factor = self.get_hot_factor(target)
            self.priority_bins[max(0, min(self.Num_of_bins-1, bin_idx))] += 1 * factor

    def switch_target(self, targets):
        # Called periodically to track and switch targets
        now = time.time()
        current_bin = int(getattr(self.current_target, 'azimuth_bin', -1))
        time_served = now - self.target_timestamp if self.target_timestamp else 0
        bins_with_targets = [int(t.azimuth_bin) for t in targets]

        # Track target within target_dist_bin bins
        target_in_range = None
        for t in targets:
            if abs(int(t.azimuth_bin) - current_bin) <= self.target_dist_bin:
                target_in_range = t
                break

        # If timer finished or no target in range, switch to next visible bin cluster
        if (time_served > self.intended_time or target_in_range is None):
            # Only consider bins with visible targets
            visible_bins = set(bins_with_targets)
            # Find highest priority among visible bins
            visible_priorities = {b: self.priority_bins[b] for b in visible_bins}
            if visible_priorities:
                max_bin = max(visible_priorities, key=lambda b: visible_priorities[b])
                candidate_bins = range(max(0, max_bin-self.target_clustering_mins), min(self.Num_of_bins, max_bin+self.target_clustering_mins+1))
                # Select bin with highest priority among candidates that have visible targets
                candidate_bins = [b for b in candidate_bins if b in visible_bins]
                if candidate_bins:
                    selected_bin = max(candidate_bins, key=lambda b: self.priority_bins[b])
                    # Nullify priority in selected bin and neighbors
                    for b in range(max(0, selected_bin-self.target_clustering_mins), min(self.Num_of_bins, selected_bin+self.target_clustering_mins+1)):
                        self.priority_bins[b] = 0
                    # Set new target in selected bin
                    self.current_target = next((t for t in targets if int(t.azimuth_bin) == selected_bin), None)
                    self.target_timestamp = now
                    bin_distance = abs(selected_bin - current_bin)
                    transition_time = self.fullSwingTime * bin_distance / self.Num_of_bins
                    self.intended_time = self.serve_time + transition_time
        else:
            # Continue tracking target in range
            self.current_target = target_in_range

    def get_implement_config(self):
        # Return states for ImplementConfig (azimuth, etc.)
        if self.current_target:
            return {
                'targetAzimuth': getattr(self.current_target, 'azimuth', 0),
                # Add other states as needed
            }
        else:
            return {
                'targetAzimuth': 0
            }

# Example usage:
# brain = BrainState()
# brain.propagate_priority(targets)
# brain.switch_target(targets)
# config = brain.get_implement_config()